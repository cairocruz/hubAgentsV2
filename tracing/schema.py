"""
tracing/schema.py — SQL para criar a tabela de tracing e views de análise.

Este módulo contém apenas strings SQL. Nenhuma dependência de runtime.
O SQL deve ser executado no SQL Editor do Supabase antes de usar o tracing.

Tabela:
  - agent_trace_events : cada linha é um evento (step ou task) capturado
    durante a execução de um agente.

Views:
  - vw_trace_timeline        : timeline ordenada de todos os eventos por análise
  - vw_trace_agent_summary   : resumo agregado por agente (total de steps, tokens, duração)
  - vw_trace_analysis_overview: visão geral por análise (total de agentes, steps, tokens, tempo)
"""

# ===========================================================================
# SQL para criar a tabela de eventos de tracing
# ===========================================================================
TRACING_TABLE_SQL = """
-- =====================================================
-- Tabela: agent_trace_events
-- Armazena cada evento (step/task) da execução dos agentes.
-- =====================================================
CREATE TABLE IF NOT EXISTS agent_trace_events (
    id              UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    
    -- Vínculo com a análise (mesmo UUID usado em agent_logs)
    analysis_id     TEXT NOT NULL,
    
    -- Identificação do agente
    agent_role      TEXT NOT NULL,          -- Ex: "Especialista 1 (Rotina...)"
    agent_id        INT,                    -- 1-5 para especialistas, NULL para supervisor/sintetizador
    
    -- Tipo do evento
    event_type      TEXT NOT NULL,          -- 'step_action' | 'step_finish' | 'task_complete'
    
    -- Conteúdo do evento
    thought         TEXT,                   -- Pensamento do agente antes de agir
    tool_name       TEXT,                   -- Nome da tool usada (NULL se não usou)
    tool_input      TEXT,                   -- Input enviado à tool
    tool_result     TEXT,                   -- Resultado da tool
    output          TEXT,                   -- Output final (para step_finish e task_complete)
    
    -- Métricas
    token_count     INT,                    -- Tokens estimados (se disponível)
    duration_ms     FLOAT,                  -- Duração em milissegundos
    
    -- Metadados
    step_number     INT DEFAULT 0,          -- Número sequencial do step dentro da análise
    phase           TEXT,                   -- 'phase1' | 'phase2' | 'phase3'
    iteration       INT DEFAULT 1,          -- Iteração do loop de retrabalho (1 = primeira vez)
    
    -- Timestamp automático
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para consultas frequentes
CREATE INDEX IF NOT EXISTS idx_trace_analysis_id ON agent_trace_events(analysis_id);
CREATE INDEX IF NOT EXISTS idx_trace_agent_role ON agent_trace_events(agent_role);
CREATE INDEX IF NOT EXISTS idx_trace_event_type ON agent_trace_events(event_type);
CREATE INDEX IF NOT EXISTS idx_trace_phase ON agent_trace_events(phase);
"""

# ===========================================================================
# SQL para criar views de análise humana
# ===========================================================================
TRACING_VIEWS_SQL = """
-- =====================================================
-- View 1: Timeline completa de eventos por análise
-- Uso: SELECT * FROM vw_trace_timeline WHERE analysis_id = 'xxx';
-- =====================================================
CREATE OR REPLACE VIEW vw_trace_timeline AS
SELECT
    analysis_id,
    step_number,
    phase,
    iteration,
    agent_role,
    agent_id,
    event_type,
    -- Resumo curto do que aconteceu
    CASE
        WHEN event_type = 'step_action' THEN 'Tool: ' || COALESCE(tool_name, '?')
        WHEN event_type = 'step_finish' THEN 'Resposta final do agente'
        WHEN event_type = 'task_complete' THEN 'Tarefa concluída'
        ELSE event_type
    END AS event_summary,
    thought,
    tool_name,
    tool_input,
    LEFT(tool_result, 500) AS tool_result_preview,    -- Trunca para não poluir
    LEFT(output, 500) AS output_preview,
    duration_ms,
    token_count,
    created_at
FROM agent_trace_events
ORDER BY analysis_id, step_number, created_at;


-- =====================================================
-- View 2: Resumo agregado por agente dentro de uma análise
-- Uso: SELECT * FROM vw_trace_agent_summary WHERE analysis_id = 'xxx';
-- =====================================================
CREATE OR REPLACE VIEW vw_trace_agent_summary AS
SELECT
    analysis_id,
    agent_role,
    agent_id,
    phase,
    
    -- Métricas de execução
    COUNT(*) FILTER (WHERE event_type = 'step_action')  AS total_steps,
    COUNT(*) FILTER (WHERE event_type = 'step_finish')  AS total_finishes,
    COUNT(*) FILTER (WHERE tool_name IS NOT NULL)        AS tool_calls,
    
    -- Tokens e tempo
    SUM(COALESCE(token_count, 0))  AS total_tokens,
    SUM(COALESCE(duration_ms, 0))  AS total_duration_ms,
    
    -- Timestamps
    MIN(created_at) AS started_at,
    MAX(created_at) AS finished_at,
    
    -- Extrair duração real em segundos
    EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at))) AS wall_time_seconds
    
FROM agent_trace_events
GROUP BY analysis_id, agent_role, agent_id, phase
ORDER BY analysis_id, MIN(created_at);


-- =====================================================
-- View 3: Visão geral por análise (dashboard)
-- Uso: SELECT * FROM vw_trace_analysis_overview ORDER BY created_at DESC;
-- =====================================================
CREATE OR REPLACE VIEW vw_trace_analysis_overview AS
SELECT
    analysis_id,
    
    -- Contadores
    COUNT(DISTINCT agent_role)   AS total_agents,
    COUNT(*)                     AS total_events,
    COUNT(*) FILTER (WHERE event_type = 'step_action')  AS total_steps,
    COUNT(*) FILTER (WHERE tool_name IS NOT NULL)        AS total_tool_calls,
    COUNT(*) FILTER (WHERE event_type = 'task_complete') AS total_tasks_completed,
    
    -- Tokens e tempo
    SUM(COALESCE(token_count, 0))  AS total_tokens,
    SUM(COALESCE(duration_ms, 0))  AS total_duration_ms,
    
    -- Janela temporal
    MIN(created_at) AS analysis_started,
    MAX(created_at) AS analysis_finished,
    EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at))) AS total_wall_time_seconds,
    
    -- Fases alcançadas
    ARRAY_AGG(DISTINCT phase) FILTER (WHERE phase IS NOT NULL) AS phases_executed
    
FROM agent_trace_events
GROUP BY analysis_id
ORDER BY MIN(created_at) DESC;
"""

# ===========================================================================
# SQL combinado (prático para executar de uma vez)
# ===========================================================================
TRACING_SQL = TRACING_TABLE_SQL + "\n\n" + TRACING_VIEWS_SQL

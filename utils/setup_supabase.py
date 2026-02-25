"""
utils/setup_supabase.py — Script de configuração inicial do banco Supabase.

Este módulo é executado UMA VEZ para preparar o ambiente de banco de dados:

  1. Exibe o SQL necessário para criar as tabelas e funções no Supabase
     (deve ser executado manualmente no SQL Editor do painel Supabase).
  2. Lê os 5 arquivos CSV de dados históricos (data/dataset_1..5.csv).
  3. Gera embeddings de 384 dimensões para cada frase usando SentenceTransformer.
  4. Faz upload em lotes (batch de 50) para a tabela `agent_examples`.

Tabelas criadas pelo SQL:
  - agent_examples        : dados históricos com embeddings (RAG)
  - agent_logs            : log final do sintetizador
  - agent_individual_logs : log individual por especialista
  - agent_rework_history  : histórico de retrabalhos (análises reprovadas)
  - agent_trace_events    : eventos de tracing de execução dos agentes

Views criadas pelo SQL (tracing):
  - vw_trace_timeline         : timeline completa de eventos por análise
  - vw_trace_agent_summary    : resumo agregado por agente
  - vw_trace_analysis_overview: visão geral por análise (dashboard)

Requisitos:
  - Variáveis SUPABASE_URL e SUPABASE_KEY no .env
  - Extensões pgvector e uuid-ossp habilitadas no Supabase

Uso:
  python -m utils.setup_supabase
"""
import os
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega variáveis de ambiente (.env)
load_dotenv()

# ---------------------------------------------------------------------------
# Conexão com o Supabase (necessária para o upload dos dados)
# ---------------------------------------------------------------------------
url: str = os.getenv("SUPABASE_URL", "")
key: str = os.getenv("SUPABASE_KEY", "")

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

supabase: Client = create_client(url, key)

# Modelo de embedding multilingual para gerar vetores das frases em português
print("📥 Carregando modelo SentenceTransformer...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')


def create_database_schema():
    """
    Exibe o SQL completo para criar o schema do banco de dados no Supabase.

    O Supabase não permite criar tabelas/extensões via API REST padrão
    com roles 'anon' ou 'service_role', então o SQL deve ser copiado e
    executado manualmente no SQL Editor do painel do Supabase.

    O schema inclui:
      - Extensões: pgvector (vetores) e uuid-ossp (UUIDs)
      - Tabela agent_examples: dados históricos com embeddings para RAG
      - Tabela agent_logs: log final do sintetizador
      - Tabela agent_individual_logs: log individual por especialista
      - Tabela agent_rework_history: histórico de análises reprovadas
      - Índices para busca rápida por analysis_id
      - Função RPC match_responses: busca vetorial por similaridade
    """
    sql = """
    -- Executar no painel do Supabase -> SQL Editor

    -- 0. Extensões necessárias
    create extension if not exists vector;
    create extension if not exists "uuid-ossp";  -- para uuid_generate_v4()

    -- 1. Tabela para os exemplos (Few-Shot/RAG)
    create table if not exists agent_examples (
      id bigserial primary key,
      agent_id integer not null,
      frase text not null,
      risco text not null,
      fator text,
      taxonomia text,
      metadata text,
      embedding vector(384)
    );

    -- 2. Tabela de log FINAL (Sintetizador) – agora com analysis_id
    create table if not exists agent_logs (
      id bigserial primary key,
      analysis_id uuid not null default uuid_generate_v4(),
      agent_role text not null,
      quest text,
      user_response text not null,
      analysis_result text not null,
      metadata jsonb,
      created_at timestamptz default now()
    );

    -- 3. Tabela de log INDIVIDUAL de cada especialista
    create table if not exists agent_individual_logs (
      id bigserial primary key,
      analysis_id uuid not null,            -- FK lógica para agent_logs.analysis_id
      agent_id integer not null,            -- 1-5
      agent_domain text not null,           -- nome da dimensão
      question text,                        -- pergunta feita à usuária
      user_response text not null,          -- resposta da usuária
      score_risco integer,                  -- 0-100
      justificativa text,                   -- justificativa do agente
      rag_results text,                     -- o que a busca de casos similares retornou
      raw_output text,                      -- saída bruta completa do agente
      rework_count integer default 0,       -- quantas vezes foi retrabalhado
      supervisor_status text,               -- APROVADO / REPROVADO
      supervisor_feedback text,             -- feedback do supervisor
      metadata jsonb,
      created_at timestamptz default now()
    );

    -- 4. Tabela de histórico de retrabalho
    create table if not exists agent_rework_history (
      id bigserial primary key,
      analysis_id uuid not null,            -- FK lógica para agent_logs.analysis_id
      agent_id integer not null,            -- 1-5
      agent_domain text not null,           -- nome da dimensão
      iteration integer not null default 1, -- rodada de revisão (1, 2, ...)
      original_score_risco integer,         -- score da análise reprovada
      original_justificativa text,          -- justificativa da análise reprovada
      original_raw_output text,             -- saída bruta completa que foi reprovada
      supervisor_feedback text not null,    -- motivo da reprovação pelo supervisor
      created_at timestamptz default now()
    );

    -- 5. Índice para buscar logs individuais por analysis_id
    create index if not exists idx_individual_logs_analysis_id
      on agent_individual_logs (analysis_id);

    -- 6. Índice para buscar logs finais por analysis_id
    create index if not exists idx_agent_logs_analysis_id
      on agent_logs (analysis_id);

    -- 7. Índice para buscar histórico de retrabalho por analysis_id
    create index if not exists idx_rework_history_analysis_id
      on agent_rework_history (analysis_id);

    -- 8. Função RPC para buscar vetores similares
    -- Esta função é chamada pelo SupabaseDB.find_similar_responses()
    -- via supabase.rpc('match_responses', params). Recebe o embedding
    -- da query, filtra opcionalmente por agent_id, e retorna os N
    -- registros mais similares acima do threshold.
    create or replace function match_responses (
      query_embedding vector(384),
      filter_agent_id int,
      match_threshold float,
      match_count int
    )
    returns table (
      id bigint,
      frase text,
      risco text,
      fator text,
      taxonomia text,
      metadata text,
      similarity float
    )
    language sql stable
    as $$
      select
        agent_examples.id,
        agent_examples.frase,
        agent_examples.risco,
        agent_examples.fator,
        agent_examples.taxonomia,
        agent_examples.metadata,
        1 - (agent_examples.embedding <=> query_embedding) as similarity
      from agent_examples
      where (filter_agent_id is null or agent_id = filter_agent_id)
        and 1 - (agent_examples.embedding <=> query_embedding) > match_threshold
      order by agent_examples.embedding <=> query_embedding
      limit match_count;
    $$;
    """

    # Importar o SQL de tracing (tabela + views) do módulo separado
    from tracing.schema import TRACING_SQL

    print("\n⚠️ IMPORTANTE: Execute o seguinte SQL no 'SQL Editor' do seu projeto Supabase antes de continuar:\n")
    print(sql)
    print("\n-- =====================================================")
    print("-- SQL DE TRACING (tabela agent_trace_events + views)")
    print("-- =====================================================")
    print(TRACING_SQL)
    # Pausa para o usuário executar o SQL manualmente antes de continuar
    input("\nPressione [Enter] após criar as tabelas para iniciar o upload dos dados...")


import csv


def process_and_upload_dataset(file_path: str, agent_id: int):
    """
    Lê um CSV de dados históricos, gera embeddings e envia para o Supabase.

    Cada CSV contém frases rotuladas para uma dimensão específica de risco.
    O processo:
      1. Lê todas as linhas do CSV (colunas: frase, risco, fator, taxonomia, metadata)
      2. Divide em lotes de 50 registros
      3. Gera embeddings (384 dims) para cada frase do lote
      4. Insere o lote na tabela agent_examples do Supabase

    Args:
        file_path: Caminho absoluto para o arquivo CSV.
        agent_id:  ID do agente/dimensão (1-5) ao qual os dados pertencem.
    """
    print(f"\n⚙️ Processando dataset__{agent_id} ({file_path})...")
    
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        return
        
    records = []
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Preencher NaNs com vazio
            for key in row:
                if row[key] is None:
                    row[key] = ""
            records.append(row)
            
    total = len(records)
    
    batch_size = 50
    for i in range(0, total, batch_size):
        batch = records[i:i+batch_size]
        
        # Gerar os embeddings para a coluna 'frase'
        frases = [r.get('frase', '') for r in batch]
        embeddings = model.encode(frases).tolist() # Converte array numpy para list
        
        supabase_data = []
        for j, record in enumerate(batch):
            supabase_data.append({
                "agent_id": agent_id,
                "frase": record.get("frase", ""),
                "risco": record.get("risco", ""),
                "fator": record.get("fator", ""),
                "taxonomia": record.get("taxonomia", ""),
                "metadata": record.get("metadata", ""),
                "embedding": embeddings[j]
            })
            
        # Inserir no Supabase
        try:
            response = supabase.table("agent_examples").insert(supabase_data).execute()
            print(f"✅ Inseridos {len(response.data)} registros (Lote {i//batch_size + 1})")
        except Exception as e:
            print(f"❌ Erro ao inserir lote {i//batch_size + 1}: {e}")

def main():
    """
    Função principal do script de migração.

    Fluxo:
      1. Exibe o SQL para o usuário executar no Supabase
      2. Aguarda confirmação (Enter)
      3. Processa cada um dos 5 CSVs (dataset_1.csv a dataset_5.csv)
      4. Para cada CSV, gera embeddings e faz upload para agent_examples
    """
    print("\ud83d\ude80 Iniciando migra\u00e7\u00e3o de dados locais para Supabase PgVector...")
    
    # Passo 1: Mostrar o SQL e aguardar cria\u00e7\u00e3o das tabelas
    create_database_schema()
    
    # Passo 2: Processar cada dataset (1 por dimens\u00e3o de risco)
    # Os CSVs ficam em data/ na raiz do projeto
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    for i in range(1, 6):
        file_path = os.path.join(data_dir, f"dataset_{i}.csv")
        process_and_upload_dataset(file_path, i)
        
    print("\n✅ Migração concluída!")

if __name__ == "__main__":
    main()

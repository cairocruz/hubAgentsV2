"""
tracing/service.py — Serviço de persistência de eventos de trace no Supabase.

Classe TracingService: responsável EXCLUSIVAMENTE por gravar eventos
na tabela agent_trace_events. Não conhece nada sobre agentes, tasks,
ou CrewAI — recebe apenas dados primitivos (strings, ints, floats).

Usa a mesma estratégia de lazy initialization do supabase_client.py
para não bloquear imports.
"""

import os
import time
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Cliente Supabase lazy (independente do utils/supabase_client.py)
# ---------------------------------------------------------------------------
# O tracing tem seu próprio cliente para manter 100% de desacoplamento.
# Se o Supabase não estiver configurado, os logs são silenciosamente ignorados.

_trace_client = None
_trace_initialized = False


def _get_trace_client():
    """
    Retorna o cliente Supabase para tracing (lazy singleton).

    Cria o cliente apenas na primeira chamada. Se SUPABASE_URL ou
    SUPABASE_KEY não estiverem no .env, retorna None e todos os
    logs de trace serão silenciosamente descartados.
    """
    global _trace_client, _trace_initialized
    if _trace_initialized:
        return _trace_client
    _trace_initialized = True

    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if url and key:
        try:
            from supabase import create_client
            _trace_client = create_client(url, key)
        except Exception as e:
            print(f"⚠️  Tracing: não foi possível conectar ao Supabase: {e}")
    return _trace_client


class TracingService:
    """
    Serviço de persistência de eventos de tracing.

    Responsabilidades:
      - Receber dados brutos de um evento (step ou task).
      - Inserir na tabela agent_trace_events do Supabase.
      - Manter um contador sequencial de steps por análise.
      - Ser thread-safe (cada análise cria sua instância).

    Não possui dependência alguma com CrewAI, agents, ou qualquer outro
    módulo do projeto. Recebe apenas tipos primitivos.
    """

    def __init__(self, analysis_id: str, phase: str = "phase1", iteration: int = 1):
        """
        Inicializa o serviço de tracing para uma análise específica.

        Args:
            analysis_id: UUID da análise (mesmo usado em agent_logs).
            phase: fase atual ('phase1', 'phase2', 'phase3').
            iteration: iteração do loop de retrabalho (1 = primeira vez).
        """
        self.analysis_id = analysis_id
        self.phase = phase
        self.iteration = iteration
        self._step_counter = 0  # Contador sequencial de steps

    def set_phase(self, phase: str, iteration: int = 1):
        """
        Atualiza a fase e iteração atuais (chamado entre fases).

        Args:
            phase: nova fase ('phase1', 'phase2', 'phase3').
            iteration: novo valor de iteração.
        """
        self.phase = phase
        self.iteration = iteration

    def log_event(
        self,
        agent_role: str,
        event_type: str,
        *,
        agent_id: Optional[int] = None,
        thought: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_input: Optional[str] = None,
        tool_result: Optional[str] = None,
        output: Optional[str] = None,
        token_count: Optional[int] = None,
        duration_ms: Optional[float] = None,
    ) -> None:
        """
        Grava um evento de trace na tabela agent_trace_events.

        Se o Supabase não estiver disponível, o evento é silenciosamente
        descartado (sem impacto na execução dos agentes).

        Args:
            agent_role:  papel do agente (ex: "Especialista 1 (Rotina...)")
            event_type:  tipo do evento ('step_action'|'step_finish'|'task_complete')
            agent_id:    ID numérico do agente (1-5) ou None
            thought:     pensamento do agente antes de agir
            tool_name:   nome da tool chamada (se aplicável)
            tool_input:  input passado à tool
            tool_result: resultado retornado pela tool
            output:      output final do step/task
            token_count: tokens estimados
            duration_ms: duração em milissegundos
        """
        client = _get_trace_client()
        if client is None:
            return  # Supabase não configurado — ignora silenciosamente

        self._step_counter += 1

        # Monta o registro para inserção
        record = {
            "analysis_id": self.analysis_id,
            "agent_role": agent_role,
            "agent_id": agent_id,
            "event_type": event_type,
            "thought": _truncate(thought, 5000),
            "tool_name": tool_name,
            "tool_input": _truncate(tool_input, 5000),
            "tool_result": _truncate(tool_result, 10000),
            "output": _truncate(output, 10000),
            "token_count": token_count,
            "duration_ms": duration_ms,
            "step_number": self._step_counter,
            "phase": self.phase,
            "iteration": self.iteration,
        }

        try:
            client.table("agent_trace_events").insert(record).execute()
        except Exception as e:
            # Falha no tracing NUNCA deve interromper a execução dos agentes
            print(f"⚠️  Tracing: erro ao gravar evento: {e}")


def _truncate(text: Optional[str], max_len: int) -> Optional[str]:
    """Trunca uma string para evitar exceder limites de coluna no banco."""
    if text is None:
        return None
    if len(text) > max_len:
        return text[:max_len] + "…[truncado]"
    return text

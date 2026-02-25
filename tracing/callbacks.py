"""
tracing/callbacks.py — Factories de callbacks para injeção no CrewAI.

Este módulo é a ÚNICA ponte entre o pacote tracing/ e o CrewAI.
Exporta duas factory functions que criam callbacks compatíveis com:

  - Agent.step_callback  : recebe AgentAction | AgentFinish a cada step
  - Crew.task_callback   : recebe TaskOutput ao final de cada task

As factories recebem apenas o TracingService (que é agnóstico ao CrewAI)
e retornam funções prontas para serem passadas aos construtores do CrewAI.

Isso permite que o código em agents/ faça APENAS:
    step_cb = create_step_callback(tracing_svc, "Especialista 1", agent_id=1)
    agent = Agent(..., step_callback=step_cb)

Sem nunca importar nada do pacote tracing/ dentro da lógica de negócio.
"""

import time
from typing import Optional, Callable, Any
from .service import TracingService


def create_step_callback(
    tracing_service: TracingService,
    agent_role: str,
    agent_id: Optional[int] = None,
) -> Callable[[Any], None]:
    """
    Cria um step_callback compatível com o CrewAI Agent.

    O callback criado é chamado automaticamente pelo CrewAI a cada step
    do agente (cada chamada ao LLM, cada uso de tool, cada resposta final).

    Ele distingue dois tipos de evento:
      - AgentAction (step_action): o agente decidiu usar uma tool
        → grava thought, tool_name, tool_input, tool_result
      - AgentFinish (step_finish): o agente emitiu sua resposta final
        → grava thought e output

    Args:
        tracing_service: instância do TracingService já vinculada a um analysis_id.
        agent_role: nome/papel do agente (ex: "Especialista 3 (Redes de Apoio...)").
        agent_id: ID numérico (1-5) ou None para supervisor/sintetizador.

    Returns:
        Callable que pode ser passada diretamente como step_callback= no Agent.
    """
    # Marca o tempo do último step para calcular duração entre steps
    last_step_time = {"t": time.time()}

    def _callback(step_output: Any) -> None:
        """
        Callback executado pelo CrewAI a cada step do agente.

        Recebe um objeto AgentAction ou AgentFinish (dataclass do CrewAI).
        """
        now = time.time()
        duration_ms = (now - last_step_time["t"]) * 1000
        last_step_time["t"] = now

        # AgentAction: o agente chamou uma tool
        if hasattr(step_output, "tool"):
            tracing_service.log_event(
                agent_role=agent_role,
                event_type="step_action",
                agent_id=agent_id,
                thought=getattr(step_output, "thought", None),
                tool_name=getattr(step_output, "tool", None),
                tool_input=str(getattr(step_output, "tool_input", "")),
                tool_result=str(getattr(step_output, "result", "")),
                duration_ms=round(duration_ms, 2),
            )
        # AgentFinish: o agente emitiu resposta final
        elif hasattr(step_output, "output"):
            output = getattr(step_output, "output", "")
            # output pode ser string ou objeto — converte para string
            if not isinstance(output, str):
                output = str(output)
            tracing_service.log_event(
                agent_role=agent_role,
                event_type="step_finish",
                agent_id=agent_id,
                thought=getattr(step_output, "thought", None),
                output=output,
                duration_ms=round(duration_ms, 2),
            )

    return _callback


def create_task_callback(
    tracing_service: TracingService,
) -> Callable[[Any], None]:
    """
    Cria um task_callback compatível com o CrewAI Crew.

    O callback criado é chamado automaticamente ao final de cada Task,
    gravando o output completo da tarefa e o agente responsável.

    Args:
        tracing_service: instância do TracingService já vinculada a um analysis_id.

    Returns:
        Callable que pode ser passada diretamente como task_callback= no Crew.
    """

    def _callback(task_output: Any) -> None:
        """
        Callback executado pelo CrewAI ao concluir cada Task.

        Recebe um TaskOutput com campos: raw, agent, description, summary, etc.
        """
        agent_name = getattr(task_output, "agent", "Desconhecido") or "Desconhecido"
        raw = getattr(task_output, "raw", "")
        summary = getattr(task_output, "summary", "")
        description = getattr(task_output, "description", "")

        tracing_service.log_event(
            agent_role=str(agent_name),
            event_type="task_complete",
            output=raw or summary,
            thought=f"Task: {description[:200]}" if description else None,
        )

    return _callback

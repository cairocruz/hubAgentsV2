"""
agents/risk_analysis_crew.py — Orquestrador multiagente com CrewAI.

Este é o módulo central do sistema. Ele define e coordena 7 agentes de IA:
  - 5 Especialistas (um por dimensão de risco)
  - 1 Supervisor de Qualidade
  - 1 Sintetizador Final

O fluxo é dividido em 3 fases:

  ┌─────────────────────────────────────────────────────┐
  │  FASE 1 – 5 Especialistas analisam em sequência     │
  │           (cada um usa RAG para buscar casos         │
  │           similares no Supabase antes de avaliar)    │
  ├─────────────────────────────────────────────────────┤
  │  FASE 2 – Supervisor revisa cada análise:            │
  │           • APROVADO → segue adiante                 │
  │           • REPROVADO → especialista refaz (loop     │
  │             de até MAX_REWORK_ITERATIONS vezes)      │
  │           Cada retrabalho é salvo no banco            │
  ├─────────────────────────────────────────────────────┤
  │  FASE 3 – Sintetizador consolida todas as análises   │
  │           aprovadas em um relatório final com         │
  │           risk_score, risk_level e recomendações      │
  └─────────────────────────────────────────────────────┘

Dependências externas:
  - crewai: framework de orquestração de agentes
  - config.llm_config: determina qual provedor/modelo LLM usar
  - prompts.system_prompts: descrições de domínio e perguntas
  - utils.data_loader: ferramentas RAG (SupabaseRAGTool, GlobalSupabaseRAGTool)
  - utils.supabase_client: wrapper do banco de dados Supabase
"""

import json
import os
import uuid
from crewai import Agent, Task, Crew, Process, LLM  # Componentes do CrewAI
from typing import List, Dict, Any

from config.llm_config import get_model_name       # Retorna o nome do modelo LLM
from prompts.system_prompts import get_domain_description, get_agent_question
from utils.data_loader import SupabaseRAGTool, GlobalSupabaseRAGTool, _LAST_RAG_RESULTS
from utils.supabase_client import SupabaseDB

# Tracing — módulo 100% desacoplado; se removido, o sistema funciona normalmente
from tracing import TracingService, create_step_callback, create_task_callback

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
# Número máximo de vezes que o supervisor pode mandar um especialista refazer.
# Se após 2 retrabalhos o especialista ainda for reprovado, prossegue assim mesmo.
MAX_REWORK_ITERATIONS = 2

# Instância do banco usada por todos os agentes para salvar logs e RAG.
db = SupabaseDB()

# ---------------------------------------------------------------------------
# Helpers: criação de agentes
# ---------------------------------------------------------------------------

def _build_llm() -> LLM:
    """
    Cria a instância do modelo de linguagem (LLM) que os agentes usarão.

    Lê as variáveis de ambiente LLM_PROVIDER e as chaves de API correspondentes
    para construir o objeto LLM do CrewAI (que usa LiteLLM por baixo).

    Provedores suportados:
      - "groq"   → usa a API da Groq (compatível com OpenAI)
      - "openai"  → usa a API da OpenAI diretamente
      - "gemini"  → (padrão) usa a API do Google Gemini

    Returns:
        LLM: instância configurada para o provedor escolhido.
    """
    raw_model = get_model_name()  # Ex.: "gemini/gemini-1.5-flash"
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    if provider == "groq":
        # Groq usa uma API compatível com OpenAI — redirecionamos a base URL
        os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
        return LLM(model=raw_model, api_key=os.getenv("GROQ_API_KEY"))
    elif provider == "openai":
        return LLM(model=raw_model, api_key=os.getenv("OPENAI_API_KEY"))
    else:
        # Padrão: Gemini
        return LLM(model=raw_model, api_key=os.getenv("GEMINI_API_KEY"))


def _create_specialist(
    agent_id: int,
    llm_instance: LLM,
    step_callback=None,
) -> Agent:
    """
    Cria um agente Especialista para uma dimensão específica de risco.

    Cada especialista:
      - Tem um domínio de análise (ex.: "Tom Emocional, Comunicação e Intimidação")
      - Possui uma ferramenta RAG (SupabaseRAGTool) que busca casos históricos
        similares no Supabase para embasar sua análise
      - Deve OBRIGATORIAMENTE consultar a base de dados antes de emitir seu score
      - Retorna um JSON com 'score_risco' (0-100) e 'justificativa'

    Args:
        agent_id: ID do especialista (1 a 5), corresponde à dimensão de risco.
        llm_instance: instância do LLM já configurada.
        step_callback: (opcional) callback de tracing injetado pelo orquestrador.

    Returns:
        Agent: agente CrewAI pronto para executar tarefas.
    """
    domain = get_domain_description(agent_id)   # Nome da dimensão (ex.: "Isolamento Social")
    question = get_agent_question(agent_id)     # Pergunta feita à usuária nessa dimensão
    rag_tool = SupabaseRAGTool(agent_id=agent_id, db=db)  # Tool de RAG específica

    return Agent(
        role=f"Especialista {agent_id} ({domain})",
        goal=f"Analisar o relato da vítima na dimensão: {domain}.",
        backstory=(
            f"Você é um especialista na dimensão: {domain}. "
            f"A pergunta que foi feita à usuária para esta dimensão foi: \"{question}\" — "
            "leve isso em conta ao interpretar a resposta dela. "
            "Sua responsabilidade primária é avaliar o risco de violência doméstica baseando-se no relato da vítima. "
            "ANTES de dar seu veredito, você DEVE OBRIGATORIAMENTE usar sua ferramenta 'Buscar Casos Similares' "
            "passando o relato atual para buscar contexto histórico. "
            "É TERMINANTEMENTE PROIBIDO inventar uma análise antes de ler o banco de dados. "
            "Suas saídas devem ser diretas, profissionais e formatadas em JSON contendo "
            "'score_risco' (0-100) e 'justificativa'."
        ),
        verbose=True,          # Exibe logs detalhados no console
        allow_delegation=False, # Não pode delegar para outros agentes
        tools=[rag_tool],       # Ferramenta de busca de casos similares
        llm=llm_instance,       # Modelo LLM utilizado
        step_callback=step_callback,  # Tracing (None se desativado)
    )


def _create_supervisor(llm_instance: LLM, step_callback=None) -> Agent:
    """
    Cria o agente Supervisor de Qualidade.

    O Supervisor:
      - Recebe os relatórios de todos os 5 especialistas.
      - Verifica se cada um consultou dados históricos, se o score condiz
        com a justificativa e se a análise é coerente.
      - Emite APROVADO ou REPROVADO (com feedback obrigatório) para cada um.
      - Possui a ferramenta GlobalSupabaseRAGTool para buscar na base inteira.

    Args:
        llm_instance: instância do LLM já configurada.
        step_callback: (opcional) callback de tracing injetado pelo orquestrador.

    Returns:
        Agent: agente supervisor pronto para revisar análises.
    """
    rag_tool = GlobalSupabaseRAGTool(db=db)  # Tool de RAG global (todas as dimensões)

    return Agent(
        role="Supervisor de Qualidade Analítica",
        goal=(
            "Revisar cada análise emitida pelos especialistas e garantir precisão, "
            "coerência e uso de dados históricos."
        ),
        backstory=(
            "Você atua como um supervisor rigoroso. Para cada relatório de especialista você deve:\n"
            "1. Verificar se o especialista consultou a base de dados histórica.\n"
            "2. Avaliar se o score_risco condiz com a justificativa apresentada.\n"
            "3. Comparar com casos da base global usando sua ferramenta.\n"
            "4. Emitir APROVADO ou REPROVADO (com feedback claro) para cada um.\n"
            "Você DEVE retornar o resultado em JSON estruturado."
        ),
        verbose=True,          # Logs detalhados no console
        allow_delegation=False, # Não delega tarefas
        tools=[rag_tool],       # Ferramenta de busca global
        llm=llm_instance,
        step_callback=step_callback,  # Tracing (None se desativado)
    )


def _create_synthesizer(llm_instance: LLM, step_callback=None) -> Agent:
    """
    Cria o agente Sintetizador Final.

    O Sintetizador:
      - Recebe todas as análises aprovadas + o resumo do supervisor.
      - Consolida tudo em um único relatório com:
        • risk_score (0-100): score unificado de risco
        • risk_level: BAIXO | MODERADO | ALTO | CRÍTICO
        • consolidated_factors: lista de fatores de risco identificados
        • recommendations: lista de ações recomendadas
      - Não possui ferramentas RAG — trabalha apenas com os dados recebidos.

    Args:
        llm_instance: instância do LLM já configurada.
        step_callback: (opcional) callback de tracing injetado pelo orquestrador.

    Returns:
        Agent: agente sintetizador pronto para consolidar o relatório.
    """
    return Agent(
        role="Sintetizador Chefe de Análise de Risco",
        goal=(
            "Consolidar todas as análises aprovadas em um único relatório de risco "
            "(0 a 100), determinando o nível (BAIXO, MODERADO, ALTO, CRÍTICO)."
        ),
        backstory=(
            "Como sintetizador, sua função é agregar os dados de todos os especialistas "
            "e produzir a avaliação definitiva de risco da vítima."
        ),
        verbose=True,          # Logs detalhados
        allow_delegation=False, # Não delega tarefas
        llm=llm_instance,
        step_callback=step_callback,  # Tracing (None se desativado)
    )


# ---------------------------------------------------------------------------
# Helpers: parsing seguro de JSON
# ---------------------------------------------------------------------------

def _extract_json(text: str) -> dict:
    """
    Extrai o primeiro objeto JSON válido de uma string qualquer.

    Os agentes LLM frequentemente retornam texto livre em volta do JSON
    (ex.: "```json\n{...}\n```"). Esta função localiza o primeiro '{' e
    o último '}' na string e tenta fazer o parse apenas dessa porção.

    Args:
        text: string contendo (possivelmente) um objeto JSON.

    Returns:
        dict: objeto parseado, ou {} se não encontrar JSON válido.
    """
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > 0:
            return json.loads(text[start:end])
    except (json.JSONDecodeError, ValueError):
        pass
    return {}


# ===========================================================================
# Classe principal – orquestração em 3 fases com loop de retrabalho
# ===========================================================================

class RiskAnalysisCrew:
    """
    Orquestra a análise de risco em 3 fases:

    ┌─────────────────────────────────────────────────────┐
    │  FASE 1 – 5 Especialistas analisam em paralelo      │
    ├─────────────────────────────────────────────────────┤
    │  FASE 2 – Supervisor revisa → aprova / retrabalha   │
    │           (loop de até MAX_REWORK_ITERATIONS vezes)  │
    ├─────────────────────────────────────────────────────┤
    │  FASE 3 – Sintetizador consolida relatório final     │
    └─────────────────────────────────────────────────────┘
    """

    def __init__(self, responses: List[str]):
        """
        Inicializa o orquestrador.

        Args:
            responses: lista com exatamente 5 strings, uma para cada dimensão
                       de risco, na ordem dos agent_ids 1 a 5.
        """
        self.responses = responses   # Respostas da usuária
        self.llm = _build_llm()      # Instância única do LLM (reutilizada por todos os agentes)
        self.tracer: TracingService = None  # Inicializado no kickoff (quando analysis_id existe)

    # ----- FASE 1 ---------------------------------------------------------

    def _run_phase1(self) -> Dict[int, str]:
        """
        FASE 1: Executa os 5 especialistas sequencialmente.

        Para cada resposta da usuária:
          1. Cria o agente especialista correspondente (com tool RAG).
          2. Cria a Task com a descrição contendo a pergunta, o domínio e
             as regras (obrigatório usar RAG, retornar JSON).
          3. Adiciona agente e task às listas.

        Depois executa todos via Crew (Process.sequential) e coleta as
        saídas brutas (raw) de cada task.

        Returns:
            Dict[int, str]: mapa {agent_id: saída_bruta_do_agente}
        """
        agents: List[Agent] = []
        tasks: List[Task] = []

        for idx, answer in enumerate(self.responses[:5], start=1):
            domain = get_domain_description(idx)
            question = get_agent_question(idx)
            # Tracing: cria callback por especialista (None se tracer não existe)
            step_cb = (
                create_step_callback(self.tracer, f"Especialista {idx} ({domain})", agent_id=idx)
                if self.tracer else None
            )
            specialist = _create_specialist(agent_id=idx, llm_instance=self.llm, step_callback=step_cb)
            agents.append(specialist)

            task = Task(
                description=(
                    f"Pergunta feita à usuária: \"{question}\"\n"
                    f"Dimensão: {domain}\n\n"
                    f"Resposta da usuária:\n\"{answer}\"\n\n"
                    f"Regra 1: Use a ferramenta 'Buscar Casos Similares' passando \"{answer}\" como input.\n"
                    f"Regra 2: Após ler o histórico, analise o risco apresentado pela vítima "
                    f"levando em conta a pergunta que foi feita.\n"
                    f"Regra 3: Retorne APENAS um JSON válido contendo os campos "
                    f"'score_risco' (int 0-100) e 'justificativa' (string)."
                ),
                expected_output="JSON com 'score_risco' e 'justificativa'",
                agent=specialist,
            )
            tasks.append(task)

        # Cria o Crew com todos os agentes e tarefas e executa sequencialmente
        # Tracing: injeta task_callback no Crew se tracer estiver ativo
        task_cb = create_task_callback(self.tracer) if self.tracer else None
        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,  # Uma task por vez (cada especialista na sua vez)
            verbose=True,
            task_callback=task_cb,
        )
        crew.kickoff()  # Dispara a execução

        # Coletar saída individual de cada Task (texto bruto retornado pelo agente)
        outputs: Dict[int, str] = {}
        for idx, task in enumerate(tasks, start=1):
            outputs[idx] = task.output.raw if task.output else ""
        return outputs

    # ----- FASE 2 ---------------------------------------------------------

    def _run_supervisor_review(self, specialist_outputs: Dict[int, str]) -> Dict:
        """
        Executa o Supervisor para revisar todos os relatórios dos especialistas.

        O Supervisor recebe um texto com todos os relatórios concatenados e
        deve emitir um veredito para cada especialista (1 a 5) no formato:
        {
          "vereditos": {
            "1": {"status": "APROVADO", "feedback": "..."},
            "2": {"status": "REPROVADO", "feedback": "..."},
            ...
          }
        }

        O campo 'feedback' é OBRIGATÓRIO tanto para aprovações quanto reprovações.

        Args:
            specialist_outputs: {agent_id: saída_bruta} de cada especialista.

        Returns:
            Dict com a chave 'vereditos' contendo status e feedback por agente.
            Se o parsing falhar, retorna todos como APROVADO para não travar o fluxo.
        """
        supervisor = _create_supervisor(
            self.llm,
            step_callback=(
                create_step_callback(self.tracer, "Supervisor de Qualidade")
                if self.tracer else None
            ),
        )

        # Monta o texto de contexto concatenando todos os relatórios
        reports_text = ""
        for aid in sorted(specialist_outputs):
            domain = get_domain_description(aid)
            reports_text += (
                f"\n--- Relatório do Especialista {aid} ({domain}) ---\n"
                f"{specialist_outputs[aid]}\n"
            )

        # Define a tarefa do Supervisor: revisar e emitir vereditos
        review_task = Task(
            description=(
                f"Revise as análises dos 5 especialistas a seguir:\n"
                f"{reports_text}\n\n"
                "Para CADA especialista (1 a 5), emita um veredito:\n"
                "- 'APROVADO' se a análise está coerente, bem justificada e usa dados históricos.\n"
                "- 'REPROVADO' se faltam dados, a justificativa é fraca ou o score é inconsistente.\n\n"
                "REGRA IMPORTANTE: O campo 'feedback' é OBRIGATÓRIO e NUNCA pode ser vazio.\n"
                "- Se APROVADO: explique POR QUE a análise é satisfatória (ex: 'Score coerente com a justificativa, "
                "uso adequado de dados históricos, fatores de risco bem identificados').\n"
                "- Se REPROVADO: explique detalhadamente o que precisa ser corrigido.\n\n"
                "Retorne APENAS um JSON com a estrutura:\n"
                "{\n"
                '  "vereditos": {\n'
                '    "1": {"status": "APROVADO", "feedback": "Justificativa detalhada da aprovação..."},\n'
                '    "2": {"status": "REPROVADO", "feedback": "Motivo detalhado da reprovação..."},\n'
                "    ...\n"
                "  }\n"
                "}"
            ),
            expected_output="JSON com campo 'vereditos' contendo status e feedback OBRIGATÓRIO por especialista.",
            agent=supervisor,
        )

        # Executa o Supervisor como um Crew de agente único
        task_cb = create_task_callback(self.tracer) if self.tracer else None
        crew = Crew(
            agents=[supervisor],
            tasks=[review_task],
            process=Process.sequential,
            verbose=True,
            task_callback=task_cb,
        )
        result = crew.kickoff()

        # Tenta parsear o JSON de vereditos da saída do supervisor
        parsed = _extract_json(result.raw)
        if "vereditos" in parsed:
            return parsed

        # Fallback: se o parsing falhar, aprova tudo para não travar o fluxo
        return {
            "vereditos": {
                str(i): {"status": "APROVADO", "feedback": ""}
                for i in range(1, 6)
            }
        }

    def _rework_specialist(
        self,
        agent_id: int,
        original_answer: str,
        previous_output: str,
        feedback: str,
    ) -> str:
        """
        Re-executa um especialista específico incorporando o feedback do Supervisor.

        Quando o Supervisor reprova uma análise, este método cria uma nova tarefa
        para o especialista contendo:
          - O relato original da usuária
          - A análise anterior (que foi reprovada)
          - O feedback do supervisor (o que precisa ser corrigido)

        O especialista deve corrigir os pontos levantados e retornar um novo JSON.

        Args:
            agent_id: ID do especialista que precisa refazer (1-5).
            original_answer: resposta original da usuária para essa dimensão.
            previous_output: saída bruta da análise que foi reprovada.
            feedback: texto do supervisor explicando por que reprovou.

        Returns:
            str: nova saída bruta (raw) do especialista após o retrabalho.
        """
        domain = get_domain_description(agent_id)
        question = get_agent_question(agent_id)
        # Tracing: callback de retrabalho para este especialista
        step_cb = (
            create_step_callback(self.tracer, f"Especialista {agent_id} ({domain}) [Rework]", agent_id=agent_id)
            if self.tracer else None
        )
        specialist = _create_specialist(agent_id=agent_id, llm_instance=self.llm, step_callback=step_cb)

        rework_task = Task(
            description=(
                "⚠️ RETRABALHO SOLICITADO PELO SUPERVISOR ⚠️\n\n"
                f"Dimensão: {domain}\n"
                f"Pergunta feita à usuária: \"{question}\"\n\n"
                f"Relato original da usuária:\n\"{original_answer}\"\n\n"
                f"Sua análise anterior:\n{previous_output}\n\n"
                f"Feedback do Supervisor:\n{feedback}\n\n"
                "INSTRUÇÕES:\n"
                "1. Corrija os pontos levantados pelo supervisor.\n"
                "2. Use novamente a ferramenta 'Buscar Casos Similares' se precisar de mais contexto.\n"
                "3. Retorne APENAS um JSON com 'score_risco' (int 0-100) e 'justificativa' (string)."
            ),
            expected_output="JSON corrigido com 'score_risco' e 'justificativa'",
            agent=specialist,
        )

        # Cria o Crew com um único especialista e executa
        task_cb = create_task_callback(self.tracer) if self.tracer else None
        crew = Crew(
            agents=[specialist],
            tasks=[rework_task],
            process=Process.sequential,
            verbose=True,
            task_callback=task_cb,
        )
        result = crew.kickoff()
        return result.raw  # Retorna a saída bruta corrigida

    def _phase2_review_loop(
        self, specialist_outputs: Dict[int, str], analysis_id: str
    ) -> tuple[Dict[int, str], str, Dict[int, int], Dict, List[Dict]]:
        """
        FASE 2: Loop de revisão pelo Supervisor com retrabalho automático.

        Fluxo:
          1. O Supervisor avalia todos os relatórios.
          2. Se houver reprovações:
             a) Salva a análise reprovada + feedback no banco (agent_rework_history)
             b) O especialista reprovado refaz sua análise
          3. Repete até tudo ser aprovado ou esgotar MAX_REWORK_ITERATIONS.

        Args:
            specialist_outputs: {agent_id: saída_bruta} da Fase 1.
            analysis_id: UUID que vincula todos os logs desta análise.

        Returns:
            Tupla com 5 elementos:
              - outputs_aprovados: {agent_id: saída_final} de cada especialista
              - supervisor_raw: JSON string do último veredito do supervisor
              - rework_counts: {agent_id: nº de retrabalhos} (0 se nunca reprovou)
              - last_review: dict com os vereditos finais do supervisor
              - rework_history: lista de dicts com todo o histórico de retrabalhos
        """
        outputs = dict(specialist_outputs)  # Cópia de trabalho para não alterar o original
        supervisor_raw = "{}"               # Último JSON bruto do supervisor
        rework_counts: Dict[int, int] = {i: 0 for i in range(1, 6)}  # Contador por agente
        last_review: Dict = {}              # Último veredito completo
        rework_history: List[Dict] = []     # Histórico de todos os retrabalhos
        total_iterations = 0

        for iteration in range(MAX_REWORK_ITERATIONS + 1):
            total_iterations = iteration + 1
            print(f"\n🔍 Supervisor – rodada de revisão {total_iterations}")

            # Atualizar iteração no tracing
            if self.tracer:
                self.tracer.set_phase("phase2", iteration=total_iterations)

            # Executa o Supervisor para avaliar os relatórios atuais
            review = self._run_supervisor_review(outputs)
            last_review = review
            supervisor_raw = json.dumps(review, ensure_ascii=False)
            vereditos = review.get("vereditos", {})

            # Identifica quais especialistas foram reprovados nesta rodada
            rejected_ids = [
                int(aid)
                for aid, v in vereditos.items()
                if v.get("status", "").upper() == "REPROVADO"
            ]

            # Se ninguém foi reprovado, encerra o loop
            if not rejected_ids:
                print(f"✅ Todos os relatórios APROVADOS na rodada {total_iterations}.")
                break

            # Se já atingiu o limite de retrabalhos, prossegue com o que tem
            if iteration == MAX_REWORK_ITERATIONS:
                print(
                    f"⚠️  Limite de {MAX_REWORK_ITERATIONS} retrabalho(s) atingido. "
                    "Prosseguindo com os relatórios atuais."
                )
                break

            # --- Retrabalho dos reprovados ---
            # Antes de sobrescrever a saída, salva a análise reprovada no banco
            print(f"🔄 Especialistas reprovados: {rejected_ids} – iniciando retrabalho…")
            for aid in rejected_ids:
                feedback = vereditos.get(str(aid), {}).get("feedback", "Melhore sua análise.")
                original = self.responses[aid - 1] if aid <= len(self.responses) else ""
                rejected_output = outputs.get(aid, "")          # Saída que foi reprovada
                rejected_parsed = _extract_json(rejected_output) # Parse para extrair score/justificativa
                domain = get_domain_description(aid)

                # Monta o registro do evento de retrabalho (preserva a análise original + feedback)
                rework_event = {
                    "analysis_id": analysis_id,
                    "agent_id": aid,
                    "agent_domain": domain,
                    "iteration": total_iterations,
                    "original_score_risco": rejected_parsed.get("score_risco"),
                    "original_justificativa": rejected_parsed.get("justificativa", ""),
                    "original_raw_output": rejected_output,
                    "supervisor_feedback": feedback,
                }
                rework_history.append(rework_event)  # Guarda na lista em memória

                # Persiste no banco de dados imediatamente (tabela agent_rework_history)
                db.log_rework_event(**rework_event)
                print(f"   💾 Histórico de retrabalho do Especialista {aid} salvo (rodada {total_iterations}).")

                # Executa o retrabalho: o especialista recebe o feedback e refaz
                new_output = self._rework_specialist(
                    agent_id=aid,
                    original_answer=original,
                    previous_output=rejected_output,
                    feedback=feedback,
                )
                outputs[aid] = new_output  # Substitui a saída antiga pela nova
                rework_counts[aid] = rework_counts.get(aid, 0) + 1  # Incrementa contador
                print(f"   ✏️  Especialista {aid} refez sua análise.")

        return outputs, supervisor_raw, rework_counts, last_review, rework_history

    # ----- FASE 3 ---------------------------------------------------------

    def _run_phase3(self, specialist_outputs: Dict[int, str], supervisor_summary: str) -> Dict:
        """
        FASE 3: Sintetizador consolida os relatórios aprovados no veredito final.

        Recebe todos os relatórios aprovados e o resumo do supervisor, e gera
        um relatório unificado contendo:
          - risk_score (0-100): score consolidado
          - risk_level: BAIXO | MODERADO | ALTO | CRÍTICO
          - consolidated_factors: lista de fatores de risco identificados
          - recommendations: lista de recomendações de ação

        Args:
            specialist_outputs: {agent_id: saída_aprovada} de cada especialista.
            supervisor_summary: JSON string com os vereditos do supervisor.

        Returns:
            Dict com o relatório final. Se o parsing falhar, retorna um dict
            com risk_score=50 e risk_level="DESCONHECIDO".
        """
        synthesizer = _create_synthesizer(
            self.llm,
            step_callback=(
                create_step_callback(self.tracer, "Sintetizador Chefe")
                if self.tracer else None
            ),
        )

        # Monta texto concatenando todos os relatórios aprovados
        reports_text = ""
        for aid in sorted(specialist_outputs):
            domain = get_domain_description(aid)
            reports_text += (
                f"\n--- Especialista {aid} ({domain}) ---\n"
                f"{specialist_outputs[aid]}\n"
            )

        # Define a tarefa de síntese
        synth_task = Task(
            description=(
                f"Resumo do Supervisor:\n{supervisor_summary}\n\n"
                f"Relatórios aprovados dos especialistas:\n{reports_text}\n\n"
                "Consolide todas as análises acima e calcule o score de risco final.\n"
                "Defina o nível como BAIXO, MODERADO, ALTO ou CRÍTICO.\n\n"
                "Retorne ESTRITAMENTE um JSON contendo:\n"
                "- 'risk_score' (int 0-100)\n"
                "- 'risk_level' (string: BAIXO | MODERADO | ALTO | CRÍTICO)\n"
                "- 'consolidated_factors' (lista de strings com fatores de risco)\n"
                "- 'recommendations' (lista de strings com recomendações)"
            ),
            expected_output="JSON com risk_score, risk_level, consolidated_factors, recommendations",
            agent=synthesizer,
        )

        # Executa o Sintetizador
        task_cb = create_task_callback(self.tracer) if self.tracer else None
        crew = Crew(
            agents=[synthesizer],
            tasks=[synth_task],
            process=Process.sequential,
            verbose=True,
            task_callback=task_cb,
        )
        result = crew.kickoff()

        # Tenta parsear o JSON do resultado final
        parsed = _extract_json(result.raw)
        if parsed:
            return parsed
        # Fallback caso não consiga parsear
        return {"raw": result.raw, "risk_score": 50, "risk_level": "DESCONHECIDO"}

    # ----- Orquestração principal ------------------------------------------

    def kickoff(self) -> Dict:
        """
        Método principal que orquestra as 3 fases da análise.

        Fluxo completo:
          1. Gera um analysis_id (UUID) único para vincular todos os logs.
          2. Executa a Fase 1 (5 especialistas).
          3. Executa a Fase 2 (Supervisor + loop de retrabalho).
          4. Salva os logs individuais de cada especialista no Supabase.
          5. Executa a Fase 3 (Sintetizador).
          6. Salva o log mestre (resultado final) no Supabase.
          7. Retorna o dict final com score, nível, fatores e recomendações.

        Returns:
            Dict contendo risk_score, risk_level, consolidated_factors,
            recommendations e analysis_id.
        """
        # Gerar ID único que liga todos os logs desta análise
        analysis_id = str(uuid.uuid4())
        print(f"\n🆔 Analysis ID: {analysis_id}")

        # Inicializar tracing (módulo desacoplado — se Supabase indisponível, ignora)
        self.tracer = TracingService(analysis_id=analysis_id, phase="phase1")

        # ========== FASE 1 ==========
        print("=" * 60)
        print("🤖 FASE 1: Análise pelos 5 Especialistas")
        print("=" * 60)
        specialist_outputs = self._run_phase1()

        # ========== FASE 2 ==========
        print("\n" + "=" * 60)
        print("🔍 FASE 2: Revisão pelo Supervisor (com retrabalho)")
        print("=" * 60)
        self.tracer.set_phase("phase2")  # Atualiza fase no tracing
        approved_outputs, supervisor_summary, rework_counts, final_review, rework_history = (
            self._phase2_review_loop(specialist_outputs, analysis_id)
        )

        # ========== SALVAR LOGS INDIVIDUAIS ==========
        # Para cada especialista, extrai o JSON parseado, o veredito do supervisor
        # e o resultado RAG (do cache da tool) e persiste na tabela agent_individual_logs.
        print("\n💾 Salvando logs individuais dos especialistas…")
        vereditos = final_review.get("vereditos", {})
        for aid in sorted(approved_outputs):
            domain = get_domain_description(aid)   # Nome da dimensão de risco
            question = get_agent_question(aid)     # Pergunta feita à usuária
            raw_out = approved_outputs[aid]         # Saída bruta final do agente
            parsed_out = _extract_json(raw_out)     # Extrai score_risco e justificativa

            v = vereditos.get(str(aid), {})  # Veredito do supervisor para este agente

            # Puxar resultado RAG direto do cache da tool (preenchido durante a execução)
            # Cada SupabaseRAGTool salva em _LAST_RAG_RESULTS[agent_id] quando é chamada
            rag_text = _LAST_RAG_RESULTS.get(aid, "")

            # Salva no Supabase (tabela agent_individual_logs)
            db.log_individual_agent(
                analysis_id=analysis_id,
                agent_id=aid,
                agent_domain=domain,
                question=question,
                user_response=self.responses[aid - 1] if aid <= len(self.responses) else "",
                score_risco=parsed_out.get("score_risco"),
                justificativa=parsed_out.get("justificativa", ""),
                rag_results=rag_text or None,            # Texto dos casos similares encontrados
                raw_output=raw_out,                       # Saída bruta completa do agente
                rework_count=rework_counts.get(aid, 0),   # Quantas vezes retrabalhado (0 se aprovado de primeira)
                supervisor_status=v.get("status", "APROVADO"),   # APROVADO ou REPROVADO
                supervisor_feedback=v.get("feedback", ""),       # Feedback do supervisor (obrigatório)
            )
            print(f"   ✅ Especialista {aid} logado.")

        # ========== FASE 3 ==========
        print("\n" + "=" * 60)
        print("📊 FASE 3: Síntese e Consolidação Final")
        print("=" * 60)
        self.tracer.set_phase("phase3")  # Atualiza fase no tracing
        final = self._run_phase3(approved_outputs, supervisor_summary)

        # Log mestre no Supabase: salva o resultado final (tabela agent_logs)
        # vinculado ao mesmo analysis_id para rastreabilidade completa.
        db.log_analysis(
            agent_role="Sintetizador Chefe",
            quest="Consolidacao Geral",
            user_response=json.dumps(self.responses, ensure_ascii=False),
            analysis_result=json.dumps(final, ensure_ascii=False),
            metadata={"status": "sucesso"},
            analysis_id=analysis_id,
        )

        # Inclui o analysis_id no retorno para o front-end poder rastrear
        final["analysis_id"] = analysis_id
        return final

"""
prompts/system_prompts.py — Mapeamento de domínios e perguntas por especialista.

Cada especialista (agent_id 1-5) cobre uma dimensão específica de risco de
violência doméstica. Este módulo fornece:

  - DOMAIN_DESCRIPTIONS : dict[int, str]
      Descrição curta do domínio (usada no prompt do agente e nos logs).

  - AGENT_QUESTIONS : dict[int, str]
      A pergunta original que foi apresentada à usuária no formulário.
      Cada pergunta mapeia diretamente ao domínio do respectivo especialista.

Funções auxiliares:
  - get_domain_description(agent_id) : retorna a descrição do domínio
  - get_agent_question(agent_id)     : retorna a pergunta do formulário
"""


# ---------------------------------------------------------------------------
# Descrições dos 5 domínios de análise de risco
# ---------------------------------------------------------------------------
# Cada chave (1-5) corresponde ao agent_id do especialista responsável.
DOMAIN_DESCRIPTIONS = {
    1: "Rotina, Sobrecarga e Divisão de Tarefas Domésticas",
    2: "Tom Emocional, Comunicação e Intimidação",
    3: "Redes de Apoio, Isolamento Social e Vínculos",
    4: "Controle Financeiro e Dependência Econômica",
    5: "Bem-estar Físico, Psicológico e Saúde Mental"
}

# ---------------------------------------------------------------------------
# Perguntas do formulário — uma por dimensão
# ---------------------------------------------------------------------------
# Cada pergunta foi elaborada para capturar indicadores específicos da
# dimensão correspondente. A resposta da usuária é encaminhada ao
# especialista cujo agent_id corresponde à chave.
AGENT_QUESTIONS = {
    1: "Como é a divisão de tarefas domésticas na sua casa? Você sente que há um equilíbrio?",
    2: "Como é a comunicação entre você e seu parceiro? Ele costuma gritar, xingar ou te intimidar?",
    3: "Você tem amigos, familiares ou pessoas de confiança com quem pode contar? Seu parceiro interfere nessas relações?",
    4: "Como funciona a questão financeira na sua casa? Você tem acesso e autonomia sobre o dinheiro?",
    5: "Como você tem se sentido fisicamente e emocionalmente? Tem sentido medo, ansiedade ou algum desconforto?"
}


def get_domain_description(agent_id: int) -> str:
    """
    Retorna a descrição do domínio de risco para o especialista indicado.

    Args:
        agent_id: Identificador do especialista (1-5).

    Returns:
        Descrição textual do domínio, ou fallback genérico se ID inválido.
    """
    return DOMAIN_DESCRIPTIONS.get(agent_id, f"Domínio {agent_id}")


def get_agent_question(agent_id: int) -> str:
    """
    Retorna a pergunta original do formulário associada à dimensão do agente.

    Args:
        agent_id: Identificador do especialista (1-5).

    Returns:
        String com a pergunta que foi apresentada à usuária.
    """
    return AGENT_QUESTIONS.get(agent_id, f"Pergunta da dimensão {agent_id}")

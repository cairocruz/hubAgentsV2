"""
utils/supabase_client.py — Wrapper para o banco de dados Supabase.

Este módulo encapsula toda a comunicação com o Supabase, incluindo:
  - Busca de respostas similares via pgvector (RAG)
  - Gravação de logs finais (tabela agent_logs)
  - Gravação de logs individuais por especialista (tabela agent_individual_logs)
  - Gravação do histórico de retrabalho (tabela agent_rework_history)

O cliente Supabase é criado de forma lazy (sob demanda) na primeira vez que
alguém instanciar SupabaseDB, evitando bloqueios durante o import do módulo.

Variáveis de ambiente necessárias (definidas no .env):
  - SUPABASE_URL: URL do projeto Supabase (ex.: https://xxx.supabase.co)
  - SUPABASE_KEY: chave de serviço (service_role) do Supabase
"""

import os
from supabase import create_client, Client      # SDK oficial do Supabase
from dotenv import load_dotenv                   # Carrega variáveis do .env
from typing import List, Dict, Any, Optional

# Carregar variáveis de ambiente do arquivo .env para os.environ
load_dotenv()

# ---------------------------------------------------------------------------
# Inicialização lazy do cliente Supabase
# ---------------------------------------------------------------------------
# Estas variáveis de módulo controlam a criação sob demanda.
# O cliente só é criado na primeira chamada a _get_supabase_client().
_supabase_client: Client = None      # Instância do cliente (ou None se falhar)
_supabase_initialized: bool = False  # Flag indicando se já tentou inicializar


def _get_supabase_client() -> Optional[Client]:
    """
    Inicializa o cliente Supabase apenas na primeira chamada (padrão Singleton lazy).

    Na primeira execução:
      - Lê SUPABASE_URL e SUPABASE_KEY do .env.
      - Se ambos existirem, cria o cliente com create_client().
      - Se faltar alguma variável ou ocorrer erro, retorna None.

    Nas chamadas seguintes, retorna a instância já criada (ou None).

    Returns:
        Client ou None se o Supabase não estiver configurado/acessível.
    """
    global _supabase_client, _supabase_initialized
    if _supabase_initialized:
        return _supabase_client

    _supabase_initialized = True
    url: str = os.getenv("SUPABASE_URL", "")
    key: str = os.getenv("SUPABASE_KEY", "")

    if not url or not key:
        print("⚠️ AVISO: Variáveis SUPABASE_URL e SUPABASE_KEY não encontradas no .env")
        return None

    try:
        _supabase_client = create_client(url, key)
    except Exception as e:
        print(f"⚠️ AVISO: Falha ao conectar ao Supabase: {e}")
        _supabase_client = None

    return _supabase_client


# ---------------------------------------------------------------------------
# Classe principal de acesso ao banco
# ---------------------------------------------------------------------------

class SupabaseDB:
    """
    Classe utilitária para interagir com o Supabase.

    Responsabilidades:
      - Buscar respostas similares via pgvector (RAG) usando a função RPC match_responses
      - Salvar logs finais do sintetizador (tabela agent_logs)
      - Salvar logs individuais de cada especialista (tabela agent_individual_logs)
      - Salvar histórico de retrabalho quando o supervisor reprova (tabela agent_rework_history)

    Uso:
        db = SupabaseDB()
        if db.client:
            # Supabase está conectado, pode usar normalmente
        else:
            # Supabase não configurado, opera sem banco
    """

    def __init__(self):
        """Obtém (ou cria) o cliente Supabase via inicialização lazy."""
        self.client = _get_supabase_client()
        
    def find_similar_responses(
        self,
        embedding: List[float],
        agent_id: Optional[int] = None,
        limit: int = 5,
        match_threshold: float = 0.70,
    ) -> List[Dict[str, Any]]:
        """
        Busca respostas históricas similares no Supabase usando pgvector.

        Chama a função RPC 'match_responses' criada no banco, que:
          1. Calcula a distância cosseno entre o embedding da query e os
             embeddings armazenados na tabela agent_examples.
          2. Filtra por agent_id (se informado) e por threshold mínimo.
          3. Retorna os top-K resultados ordenados por similaridade.

        Args:
            embedding: vetor de 384 dimensões (gerado pelo SentenceTransformer)
                       representando a resposta atual da usuária.
            agent_id: ID do especialista (1-5) para filtrar por dimensão.
                      Se None, busca em toda a base histórica.
            limit: número máximo de resultados a retornar.
            match_threshold: similaridade mínima (0.0 a 1.0). Resultados
                             abaixo deste valor são descartados.

        Returns:
            Lista de dicts, cada um com: id, frase, risco, fator, taxonomia,
            metadata e similarity (float 0-1).
        """
        if not self.client:
            return []
            
        try:
            # Chama a função RPC 'match_responses' definida no banco.
            # Esta função faz: SELECT ... WHERE similarity > threshold ORDER BY similarity DESC LIMIT N
            response = self.client.rpc(
                'match_responses',
                {
                    'query_embedding': embedding,       # Vetor da resposta atual
                    'filter_agent_id': agent_id,        # Filtro por dimensão (None = todas)
                    'match_threshold': match_threshold,  # Similaridade mínima
                    'match_count': limit                 # Quantidade máxima de resultados
                }
            ).execute()
            
            return response.data
            
        except Exception as e:
            print(f"❌ Erro ao buscar respostas similares: {e}")
            return []

    def log_analysis(
        self,
        agent_role: str,
        quest: str,
        user_response: str,
        analysis_result: str,
        metadata: Dict = None,
        analysis_id: Optional[str] = None,
    ) -> bool:
        """
        Salva o log final (resultado do Sintetizador) na tabela agent_logs.

        Esta tabela contém o resultado consolidado de cada análise completa.
        Também é usada para registrar erros fatais do sistema.

        Args:
            agent_role: papel do agente (ex.: "Sintetizador Chefe" ou "Sistema").
            quest: descrição da operação (ex.: "Consolidacao Geral", "Erro Fatal").
            user_response: respostas da usuária em JSON (ou "N/A" em caso de erro).
            analysis_result: resultado da análise em JSON.
            metadata: dados adicionais em formato dict (vira JSONB no banco).
            analysis_id: UUID que vincula ao agent_individual_logs e agent_rework_history.

        Returns:
            True se gravou com sucesso, False se falhou.
        """
        if not self.client:
            return False

        try:
            data = {
                "agent_role": agent_role,
                "quest": quest,
                "user_response": user_response,
                "analysis_result": analysis_result,
                "metadata": metadata or {},
            }
            if analysis_id:
                data["analysis_id"] = analysis_id

            self.client.table('agent_logs').insert(data).execute()
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar log no Supabase: {e}")
            return False

    def log_individual_agent(
        self,
        analysis_id: str,
        agent_id: int,
        agent_domain: str,
        question: str,
        user_response: str,
        score_risco: Optional[int] = None,
        justificativa: Optional[str] = None,
        rag_results: Optional[str] = None,
        raw_output: Optional[str] = None,
        rework_count: int = 0,
        supervisor_status: Optional[str] = None,
        supervisor_feedback: Optional[str] = None,
        metadata: Dict = None,
    ) -> bool:
        """
        Salva o log individual de um especialista na tabela agent_individual_logs.

        Cada registro representa a análise FINAL (após eventuais retrabalhos)
        de um especialista, vinculada ao analysis_id da análise geral.

        Args:
            analysis_id: UUID da análise (vincula agent_logs e agent_rework_history).
            agent_id: ID do especialista (1-5).
            agent_domain: nome da dimensão (ex.: "Isolamento Social").
            question: pergunta feita à usuária nesta dimensão.
            user_response: resposta original da usuária.
            score_risco: score de risco (0-100) atribuído pelo agente.
            justificativa: texto explicando o score.
            rag_results: texto com os casos históricos similares encontrados.
            raw_output: saída bruta completa do agente (pode incluir markdown etc.).
            rework_count: quantas vezes o agente refez a análise (0 = aprovado de primeira).
            supervisor_status: "APROVADO" ou "REPROVADO" (veredito final).
            supervisor_feedback: feedback do supervisor (obrigatório, mesmo se aprovado).
            metadata: dados adicionais em dict.

        Returns:
            True se gravou com sucesso, False se falhou.
        """
        if not self.client:
            return False

        try:
            data = {
                "analysis_id": analysis_id,
                "agent_id": agent_id,
                "agent_domain": agent_domain,
                "question": question,
                "user_response": user_response,
                "score_risco": score_risco,
                "justificativa": justificativa,
                "rag_results": rag_results,
                "raw_output": raw_output,
                "rework_count": rework_count,
                "supervisor_status": supervisor_status,
                "supervisor_feedback": supervisor_feedback,
                "metadata": metadata or {},
            }

            self.client.table('agent_individual_logs').insert(data).execute()
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar log individual (agent {agent_id}): {e}")
            return False

    def log_rework_event(
        self,
        analysis_id: str,
        agent_id: int,
        agent_domain: str,
        iteration: int,
        original_score_risco: Optional[int] = None,
        original_justificativa: Optional[str] = None,
        original_raw_output: Optional[str] = None,
        supervisor_feedback: str = "",
    ) -> bool:
        """
        Salva o registro de uma análise REPROVADA pelo supervisor
        na tabela agent_rework_history.

        Cada registro preserva:
          - A análise original que foi reprovada (score, justificativa, raw_output)
          - O feedback do supervisor explicando por que reprovou
          - A rodada (iteration) em que o retrabalho ocorreu

        Isso permite rastrear a evolução das análises ao longo
        das rodadas de revisão.

        Args:
            analysis_id: UUID da análise.
            agent_id: ID do especialista reprovado (1-5).
            agent_domain: nome da dimensão de risco.
            iteration: número da rodada de revisão (1, 2, ...).
            original_score_risco: score da análise que foi reprovada.
            original_justificativa: justificativa da análise reprovada.
            original_raw_output: saída bruta completa que foi reprovada.
            supervisor_feedback: texto do supervisor explicando a reprovação.

        Returns:
            True se gravou com sucesso, False se falhou.
        """
        if not self.client:
            return False

        try:
            data = {
                "analysis_id": analysis_id,
                "agent_id": agent_id,
                "agent_domain": agent_domain,
                "iteration": iteration,
                "original_score_risco": original_score_risco,
                "original_justificativa": original_justificativa,
                "original_raw_output": original_raw_output,
                "supervisor_feedback": supervisor_feedback,
            }

            self.client.table('agent_rework_history').insert(data).execute()
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar histórico de retrabalho (agent {agent_id}, iter {iteration}): {e}")
            return False

"""
utils/data_loader.py — Ferramentas RAG (Retrieval-Augmented Generation) para os agentes.

Este módulo define as ferramentas que os agentes CrewAI usam para buscar
casos históricos similares e embasar suas análises de risco.

Contém duas ferramentas:
  - SupabaseRAGTool: usada pelos 5 especialistas — busca casos similares
    filtrados pela dimensão de risco (agent_id) do especialista.
  - GlobalSupabaseRAGTool: usada pelo Supervisor — busca em toda a base
    histórica sem filtro de dimensão.

Fluxo de busca (ambas as ferramentas):
  1. Gera embedding da frase usando SentenceTransformer (paraphrase-multilingual-MiniLM-L12-v2).
  2. Tenta buscar no Supabase via pgvector (RPC match_responses).
  3. Se o Supabase não estiver configurado ou não retornar resultados,
     faz fallback local usando os CSVs em ./data/ com busca por cosine similarity.
  4. Formata os resultados como texto legível para o agente.
  5. Salva o resultado no cache _LAST_RAG_RESULTS para que o crew possa
     gravá-lo no log do banco depois.

Dependências:
  - sentence_transformers: modelo de embedding multilíngue
  - numpy: operações vetoriais para cosine similarity local
  - crewai.tools.BaseTool: classe base para ferramentas do CrewAI
"""

import json
import os
import csv
from typing import Any, Dict, List, Optional, Tuple

import numpy as np                                      # Operações vetoriais
from sentence_transformers import SentenceTransformer   # Modelo de embedding
from pydantic import Field                              # Campos tipados para BaseTool (Pydantic)
from crewai.tools import BaseTool                       # Classe base de ferramentas CrewAI

from utils.supabase_client import SupabaseDB            # Wrapper do Supabase


# ---------------------------------------------------------------------------
# Cache global de embeddings locais
# ---------------------------------------------------------------------------
# Evita recomputar embeddings dos CSVs a cada chamada da tool.
# Chave: (agent_id, tamanho_do_dataset), Valor: dict com frases, embeddings, model_name.
_LOCAL_DATA_CACHE: Dict[Tuple[Optional[int], int], Dict[str, Any]] = {}

# ---------------------------------------------------------------------------
# Cache global de resultados RAG
# ---------------------------------------------------------------------------
# Armazena o último resultado RAG retornado por cada agent_id.
# Usado pelo crew (kickoff) para gravar no campo rag_results do log individual.
# Chave: agent_id (int 1-5) ou 'global' (para o Supervisor).
# Valor: string formatada com os casos similares encontrados.
_LAST_RAG_RESULTS: Dict[Any, str] = {}


# ---------------------------------------------------------------------------
# Helpers: fallback local com CSVs
# ---------------------------------------------------------------------------

def _local_dataset_paths(agent_id: Optional[int]) -> List[str]:
    """
    Retorna os caminhos dos CSVs de dados históricos para o agent_id dado.

    Se agent_id for None, retorna todos os 5 datasets (busca global).
    Se agent_id for 1-5, retorna apenas o dataset correspondente.

    Args:
        agent_id: ID do especialista (1-5) ou None para todos.

    Returns:
        Lista de caminhos absolutos dos CSVs.
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))  # Raiz do projeto
    data_dir = os.path.join(base_dir, 'data')
    if agent_id is None:
        # Retorna todos os 5 datasets (para busca global do Supervisor)
        return [os.path.join(data_dir, f'dataset_{i}.csv') for i in range(1, 6)]
    # Retorna apenas o dataset do especialista específico
    return [os.path.join(data_dir, f'dataset_{agent_id}.csv')]


def _read_local_rows(agent_id: Optional[int]) -> List[Dict[str, str]]:
    """
    Lê os CSVs locais e retorna uma lista de dicts com os campos normalizados.

    Cada CSV deve ter as colunas: frase, risco, fator, taxonomia, metadata.

    Args:
        agent_id: ID do especialista (1-5) ou None para todos.

    Returns:
        Lista de dicts com campos {frase, risco, fator, taxonomia, metadata}.
        Entradas com frase vazia são descartadas.
    """
    rows: List[Dict[str, str]] = []
    for path in _local_dataset_paths(agent_id):
        if not os.path.exists(path):
            continue
        with open(path, mode='r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row:
                    continue
                # Normaliza os campos removendo espaços extras
                rows.append({
                    'frase': (row.get('frase') or '').strip(),
                    'risco': (row.get('risco') or '').strip(),
                    'fator': (row.get('fator') or '').strip(),
                    'taxonomia': (row.get('taxonomia') or '').strip(),
                    'metadata': (row.get('metadata') or '').strip(),
                })
    # Remove entradas com frase vazia
    return [r for r in rows if r.get('frase')]


def _local_find_similar(
    encoder_model: Any,
    query: str,
    agent_id: Optional[int],
    limit: int,
) -> List[Dict[str, Any]]:
    """
    Fallback local: busca por similaridade cosseno usando os CSVs em ./data/.

    Quando o Supabase não está disponível ou não retorna resultados,
    esta função é usada como alternativa. Ela:
      1. Lê todas as frases dos CSVs correspondentes ao agent_id.
      2. Gera embeddings das frases (com cache para não recomputar).
      3. Gera embedding da query.
      4. Calcula similaridade cosseno (dot product, pois vetores estão normalizados).
      5. Retorna os top-K mais similares.

    Args:
        encoder_model: instância do SentenceTransformer para gerar embeddings.
        query: texto da resposta da usuária para buscar similares.
        agent_id: ID do especialista (1-5) ou None para busca global.
        limit: número máximo de resultados.

    Returns:
        Lista de dicts com os campos do CSV + 'similarity' (float 0-1).
    """
    rows = _read_local_rows(agent_id)
    if not rows:
        return []

    frases = [r['frase'] for r in rows]

    # Cache de embeddings por (agent_id, tamanho_do_dataset) para evitar recomputar
    cache_key = (agent_id, len(frases))
    cached = _LOCAL_DATA_CACHE.get(cache_key)
    if cached and cached.get('frases') == frases and cached.get('model_name') == getattr(encoder_model, "model_card", None):
        # Usa embeddings do cache se as frases e o modelo não mudaram
        frase_embeddings = cached['embeddings']
    else:
        # Gera embeddings de todas as frases (normalizados para cosine sim = dot product)
        frase_embeddings = encoder_model.encode(frases, normalize_embeddings=True)
        frase_embeddings = np.asarray(frase_embeddings, dtype=np.float32)
        _LOCAL_DATA_CACHE[cache_key] = {
            'frases': frases,
            'embeddings': frase_embeddings,
            'model_name': getattr(encoder_model, "model_card", None),
        }

    # Gera embedding da query atual
    query_embedding = encoder_model.encode([query], normalize_embeddings=True)
    query_embedding = np.asarray(query_embedding[0], dtype=np.float32)

    # Calcula similaridade cosseno via dot product (vetores já normalizados)
    sims = frase_embeddings @ query_embedding
    if sims.size == 0:
        return []

    # Seleciona os índices dos top-K mais similares (ordena decrescente)
    top_idx = np.argsort(-sims)[: max(1, limit)]
    results: List[Dict[str, Any]] = []
    for idx in top_idx.tolist():
        r = rows[int(idx)]
        results.append({
            **r,
            'similarity': float(sims[int(idx)]),  # Adiciona o score de similaridade
        })
    return results

# ===========================================================================
# SupabaseRAGTool — Ferramenta RAG específica por dimensão (usada pelos especialistas)
# ===========================================================================

class SupabaseRAGTool(BaseTool):
    """
    Ferramenta RAG para os agentes especialistas (agent_id 1-5).

    Quando o agente chama esta ferramenta passando o relato da usuária:
      1. Gera embedding com SentenceTransformer.
      2. Busca no Supabase os 5 casos mais similares da mesma dimensão.
      3. Se Supabase não tiver resultados, faz fallback local (CSVs).
      4. Retorna texto formatado com casos históricos e seus fatores de risco.

    Herda de BaseTool (Pydantic), por isso os campos são declarados como class-level.
    """
    name: str = "Buscar Casos Similares"
    description: str = (
        "Útil para encontrar exemplos históricos de respostas de usuárias similares à atual, "
        "ajudando na classificação de risco. "
        "O input deve ser OBRIGATORIAMENTE uma string contendo o relato atual da usuária para pesquisar."
    )

    # Campos injetados via Pydantic Field:
    agent_id: int = Field(description="ID do agente especialista chamando a ferramenta (1 a 5)")
    db: SupabaseDB = Field(default_factory=SupabaseDB, exclude=True)     # Excluído do schema da tool
    encoder_model: Any = Field(default=None, exclude=True)               # Modelo é lazy-loaded

    def _run(self, frase_usuario: str) -> str:
        """
        Executa a busca por frases similares no banco de dados.

        Args:
            frase_usuario: texto do relato da usuária para buscar similares.

        Returns:
            String formatada com os casos históricos encontrados,
            ou mensagem de erro/atenção se nenhum caso for encontrado.
        """
        if not self.encoder_model:
            # Lazy loading do modelo (só carrega quando a tool é chamada pela 1ª vez)
            # O modelo paraphrase-multilingual-MiniLM-L12-v2 gera vetores de 384 dimensões
            # e suporta português nativamente.
            self.encoder_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        try:
            # 1. Gerar embedding da frase da usuária
            embedding = self.encoder_model.encode([frase_usuario]).tolist()[0]

            # 2. Tentar buscar no Supabase (limit=5 para não exceder token limit)
            historico = []
            fonte = "supabase"
            detalhes_fonte = ""

            if getattr(self.db, 'client', None) is not None:
                # Busca com threshold padrão (0.70 = similaridade mínima de 70%)
                historico = self.db.find_similar_responses(embedding, self.agent_id, limit=5, match_threshold=0.70)
                if not historico:
                    # Se não passou no limiar, relaxa para retornar os mais próximos disponíveis
                    historico = self.db.find_similar_responses(embedding, self.agent_id, limit=5, match_threshold=-1.0)
                    if historico:
                        detalhes_fonte = "(abaixo do limiar de similaridade padrão)"
            else:
                # Supabase não configurado: vai direto para fallback local
                fonte = "local"
                detalhes_fonte = "(Supabase não configurado; usando base local)"

            # 3. Fallback local se Supabase não retornou nada
            if not historico:
                fallback = _local_find_similar(self.encoder_model, frase_usuario, self.agent_id, limit=5)
                if fallback:
                    historico = fallback
                    fonte = "local"
                    if not detalhes_fonte:
                        detalhes_fonte = "(fallback local)"

            # Se nenhuma fonte retornou resultados
            if not historico:
                return (
                    "Nenhum caso similar encontrado. Isso costuma acontecer quando: "
                    "(1) o Supabase não está configurado (.env), "
                    "(2) a base histórica está vazia, ou "
                    "(3) o limiar de similaridade está alto para esse texto."
                )
                
            # 4. Formatar os resultados como texto legível para o agente
            resultado = f"=== CASOS HISTÓRICOS SIMILARES ENCONTRADOS ({fonte}) {detalhes_fonte} ===\n\n"
            for i, caso in enumerate(historico, 1):
                resultado += f"Caso {i} (Similaridade: {caso.get('similarity', 0):.2f}):\n"
                resultado += f"Relato: \"{caso['frase']}\"\n"
                resultado += f"Risco Histórico: {caso['risco']}\n"
                resultado += f"Fatores Identificados: {caso['fator']}\n"
                resultado += "-" * 40 + "\n"

            # 5. Salvar no cache global para o crew gravar no log depois
            _LAST_RAG_RESULTS[self.agent_id] = resultado

            return resultado

        except Exception as e:
            return f"Erro ao acessar base de conhecimento: {str(e)}"


# ===========================================================================
# GlobalSupabaseRAGTool — Ferramenta RAG global (usada pelo Supervisor)
# ===========================================================================

class GlobalSupabaseRAGTool(BaseTool):
    """
    Ferramenta RAG global para o agente Supervisor de Qualidade.

    Diferente da SupabaseRAGTool, esta busca em TODA a base histórica
    (sem filtro por dimensão/agent_id), permitindo ao Supervisor comparar
    a análise de um especialista com casos de qualquer dimensão.

    Retorna até 7 casos similares para dar mais contexto ao Supervisor.
    """
    name: str = "Buscar Todos os Casos"
    description: str = (
        "Útil para encontrar exemplos históricos globais de respostas de usuárias frente a qualquer dimensão, "
        "ajudando a julgar e revisar a classificação de risco por completo. "
        "O input deve ser OBRIGATORIAMENTE uma string contendo o trecho de texto que deseja pesquisar na base."
    )

    # Campos injetados via Pydantic Field (sem agent_id — busca global)
    db: SupabaseDB = Field(default_factory=SupabaseDB, exclude=True)
    encoder_model: Any = Field(default=None, exclude=True)

    def _run(self, query_contexto: str) -> str:
        """
        Executa a busca global por contexto em todas as dimensões de risco.

        Args:
            query_contexto: texto para buscar similares na base inteira.

        Returns:
            String formatada com os casos históricos encontrados globalmente.
        """
        if not self.encoder_model:
            # Lazy loading do modelo de embedding
            self.encoder_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        try:
            # 1. Gerar embedding da query
            embedding = self.encoder_model.encode([query_contexto]).tolist()[0]

            # 2. Tentar buscar no Supabase (agent_id=None → busca global)
            historico = []
            fonte = "supabase"
            detalhes_fonte = ""

            if getattr(self.db, 'client', None) is not None:
                # Busca global com threshold padrão (70%)
                historico = self.db.find_similar_responses(embedding, agent_id=None, limit=7, match_threshold=0.70)
                if not historico:
                    # Relaxa o threshold para retornar os mais próximos disponíveis
                    historico = self.db.find_similar_responses(embedding, agent_id=None, limit=7, match_threshold=-1.0)
                    if historico:
                        detalhes_fonte = "(abaixo do limiar de similaridade padrão)"
            else:
                # Supabase não configurado
                fonte = "local"
                detalhes_fonte = "(Supabase não configurado; usando base local)"

            # 3. Fallback local se Supabase não retornou nada
            if not historico:
                fallback = _local_find_similar(self.encoder_model, query_contexto, agent_id=None, limit=7)
                if fallback:
                    historico = fallback
                    fonte = "local"
                    if not detalhes_fonte:
                        detalhes_fonte = "(fallback local)"

            # Se nenhuma fonte retornou resultados
            if not historico:
                return (
                    "Nenhum caso similar encontrado na base histórica global. Isso pode indicar Supabase não configurado, "
                    "base vazia, ou limiar alto."
                )

            # 4. Formatar resultados como texto legível para o Supervisor
            resultado = f"=== CONTEXTO GERAL DE CASOS HISTÓRICOS ({fonte}) {detalhes_fonte} ===\n\n"
            for i, caso in enumerate(historico, 1):
                resultado += f"Caso {i} (Similaridade: {caso.get('similarity', 0):.2f}):\n"
                resultado += f"Relato: \"{caso['frase']}\"\n"
                resultado += f"Risco Histórico: {caso['risco']}\n"
                resultado += f"Fatores Identificados: {caso['fator']}\n"
                resultado += "-" * 40 + "\n"

            # 5. Salvar no cache global com chave 'global' (para logs)
            _LAST_RAG_RESULTS['global'] = resultado

            return resultado

        except Exception as e:
            return f"Erro ao acessar base de conhecimento global: {str(e)}"

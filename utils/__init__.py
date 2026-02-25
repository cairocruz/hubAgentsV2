"""
utils/ — Pacote de utilitários do sistema.

Exporta:
  - SupabaseRAGTool : ferramenta RAG por dimensão (usada pelos especialistas)
  - SupabaseDB      : wrapper para operações no banco Supabase (RAG + logs)
"""
from .data_loader import SupabaseRAGTool
from .supabase_client import SupabaseDB

__all__ = ['SupabaseRAGTool', 'SupabaseDB']

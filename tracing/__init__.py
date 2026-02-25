"""
tracing/ — Pacote de tracing (rastreamento) de execução dos agentes.

Módulo 100% desacoplado do código dos agentes. Fornece:

  - TracingService    : grava eventos de trace no Supabase
  - create_step_callback / create_task_callback : factories de callbacks
    que podem ser injetados no CrewAI sem alterar a lógica dos agentes
  - TRACING_SQL       : SQL para criar a tabela e views no Supabase

Uso mínimo no código dos agentes (única linha de acoplamento):
    from tracing import create_step_callback, create_task_callback
"""

from .service import TracingService
from .callbacks import create_step_callback, create_task_callback
from .schema import TRACING_SQL

__all__ = [
    "TracingService",
    "create_step_callback",
    "create_task_callback",
    "TRACING_SQL",
]

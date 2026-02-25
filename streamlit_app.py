"""
streamlit_app.py — Dashboard de Tracing e Observabilidade.

Visualização interativa dos eventos capturados pelo módulo tracing/
durante a execução dos agentes. Consulta diretamente o Supabase.

Executar:
    streamlit run streamlit_app.py
"""

import os
import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Conexão com Supabase (lazy, cacheada pelo Streamlit)
# ---------------------------------------------------------------------------

@st.cache_resource
def _get_supabase():
    """Cria o cliente Supabase uma única vez (cacheado pela sessão)."""
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        return None
    from supabase import create_client
    return create_client(url, key)


def query_table(table: str, filters: dict | None = None, order: str | None = None, limit: int = 1000) -> pd.DataFrame:
    """
    Consulta genérica a uma tabela/view do Supabase e retorna DataFrame.

    Args:
        table: nome da tabela ou view.
        filters: dict de {coluna: valor} para filtrar com eq().
        order: coluna para ordenar (ascendente).
        limit: máximo de registros.
    """
    client = _get_supabase()
    if client is None:
        return pd.DataFrame()

    try:
        q = client.table(table).select("*").limit(limit)
        if filters:
            for col, val in filters.items():
                q = q.eq(col, val)
        if order:
            q = q.order(order)
        resp = q.execute()
        if resp.data:
            return pd.DataFrame(resp.data)
    except Exception as e:
        st.error(f"Erro ao consultar `{table}`: {e}")
    return pd.DataFrame()


# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="HubAgents V2 — Tracing Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🔍 HubAgents V2 — Tracing Dashboard")
st.caption("Visualização dos eventos de execução dos agentes de análise de risco.")

# ---------------------------------------------------------------------------
# Verificação de conexão
# ---------------------------------------------------------------------------

client = _get_supabase()
if client is None:
    st.error(
        "⚠️ Supabase não configurado. Defina `SUPABASE_URL` e `SUPABASE_KEY` no arquivo `.env`."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar — Seleção de análise
# ---------------------------------------------------------------------------

st.sidebar.header("Filtros")

# Buscar lista de análises disponíveis (overview)
df_overview = query_table("vw_trace_analysis_overview")

if df_overview.empty:
    st.warning("Nenhum evento de tracing encontrado no banco. Execute uma análise primeiro.")
    st.stop()

# Formatar opções do selectbox
df_overview["label"] = df_overview.apply(
    lambda r: f"{r['analysis_id'][:8]}… | {r.get('total_agents', '?')} agentes | {r.get('total_events', '?')} eventos",
    axis=1,
)

selected_label = st.sidebar.selectbox(
    "Selecione uma análise",
    options=df_overview["label"].tolist(),
    index=0,
)

# Extrair analysis_id selecionado
selected_idx = df_overview["label"].tolist().index(selected_label)
analysis_id = df_overview.iloc[selected_idx]["analysis_id"]

st.sidebar.markdown(f"**Analysis ID:**\n`{analysis_id}`")

# ---------------------------------------------------------------------------
# Tabs principais
# ---------------------------------------------------------------------------

tab_overview, tab_agents, tab_timeline, tab_raw = st.tabs([
    "📊 Visão Geral",
    "🤖 Por Agente",
    "📜 Timeline",
    "🗄️ Dados Brutos",
])

# ============================= TAB: VISÃO GERAL ============================

with tab_overview:
    row = df_overview[df_overview["analysis_id"] == analysis_id].iloc[0]

    # Métricas principais em colunas
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Agentes", int(row.get("total_agents", 0)))
    c2.metric("Eventos", int(row.get("total_events", 0)))
    c3.metric("Steps", int(row.get("total_steps", 0)))
    c4.metric("Tool Calls", int(row.get("total_tool_calls", 0)))

    wall_time = row.get("total_wall_time_seconds")
    if wall_time is not None:
        c5.metric("Tempo Total", f"{float(wall_time):.1f}s")
    else:
        c5.metric("Tempo Total", "—")

    st.divider()

    # Fases executadas
    phases = row.get("phases_executed")
    if phases:
        phase_labels = {"phase1": "Fase 1 — Especialistas", "phase2": "Fase 2 — Supervisor", "phase3": "Fase 3 — Sintetizador"}
        st.subheader("Fases Executadas")
        cols = st.columns(len(phases))
        for i, p in enumerate(phases):
            cols[i].success(phase_labels.get(p, p))

    st.divider()

    # Gráfico de eventos por fase
    df_timeline = query_table("vw_trace_timeline", filters={"analysis_id": analysis_id})
    if not df_timeline.empty and "phase" in df_timeline.columns:
        st.subheader("Eventos por Fase")
        phase_counts = df_timeline["phase"].value_counts().sort_index()
        st.bar_chart(phase_counts)

    # Gráfico de eventos por tipo
    if not df_timeline.empty and "event_type" in df_timeline.columns:
        st.subheader("Eventos por Tipo")
        type_counts = df_timeline["event_type"].value_counts()
        st.bar_chart(type_counts)


# ============================= TAB: POR AGENTE =============================

with tab_agents:
    df_agents = query_table("vw_trace_agent_summary", filters={"analysis_id": analysis_id})

    if df_agents.empty:
        st.info("Sem dados de agentes para esta análise.")
    else:
        st.subheader("Resumo por Agente")

        # Tabela resumo
        display_cols = [
            "agent_role", "phase", "total_steps", "tool_calls",
            "total_tokens", "total_duration_ms", "wall_time_seconds",
        ]
        available = [c for c in display_cols if c in df_agents.columns]
        st.dataframe(
            df_agents[available].rename(columns={
                "agent_role": "Agente",
                "phase": "Fase",
                "total_steps": "Steps",
                "tool_calls": "Tool Calls",
                "total_tokens": "Tokens",
                "total_duration_ms": "Duração (ms)",
                "wall_time_seconds": "Tempo Real (s)",
            }),
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        # Gráfico: steps por agente
        st.subheader("Steps por Agente")
        if "agent_role" in df_agents.columns and "total_steps" in df_agents.columns:
            chart_data = df_agents.set_index("agent_role")["total_steps"]
            st.bar_chart(chart_data)

        # Gráfico: tempo real por agente
        if "wall_time_seconds" in df_agents.columns:
            st.subheader("Tempo Real por Agente (s)")
            time_data = df_agents.set_index("agent_role")["wall_time_seconds"].astype(float)
            st.bar_chart(time_data)

        st.divider()

        # Detalhes individuais
        st.subheader("Detalhes por Agente")
        agent_options = df_agents["agent_role"].tolist()
        selected_agent = st.selectbox("Selecione um agente", agent_options)

        if selected_agent and not df_timeline.empty:
            agent_events = df_timeline[df_timeline["agent_role"] == selected_agent].sort_values("step_number")
            if agent_events.empty:
                st.info("Sem eventos para este agente.")
            else:
                for _, evt in agent_events.iterrows():
                    event_type = evt.get("event_type", "")
                    summary = evt.get("event_summary", event_type)
                    step = evt.get("step_number", "?")

                    # Ícones por tipo de evento
                    icon = {"step_action": "🔧", "step_finish": "✅", "task_complete": "🏁"}.get(event_type, "📌")

                    with st.expander(f"{icon} Step {step} — {summary}", expanded=False):
                        if evt.get("thought"):
                            st.markdown("**Pensamento do agente:**")
                            st.text(evt["thought"])
                        if evt.get("tool_name"):
                            st.markdown(f"**Tool:** `{evt['tool_name']}`")
                        if evt.get("tool_input"):
                            st.markdown("**Input da tool:**")
                            st.code(evt["tool_input"], language="text")
                        if evt.get("tool_result_preview"):
                            st.markdown("**Resultado da tool (preview):**")
                            st.code(evt["tool_result_preview"], language="text")
                        if evt.get("output_preview"):
                            st.markdown("**Output:**")
                            st.code(evt["output_preview"], language="text")
                        if evt.get("duration_ms"):
                            st.caption(f"⏱️ {float(evt['duration_ms']):.0f}ms")


# ============================= TAB: TIMELINE ===============================

with tab_timeline:
    if df_timeline.empty:
        st.info("Sem eventos na timeline para esta análise.")
    else:
        st.subheader("Timeline Completa")

        # Filtro por fase
        phases_available = sorted(df_timeline["phase"].dropna().unique().tolist())
        selected_phases = st.multiselect("Filtrar por fase", phases_available, default=phases_available)
        filtered = df_timeline[df_timeline["phase"].isin(selected_phases)]

        # Filtro por tipo de evento
        types_available = sorted(filtered["event_type"].dropna().unique().tolist())
        selected_types = st.multiselect("Filtrar por tipo de evento", types_available, default=types_available)
        filtered = filtered[filtered["event_type"].isin(selected_types)]

        st.caption(f"Exibindo {len(filtered)} de {len(df_timeline)} eventos.")

        # Tabela interativa
        show_cols = [
            "step_number", "phase", "iteration", "agent_role",
            "event_type", "event_summary", "tool_name",
            "output_preview", "duration_ms", "created_at",
        ]
        available = [c for c in show_cols if c in filtered.columns]
        st.dataframe(
            filtered[available].rename(columns={
                "step_number": "#",
                "phase": "Fase",
                "iteration": "Iter",
                "agent_role": "Agente",
                "event_type": "Tipo",
                "event_summary": "Resumo",
                "tool_name": "Tool",
                "output_preview": "Output (preview)",
                "duration_ms": "ms",
                "created_at": "Timestamp",
            }),
            use_container_width=True,
            hide_index=True,
            height=600,
        )


# ============================= TAB: DADOS BRUTOS ==========================

with tab_raw:
    st.subheader("Dados Brutos — agent_trace_events")
    st.caption("Registros completos sem truncamento de views.")

    df_raw = query_table("agent_trace_events", filters={"analysis_id": analysis_id})

    if df_raw.empty:
        st.info("Sem dados brutos para esta análise.")
    else:
        st.dataframe(df_raw, use_container_width=True, hide_index=True, height=600)

        # Download CSV
        csv_data = df_raw.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Baixar CSV",
            data=csv_data,
            file_name=f"trace_{analysis_id[:8]}.csv",
            mime="text/csv",
        )


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.sidebar.divider()
st.sidebar.caption("HubAgents V2 — Tracing Dashboard")
st.sidebar.caption(f"Supabase: ✅ Conectado")

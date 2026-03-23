"""
streamlit_app.py — Dashboard de Tracing e Observabilidade.

Visualização interativa dos eventos capturados pelo módulo tracing/
durante a execução dos agentes. Consulta diretamente o Supabase.

Executar:
    streamlit run streamlit_app.py
"""

import os
import json
import io
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
    """Cria o cliente Supabase uma única vez (cacheado pela sessão).

    Prioridade das credenciais, em ordem:
      1. Variáveis de ambiente (SUPABASE_URL, SUPABASE_KEY) — usadas no deploy local/Cloud Run.
      2. st.secrets (quando rodando no Streamlit Cloud).
    """
    # 1) Tenta pegar das variáveis de ambiente (local, Cloud Run, etc.)
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")

    # 2) Se não veio nada, tenta buscar em st.secrets (Streamlit Cloud)
    if (not url or not key) and hasattr(st, "secrets"):
        if "SUPABASE_URL" in st.secrets:
            url = url or st.secrets["SUPABASE_URL"]
        if "SUPABASE_KEY" in st.secrets:
            key = key or st.secrets["SUPABASE_KEY"]

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
    page_title="Visualização de Dados",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("� Visualização de Dados")
st.caption("Resultados de análise e eventos de execução dos agentes.")

# ---------------------------------------------------------------------------
# Verificação de conexão
# ---------------------------------------------------------------------------

client = _get_supabase()
if client is None:
    st.error(
        "⚠️ Supabase não configurado. Defina `SUPABASE_URL` e `SUPABASE_KEY` no `.env` (local) "
        "ou em `Secrets` / variáveis de ambiente da plataforma de deploy."
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

tab_results, tab_rework, tab_overview, tab_agents, tab_timeline, tab_raw = st.tabs([
    "📋 Resultados da Análise",
    "🔄 Histórico de Retrabalho",
    "📊 Visão Geral (Tracing)",
    "🤖 Por Agente (Tracing)",
    "📜 Timeline",
    "🗄️ Dados Brutos",
])

# ============================= TAB: RESULTADOS DA ANÁLISE ==================

def _color_risk(level: str) -> str:
    """Retorna emoji + cor para o nível de risco."""
    mapping = {
        "BAIXO": "🟢 BAIXO",
        "MODERADO": "🟡 MODERADO",
        "ALTO": "🟠 ALTO",
        "CRÍTICO": "🔴 CRÍTICO",
    }
    return mapping.get(str(level).upper(), level)


def _color_status(status: str) -> str:
    """Emoji para status do supervisor."""
    if str(status).upper() == "APROVADO":
        return "✅ APROVADO"
    return "❌ REPROVADO"


with tab_results:
    # --- Dados dos especialistas (agent_individual_logs) ---
    df_individual = query_table(
        "agent_individual_logs",
        filters={"analysis_id": analysis_id},
        order="agent_id",
    )

    # --- Resultado final (agent_logs) ---
    df_final = query_table(
        "agent_logs",
        filters={"analysis_id": analysis_id},
    )

    if df_individual.empty and df_final.empty:
        st.warning("Nenhum resultado de análise encontrado para este analysis_id. "
                   "Verifique se a análise foi concluída com sucesso.")
    else:
        # ---- RESULTADO FINAL (SINTETIZADOR) ----
        if not df_final.empty:
            st.subheader("🏁 Resultado Final Consolidado")

            # Tentar parsear o analysis_result (JSON string)
            final_row = df_final.iloc[0]
            final_result = {}
            raw_result = final_row.get("analysis_result", "{}")
            if isinstance(raw_result, str):
                try:
                    final_result = json.loads(raw_result)
                except json.JSONDecodeError:
                    final_result = {"raw": raw_result}
            elif isinstance(raw_result, dict):
                final_result = raw_result

            risk_score = final_result.get("risk_score", "—")
            risk_level = final_result.get("risk_level", "—")

            # Métricas principais
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Score de Risco", f"{risk_score}/100")
            mc2.metric("Nível de Risco", _color_risk(str(risk_level)))
            mc3.metric("Analysis ID", analysis_id[:12] + "…")

            st.divider()

            # Fatores de risco consolidados
            factors = final_result.get("consolidated_factors", [])
            if factors:
                st.subheader("⚠️ Fatores de Risco Consolidados")
                for i, f in enumerate(factors, 1):
                    if isinstance(f, dict):
                        st.markdown(f"**{i}.** {f.get('factor', f.get('fator', str(f)))}")
                        if f.get("severity") or f.get("gravidade"):
                            st.caption(f"   Gravidade: {f.get('severity', f.get('gravidade', ''))}")
                        if f.get("description") or f.get("descricao"):
                            st.caption(f"   {f.get('description', f.get('descricao', ''))}")
                    else:
                        st.markdown(f"**{i}.** {f}")

            # Recomendações
            recs = final_result.get("recommendations", final_result.get("recomendacoes", []))
            if recs:
                st.subheader("💡 Recomendações")
                for i, r in enumerate(recs, 1):
                    st.markdown(f"{i}. {r}")

            st.divider()

        # ---- ANÁLISES POR ESPECIALISTA ----
        if not df_individual.empty:
            st.subheader("🤖 Análises por Especialista")

            # Tabela resumo
            summary_cols = [
                "agent_id", "agent_domain", "score_risco",
                "supervisor_status", "rework_count",
            ]
            available_cols = [c for c in summary_cols if c in df_individual.columns]
            df_summary = df_individual[available_cols].copy()
            df_summary = df_summary.rename(columns={
                "agent_id": "Agente",
                "agent_domain": "Domínio",
                "score_risco": "Score (0-100)",
                "supervisor_status": "Status Supervisor",
                "rework_count": "Retrabalhos",
            })
            st.dataframe(df_summary, width="stretch", hide_index=True)

            # Gráfico de barras: score por especialista
            if "score_risco" in df_individual.columns and "agent_domain" in df_individual.columns:
                st.subheader("📊 Score de Risco por Domínio")
                chart_df = df_individual.set_index("agent_domain")["score_risco"].dropna()
                if not chart_df.empty:
                    st.bar_chart(chart_df)

            st.divider()

            # Detalhes expandíveis por especialista
            st.subheader("🔎 Detalhes por Especialista")
            for _, row_spec in df_individual.iterrows():
                aid = row_spec.get("agent_id", "?")
                domain = row_spec.get("agent_domain", "")
                score = row_spec.get("score_risco", "—")
                status = row_spec.get("supervisor_status", "")
                status_icon = _color_status(status)

                with st.expander(f"Especialista {aid} — {domain} | Score: {score} | {status_icon}", expanded=False):
                    st.markdown(f"**Pergunta:** {row_spec.get('question', '—')}")
                    st.markdown(f"**Resposta da usuária:** {row_spec.get('user_response', '—')}")
                    st.markdown(f"**Score:** {score}/100")
                    st.markdown(f"**Status:** {status_icon}")
                    st.markdown(f"**Retrabalhos:** {row_spec.get('rework_count', 0)}")

                    justif = row_spec.get("justificativa", "")
                    if justif:
                        st.markdown("**Justificativa:**")
                        st.info(justif)

                    sup_fb = row_spec.get("supervisor_feedback", "")
                    if sup_fb:
                        st.markdown("**Feedback do Supervisor:**")
                        st.warning(sup_fb)

                    rag = row_spec.get("rag_results", "")
                    if rag:
                        st.markdown("**Casos Similares (RAG):**")
                        st.code(rag, language="text")

                    raw = row_spec.get("raw_output", "")
                    if raw:
                        st.markdown("**Saída Bruta Completa:**")
                        st.code(raw, language="text")

        # ---- DOWNLOADS ----
        st.divider()
        st.subheader("📥 Exportar Resultados")

        dl1, dl2, dl3, dl4 = st.columns(4)

        # CSV dos especialistas
        if not df_individual.empty:
            csv_spec = df_individual.to_csv(index=False).encode("utf-8")
            dl1.download_button(
                "📥 Especialistas (CSV)",
                data=csv_spec,
                file_name=f"especialistas_{analysis_id[:8]}.csv",
                mime="text/csv",
            )

            # Excel dos especialistas
            buf_spec = io.BytesIO()
            df_individual.to_excel(buf_spec, index=False, sheet_name="Especialistas")
            dl2.download_button(
                "📥 Especialistas (Excel)",
                data=buf_spec.getvalue(),
                file_name=f"especialistas_{analysis_id[:8]}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        # JSON do resultado final
        if not df_final.empty:
            json_final = json.dumps(final_result, ensure_ascii=False, indent=2)
            dl3.download_button(
                "📥 Resultado Final (JSON)",
                data=json_final.encode("utf-8"),
                file_name=f"resultado_final_{analysis_id[:8]}.json",
                mime="application/json",
            )

        # Tudo junto em Excel (múltiplas abas)
        if not df_individual.empty or not df_final.empty:
            buf_all = io.BytesIO()
            with pd.ExcelWriter(buf_all, engine="openpyxl") as writer:
                if not df_individual.empty:
                    df_individual.to_excel(writer, index=False, sheet_name="Especialistas")
                if not df_final.empty:
                    df_final.to_excel(writer, index=False, sheet_name="Resultado Final")
                # Rework history
                df_rw = query_table(
                    "agent_rework_history",
                    filters={"analysis_id": analysis_id},
                    order="agent_id",
                )
                if not df_rw.empty:
                    df_rw.to_excel(writer, index=False, sheet_name="Retrabalhos")
            dl4.download_button(
                "📥 Tudo (Excel)",
                data=buf_all.getvalue(),
                file_name=f"analise_completa_{analysis_id[:8]}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )


# ============================= TAB: HISTÓRICO DE RETRABALHO ================

with tab_rework:
    df_rework = query_table(
        "agent_rework_history",
        filters={"analysis_id": analysis_id},
        order="agent_id",
    )

    if df_rework.empty:
        st.info("Nenhum retrabalho registrado para esta análise. "
                "Todos os especialistas foram aprovados na primeira tentativa, "
                "ou a análise ainda não possui registros de rework.")
    else:
        st.subheader("🔄 Histórico de Retrabalho")
        st.caption("Registros das análises reprovadas pelo Supervisor e refeitas pelos especialistas.")

        # Métricas
        total_reworks = len(df_rework)
        agents_reworked = df_rework["agent_id"].nunique() if "agent_id" in df_rework.columns else 0
        rc1, rc2 = st.columns(2)
        rc1.metric("Total de Retrabalhos", total_reworks)
        rc2.metric("Agentes Retrabalhados", agents_reworked)

        st.divider()

        # Tabela resumo
        rw_cols = [
            "agent_id", "agent_domain", "iteration",
            "original_score_risco", "supervisor_feedback",
        ]
        available_rw = [c for c in rw_cols if c in df_rework.columns]
        st.dataframe(
            df_rework[available_rw].rename(columns={
                "agent_id": "Agente",
                "agent_domain": "Domínio",
                "iteration": "Rodada",
                "original_score_risco": "Score Original",
                "supervisor_feedback": "Feedback do Supervisor",
            }),
            width="stretch",
            hide_index=True,
        )

        st.divider()

        # Detalhes expandíveis
        for _, rw_row in df_rework.iterrows():
            aid = rw_row.get("agent_id", "?")
            domain = rw_row.get("agent_domain", "")
            iteration = rw_row.get("iteration", "?")

            with st.expander(f"Especialista {aid} — {domain} | Rodada {iteration}", expanded=False):
                st.markdown(f"**Score Original:** {rw_row.get('original_score_risco', '—')}")

                orig_just = rw_row.get("original_justificativa", "")
                if orig_just:
                    st.markdown("**Justificativa Original:**")
                    st.info(orig_just)

                sup_fb = rw_row.get("supervisor_feedback", "")
                if sup_fb:
                    st.markdown("**Feedback do Supervisor:**")
                    st.warning(sup_fb)

                orig_raw = rw_row.get("original_raw_output", "")
                if orig_raw:
                    st.markdown("**Saída Bruta Original (reprovada):**")
                    st.code(orig_raw, language="text")

        # Download
        st.divider()
        csv_rw = df_rework.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Baixar Retrabalhos (CSV)",
            data=csv_rw,
            file_name=f"retrabalhos_{analysis_id[:8]}.csv",
            mime="text/csv",
        )


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
            width="stretch",
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
            width="stretch",
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
        st.dataframe(df_raw, width="stretch", hide_index=True, height=600)

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
st.sidebar.caption("Visualização de Dados")
st.sidebar.caption(f"Supabase: ✅ Conectado")

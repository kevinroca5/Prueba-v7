import statistics

import streamlit as st

from common import (
    CAT_BY_KEY, CAT_LABELS, CAT_ORDER, METRICS, fmt_value, value_to_rank,
    compute_league_benchmarks, render_team_picker_and_updater,
    render_match_selection_sidebar, render_metric_filter_panel,
)

st.set_page_config(page_title="Análisis Rival — LaLiga", layout="wide", page_icon="🔴")

st.title("🔴 Análisis Rival")
st.caption("Fortalezas y debilidades automáticas de un equipo frente a la media de LaLiga, "
           "a partir de los partidos que selecciones.")

team_name, matches, has_coach_column = render_team_picker_and_updater(key_prefix="rival")
league_benchmarks = compute_league_benchmarks()

selected_matches, total_matches = render_match_selection_sidebar(team_name, matches, key_prefix="rival")
if not selected_matches:
    st.warning("No hay partidos seleccionados con estos filtros.")
    st.stop()

st.caption(f"**{len(selected_matches)}** partidos seleccionados de **{total_matches}** disponibles en el CSV.")

with st.expander("Ver partidos seleccionados"):
    import pandas as pd
    tbl = pd.DataFrame([{
        "Fecha": m["date"].split(" ")[0] if m["date"] else "?",
        "Rival": m["opponent"], "Local/Visit.": "Local" if m["home"] else "Visitante",
        "Resultado": m["resultLabel"], "Entrenador": m.get("coach") or "—",
    } for m in selected_matches])
    st.dataframe(tbl, use_container_width=True, hide_index=True)

st.divider()

# ---------------------------------------------------------------------------
# Filtros por métrica (Ofensivas / Defensivas / General / Posesión)
# ---------------------------------------------------------------------------
st.subheader("🎚️ Filtrar partidos por métrica")
st.caption("Además de fecha/local-visitante/entrenador (barra lateral), puedes acotar por "
           "rango de valores dentro de cada categoría. Ej.: solo partidos con posesión en "
           "campo rival por encima de cierto umbral.")
selected_matches = render_metric_filter_panel(selected_matches, key_prefix="rival")

if not selected_matches:
    st.warning("Ningún partido cumple estos rangos de filtro.")
    st.stop()

st.caption(f"**{len(selected_matches)}** partidos cumplen todos los filtros.")

st.divider()


def avg_metric(key):
    vals = [m["metrics"].get(key) for m in selected_matches if m["metrics"].get(key) is not None]
    return statistics.mean(vals) if vals else None


# ---------------------------------------------------------------------------
# Informe general — headline: posesión y estilo, NO goles a favor/en contra
# ---------------------------------------------------------------------------
st.header(f"📋 Informe general del rival — {team_name}")
st.caption("Lo que más dice sobre cómo juega este rival en los partidos seleccionados.")

wins = sum(1 for m in selected_matches if m["outcome"] == "W")
draws = sum(1 for m in selected_matches if m["outcome"] == "D")
losses = sum(1 for m in selected_matches if m["outcome"] == "L")
st.caption(f"Récord en los partidos seleccionados: {wins}V - {draws}E - {losses}D "
           f"(el marcador se muestra como contexto, no como métrica principal del informe).")

HEADLINE_KEYS = ["poss_campo_rival", "poss_campo_defensivo", "presiones_altas_p90",
                  "keypassp90", "crosses", "v1v1_p90"]
headline_cols = st.columns(len(HEADLINE_KEYS))
for i, key in enumerate(HEADLINE_KEYS):
    meta = CAT_BY_KEY[key]
    headline_cols[i].metric(meta["label"], fmt_value(avg_metric(key), meta))

with st.expander("Ver todas las métricas de la categoría General (incluye goles y puntos)"):
    general_metrics = [m for m in METRICS if m[3] == "general"]
    gcols = st.columns(4)
    for i, (key, col, label, cat, is_pct) in enumerate(general_metrics):
        meta = CAT_BY_KEY[key]
        gcols[i % 4].metric(label, fmt_value(avg_metric(key), meta))

st.divider()

# ---------------------------------------------------------------------------
# Fortalezas y debilidades automáticas (vs media de LaLiga, con percentil/ranking)
# ---------------------------------------------------------------------------
st.subheader("🔎 Fortalezas y debilidades automáticas (vs. media de LaLiga)")
st.caption("Se calculan sobre las métricas de los partidos seleccionados que tienen un "
           f"equivalente directo a nivel de equipo en LaLiga 24/25 ({len(league_benchmarks)} "
           f"de {len(METRICS)} métricas).")

standouts = []
for key, bench in league_benchmarks.items():
    val = avg_metric(key)
    if val is None:
        continue
    z = (val - bench["mean"]) / bench["std"]
    rank, n, percentile = value_to_rank(val, bench["values"])
    standouts.append({"key": key, "value": val, "z": z, "rank": rank, "n": n,
                       "percentile": percentile, "meta": CAT_BY_KEY[key]})
standouts.sort(key=lambda s: -abs(s["z"]))

strengths = [s for s in standouts if s["z"] >= 0.5][:8]
weaknesses = [s for s in standouts if s["z"] <= -0.5][:8]

col_str, col_weak = st.columns(2)
with col_str:
    st.markdown("**🟢 Fortalezas** (por encima de la media de LaLiga)")
    if not strengths:
        st.write("Nada destaca claramente por encima de la media en este tramo de partidos.")
    for s in strengths:
        st.write(f"• **{s['meta']['label']}**: {fmt_value(s['value'], s['meta'])} — "
                 f"percentil {s['percentile']} · equivaldría al {s['rank']}º de {s['n']} en LaLiga")
with col_weak:
    st.markdown("**🔴 Debilidades** (por debajo de la media de LaLiga)")
    if not weaknesses:
        st.write("Nada destaca claramente por debajo de la media en este tramo de partidos.")
    for s in weaknesses:
        st.write(f"• **{s['meta']['label']}**: {fmt_value(s['value'], s['meta'])} — "
                 f"percentil {s['percentile']} · equivaldría al {s['rank']}º de {s['n']} en LaLiga")

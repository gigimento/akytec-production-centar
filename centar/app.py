import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from config import (
    OEE_TARGET, AVAIL_TARGET, PERF_TARGET, QUAL_TARGET,
    REFRESH_OPTIONS, DEFAULT_REFRESH, MACHINES, M1, M2
)
from lib.db import run_query, test_connection
from lib.queries import (
    DAILY_OEE, WEEKLY_OEE, STOP_HISTORY,
    ALL_QUERIES
)

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="akYtec SMT Production Centar",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    * { box-sizing: border-box; }
    .stApp {
        background: #0A0F1D;
        color: #CBD5E1;
        font-family: 'Outfit', sans-serif;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stSidebar"] {
        background: rgba(10,15,29,0.98) !important;
        border-right: 1px solid rgba(0,229,255,0.08);
    }
    .kpi-card {
        background: rgba(15,23,42,0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0,229,255,0.06);
        border-radius: 12px;
        padding: 20px;
        position: relative;
        overflow: hidden;
    }
    .kpi-card .accent { position: absolute; left: 0; top: 0; width: 4px; height: 100%; }
    .kpi-label { font-size: 11px; color: #64748B; text-transform: uppercase; letter-spacing: 0.12em; font-family: 'JetBrains Mono', monospace; margin-bottom: 6px; }
    .kpi-value { font-size: 42px; font-weight: 700; font-family: 'JetBrains Mono', monospace; line-height: 1; }
    .kpi-sub { font-size: 12px; color: #64748B; margin-top: 6px; }
    .kpi-rag { font-size: 11px; font-family: 'JetBrains Mono', monospace; margin-top: 8px; }
    .kpi-bar { height: 4px; background: #1B3756; border-radius: 2px; margin-top: 12px; }
    .kpi-bar-fill { height: 100%; border-radius: 2px; transition: width 0.5s; }
    .section-title {
        font-size: 11px; color: #64748B; text-transform: uppercase;
        letter-spacing: 0.12em; font-family: 'JetBrains Mono', monospace;
        margin-bottom: 14px; display: flex; align-items: center; gap: 8px;
    }
    .sql-block {
        background: #050B12; border: 1px solid #1B3756; border-radius: 6px;
        padding: 14px; font-family: 'JetBrains Mono', monospace; font-size: 11px;
        color: #7FB8D4; white-space: pre; overflow-x: auto; line-height: 1.75;
    }
    .stop-row { border-bottom: 1px solid #0C1C30; }
    .badge {
        padding: 2px 10px; border-radius: 4px; font-size: 10px;
        font-family: 'JetBrains Mono', monospace;
    }
</style>
""", unsafe_allow_html=True)


# ── HELPERS ──
def rag_status(value, target=85.0):
    if value >= target:
        return "#22C55E", "✓ OK"
    elif value >= target - 5:
        return "#F5A623", "⚠ WARN"
    else:
        return "#F87171", "✗ ALERT"


def format_time(seconds):
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m}m {s}s"


# ── SIDEBAR ──
with st.sidebar:
    st.markdown("### ⚡ akYtec")

    page = st.radio(
        "Navigacija",
        ["📊 Dashboard", "🗄️ SQL Library", "🧠 AI RCA", "🧮 KPI Calculator", "⚠️ Downtime"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    auto_refresh = st.checkbox("Auto-refresh", value=True)
    refresh_interval = st.select_slider(
        "Interval (sek)", options=REFRESH_OPTIONS, value=DEFAULT_REFRESH,
        format_func=lambda x: f"{x//1000}s"
    )

    st.markdown("---")
    db_ok = test_connection()
    if db_ok:
        st.markdown("🟢 **Database** povezan")
    else:
        st.markdown("🔴 **Database** nedostupan")

    st.markdown(f"🕐 {datetime.now().strftime('%H:%M:%S')}")


# ── DASHBOARD ──
if page == "📊 Dashboard":
    st.markdown("""
    <div style="display:flex; align-items:center; justify-content:center; gap:16px; margin-bottom:20px;">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 125 100" width="60" height="48">
            <path d="M 0 0 L 25 0 L 75 50 L 25 100 L 0 100 L 0 75 L 25 75 L 50 50 L 25 25 L 0 25 Z" fill="#00a69c"/>
            <path d="M 67.5 32.5 L 80 45 L 100 25 L 125 25 L 125 0 L 100 0 Z" fill="#e6007e"/>
        </svg>
        <div>
            <div style="font-family:'Outfit',sans-serif; font-size:28px; font-weight:700; color:#00a69c;">akYtec SMT Production Centar</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:12px; color:#64748B;">LINE_1 · MACHINE_1 + MACHINE_2 · """ + datetime.now().strftime('%d.%m.%Y') + """</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fetch data
    df_daily = run_query(DAILY_OEE)
    df_weekly = run_query(WEEKLY_OEE)
    df_stops = run_query(STOP_HISTORY)

    # ── KPI CARDS ──
    st.markdown('<div class="section-title">📈 OEE DANAŠNJI DAN</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    # Calculate KPIs from daily data
    if not df_daily.empty:
        m1_data = df_daily[df_daily["MachineNm"] == M1]
        m2_data = df_daily[df_daily["MachineNm"] == M2]

        m1_oee = m1_data["OEE"].mean() * 100 if not m1_data.empty else 0
        m2_oee = m2_data["OEE"].mean() * 100 if not m2_data.empty else 0
        m1_avail = m1_data["Availability"].mean() * 100 if not m1_data.empty else 0
        m2_avail = m2_data["Availability"].mean() * 100 if not m2_data.empty else 0
        m1_perf = m1_data["Performance"].mean() * 100 if not m1_data.empty else 0
        m2_perf = m2_data["Performance"].mean() * 100 if not m2_data.empty else 0
    else:
        m1_oee = m2_oee = m1_avail = m2_avail = m1_perf = m2_perf = 0

    # Weekly averages
    if not df_weekly.empty:
        m1_avg = df_weekly[df_weekly["MachineNm"] == M1]["OEE"].mean() * 100
        m2_avg = df_weekly[df_weekly["MachineNm"] == M2]["OEE"].mean() * 100
    else:
        m1_avg = m2_avg = 0

    kpis = [
        ("MACHINE_1 — OEE danas", m1_oee, f"Avail {m1_avail:.0f}% · Perf {m1_perf:.0f}%"),
        ("MACHINE_2 — OEE danas", m2_oee, f"Avail {m2_avail:.0f}% · Perf {m2_perf:.0f}%"),
        ("M1 — Prosek (7d)", m1_avg, "7-dnevni prosek"),
        ("M2 — Prosek (7d)", m2_avg, "7-dnevni prosek"),
    ]

    for i, (label, value, sub) in enumerate(kpis):
        with [col1, col2, col3, col4][i]:
            color, rag_text = rag_status(value)
            st.markdown(f"""
            <div class="kpi-card">
                <div class="accent" style="background: {color};"></div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-value" style="color: {color};">{value:.1f}%</div>
                <div class="kpi-sub">{sub}</div>
                <div class="kpi-rag" style="color: {color};">{rag_text}</div>
                <div class="kpi-bar">
                    <div class="kpi-bar-fill" style="width: {min(value, 100):.0f}%; background: {color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # ── CHARTS ──
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown('<div class="section-title">📈 OEE TREND — OVA NEDELJA</div>', unsafe_allow_html=True)
        if not df_weekly.empty:
            fig = go.Figure()
            for machine, color, label in [(M1, "#00E5FF", "MACHINE_1"), (M2, "#F5A623", "MACHINE_2")]:
                m_data = df_weekly[df_weekly["MachineNm"] == machine]
                if not m_data.empty:
                    fig.add_trace(go.Scatter(
                        x=m_data["WorkDate"], y=m_data["OEE"] * 100,
                        name=label,
                        line=dict(color=color, width=2),
                        mode="lines+markers",
                        marker=dict(size=6),
                    ))
            fig.add_hline(y=85, line_dash="dash", line_color="#22C55E",
                          annotation_text="Target 85%", annotation_position="right")
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="JetBrains Mono", color="#CBD5E1"),
                xaxis=dict(gridcolor="#1B3756"), yaxis=dict(gridcolor="#1B3756", range=[70, 100]),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=0, r=0, t=30, b=0), height=300,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nema podataka za ovu nedelju.")

    with chart_col2:
        st.markdown('<div class="section-title">⚡ AVAILABILITY — S2 vs L2</div>', unsafe_allow_html=True)
        if not df_weekly.empty:
            fig2 = go.Figure()
            for machine, color, label in [(M1, "#00E5FF", "MACHINE_1"), (M2, "#F5A623", "MACHINE_2")]:
                m_data = df_weekly[df_weekly["MachineNm"] == machine]
                if not m_data.empty:
                    fig2.add_trace(go.Bar(
                        x=m_data["WorkDate"], y=m_data["Availability"] * 100,
                        name=label,
                        marker_color=color, opacity=0.85,
                    ))
            fig2.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="JetBrains Mono", color="#CBD5E1"),
                xaxis=dict(gridcolor="#1B3756"), yaxis=dict(gridcolor="#1B3756", range=[80, 100]),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=0, r=0, t=30, b=0), height=300, barmode="group",
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Nema podataka za ovu nedelju.")

    # ── STOP HISTORY ──
    st.markdown('<div class="section-title">⚠️ TOP STOP EVENTI — POSLEDNJIH 7 DANA</div>', unsafe_allow_html=True)
    if not df_stops.empty:
        st.dataframe(
            df_stops.style.applymap(
                lambda v: f"color: {'#F87171' if v > 600 else '#F5A623' if v > 300 else '#22C55E'}",
                subset=["DURATION_SEC"]
            ).format({"DURATION_SEC": format_time}),
            use_container_width=True,
            height=350,
        )
    else:
        st.info("Nema stop eventa za ovu nedelju.")


# ── SQL LIBRARY ──
elif page == "🗄️ SQL Library":
    st.markdown("# 🗄️ SQL Library")
    st.markdown("Klikni za proširivanje · Kopiraj → SQL client")

    colors = {"OEE": "#00E5FF", "Downtime": "#F87171", "Feeders": "#F5A623", "Placements": "#22C55E", "MSL": "#A78BFA"}

    for cat, queries in ALL_QUERIES.items():
        st.markdown(f'<div class="section-title"><span style="width:8px;height:8px;border-radius:50%;background:{colors.get(cat, "#00E5FF")};display:inline-block;"></span>{cat.upper()}</div>', unsafe_allow_html=True)
        for q in queries:
            with st.expander(q["title"]):
                st.code(q["sql"], language="sql")
                if st.button("📋 Kopiraj", key=f"copy_{cat}_{q['title']}"):
                    st.toast("Kopirano!", icon="✅")


# ── AI RCA ──
elif page == "🧠 AI RCA":
    st.markdown("# 🧠 AI RCA — Root Cause Analysis")
    st.markdown("Claude analizira grešku i generiše rankirane hipoteze + akcije P1/P2/P3")

    col_form, col_output = st.columns([1, 1])

    with col_form:
        st.markdown('<div class="section-title">📝 PARAMETRI GREŠKE</div>', unsafe_allow_html=True)
        machine = st.selectbox("Mašina", MACHINES)
        error_code = st.text_input("Kod greške", placeholder="E-4211")
        duration = st.number_input("Trajanje (min)", min_value=1, value=15)
        description = st.text_area(
            "Opis greške / simptomi",
            placeholder="Npr: Feeder na slotu 23 pravi pickup error svaka 3-4 ciklusa...",
            height=120,
        )

        if st.button("⚡ Generiši AI RCA", type="primary"):
            if not error_code and not description:
                st.warning("Unesi bar kod greške ili opis.")
            else:
                from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
                if not ANTHROPIC_API_KEY:
                    st.error("ANTHROPIC_API_KEY nije podešen.")
                else:
                    import requests
                    with st.spinner("Analiziram grešku..."):
                        try:
                            resp = requests.post(
                                "https://api.anthropic.com/v1/messages",
                                headers={
                                    "Content-Type": "application/json",
                                    "x-api-key": ANTHROPIC_API_KEY,
                                    "anthropic-version": "2023-06-01",
                                },
                                json={
                                    "model": CLAUDE_MODEL,
                                    "max_tokens": 1500,
                                    "system": """Ti si iskusni SMT process inženjer na proizvodnoj liniji (MACHINE_1 i MACHINE_2).
Generiši strukturiranu RCA analizu ISKLJUČIVO na srpskom jeziku (ekavica, NIKAD ijekavica).

Koristi tačan format:

SITUACIJA: [mašina] — [opis]
METRIKE: Trajanje: [X] min | Kod: [kod] | Uticaj: [procena]

HIPOTEZE (rankirane po verovatnoći):
1. [Uzrok] — [XX%] — Proveri: [konkretna akcija + DB view]
2. [Uzrok] — [XX%] — Proveri: [konkretna akcija + DB view]
3. [Uzrok] — [XX%] — Proveri: [konkretna akcija + DB view]

HITNE AKCIJE:
P1 (odmah): [Konkretna fizička akcija]
P2 (danas): [SQL istraga — navedi tačan view]
P3 (ova nedelja): [Preventivna/korektivna mera]

PREPORUČENI SQL QUERIES:
- [Tačan naziv view-a i ključne kolone za istragu]

Budi konkretan, kvantativan i akcioni. Referencuj SQL viewove.""",
                                    "messages": [{
                                        "role": "user",
                                        "content": f"Mašina: {machine}\nKod greške: {error_code or '(nije naveden)'}\nTrajanje: {duration} min\nOpis: {description or '(nije naveden)'}",
                                    }],
                                },
                                timeout=30,
                            )
                            data = resp.json()
                            output = data.get("content", [{}])[0].get("text", "Greška pri generisanju.")
                            st.session_state["rca_output"] = output
                        except Exception as e:
                            st.error(f"API greška: {e}")

    with col_output:
        st.markdown('<div class="section-title">📋 RCA ANALIZA — OUTPUT</div>', unsafe_allow_html=True)
        if "rca_output" in st.session_state:
            st.markdown(f'<div class="sql-block">{st.session_state["rca_output"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center; padding:80px 0; color:#1B3756;">
                <div style="font-size:48px; margin-bottom:16px;">🔍</div>
                <div style="font-size:14px; line-height:1.8;">Popuni formu i klikni<br/><strong style="color:#00E5FF;">Generiši AI RCA</strong></div>
            </div>
            """, unsafe_allow_html=True)


# ── KPI CALCULATOR ──
elif page == "🧮 KPI Calculator":
    st.markdown("# 🧮 KPI Calculator")
    st.markdown("Unesi podatke → izračunaj OEE sa RAG statusom")

    calc_col1, calc_col2 = st.columns([1, 1])

    with calc_col1:
        st.markdown('<div class="section-title">📝 UNESI PODATKE</div>', unsafe_allow_html=True)
        planned = st.number_input("Planirano vreme (min)", value=480, step=10)
        downtime = st.number_input("Downtime (min)", value=32, step=1)
        actual_uph = st.number_input("Stvarni UPH", value=2800, step=50)
        theo_uph = st.number_input("Teoretski max UPH", value=3200, step=50)
        good = st.number_input("Dobre ploče (kom)", value=4850, step=10)
        total = st.number_input("Ukupno ploča (kom)", value=4890, step=10)

        st.markdown("---")
        st.markdown("**Formule:**")
        st.code("""
OEE = A × P × Q
A = (Planned − Down) / Planned
P = ActualUPH / TheoUPH
Q = Good / Total
        """, language="text")

    with calc_col2:
        st.markdown('<div class="section-title">📊 REZULTATI — RAG STATUS</div>', unsafe_allow_html=True)

        avail = ((planned - downtime) / planned * 100) if planned else 0
        perf = (actual_uph / theo_uph * 100) if theo_uph else 0
        qual = (good / total * 100) if total else 0
        oee = (avail * perf * qual / 10000) if (planned and theo_uph and total) else 0

        results = [
            ("Availability", avail, AVAIL_TARGET, f"({planned}−{downtime})/{planned}×100"),
            ("Performance", perf, PERF_TARGET, f"{actual_uph}/{theo_uph}×100"),
            ("Quality", qual, QUAL_TARGET, f"{good}/{total}×100"),
            ("OEE", oee, OEE_TARGET, "A × P × Q"),
        ]

        for label, value, target, desc in results:
            color, rag_text = rag_status(value, target)
            delta = value - target
            delta_symbol = "▲" if delta >= 0 else "▼"
            big_font = 52 if label == "OEE" else 38

            st.markdown(f"""
            <div class="kpi-card" style="margin-bottom: 14px;">
                <div class="accent" style="background: {color};"></div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div class="kpi-label">{label}</div>
                        <div class="kpi-value" style="color: {color}; font-size: {big_font}px;">{value:.1f}%</div>
                        <div class="kpi-sub">Target ≥{target}% · {rag_text} · {desc}</div>
                    </div>
                    <div style="width:62px;height:62px;border-radius:50%;border:2.5px solid {color};display:flex;align-items:center;justify-content:center;">
                        <div style="font-size:9px;color:{color};font-family:'JetBrains Mono',monospace;text-align:center;line-height:1.4;">
                            {delta_symbol}<br/>{abs(delta):.1f}%
                        </div>
                    </div>
                </div>
                <div class="kpi-bar">
                    <div class="kpi-bar-fill" style="width: {min(value, 100):.0f}%; background: {color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ── DOWNTIME ──
elif page == "⚠️ Downtime":
    st.markdown("# ⚠️ Downtime & Loss Analysis")

    df_stops = run_query(STOP_HISTORY)

    if not df_stops.empty:
        st.markdown('<div class="section-title">📊 DISTRIBUCIJA ZASTOJA PO MAŠINI</div>', unsafe_allow_html=True)
        stop_summary = df_stops.groupby("EQMT_ID").agg(
            total_sec=("DURATION_SEC", "sum"),
            count=("DURATION_SEC", "count"),
            avg_sec=("DURATION_SEC", "mean"),
        ).reset_index().sort_values("total_sec", ascending=False)

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=stop_summary["EQMT_ID"], y=stop_summary["total_sec"] / 60,
            marker_color=["#00E5FF", "#F5A623"][:len(stop_summary)],
            text=[f"{v:.0f} min" for v in stop_summary["total_sec"] / 60],
            textposition="auto",
        ))
        fig_bar.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="JetBrains Mono", color="#CBD5E1"),
            xaxis=dict(gridcolor="#1B3756"), yaxis=dict(gridcolor="#1B3756"),
            margin=dict(l=0, r=0, t=20, b=0), height=250,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown('<div class="section-title">📋 SVI STOP EVENTI</div>', unsafe_allow_html=True)
        st.dataframe(df_stops, use_container_width=True, height=400)
    else:
        st.info("Nema stop eventa za ovu nedelju.")


# ── AUTO REFRESH ──
if auto_refresh:
    st.markdown(
        f"""
        <script>
            setTimeout(function(){{
                window.location.reload();
            }}, {refresh_interval});
        </script>
        """,
        unsafe_allow_html=True,
    )

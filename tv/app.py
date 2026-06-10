import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "centar"))

from config import OEE_TARGET, DEFAULT_REFRESH
from lib.db import run_query, test_connection
from lib.queries import DAILY_OEE, WEEKLY_OEE
from queries import PROGRAM_HISTORY_PIVOT
from themes import get_theme, get_theme_names

# ── PAGE CONFIG ──
st.set_page_config(page_title="akYtec TV Dashboard", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# ── DEFAULT THEME ──
DEFAULT_THEME = {
    "bg": "#0A0F1D",
    "surface": "rgba(15,23,42,0.75)",
    "border": "#1B3756",
    "accent1": "#00a69c",
    "accent2": "#e6007e",
    "text": "#CBD5E1",
    "muted": "#64748B",
    "green": "#22C55E",
    "amber": "#F5A623",
    "red": "#F87171",
}

if "theme" not in st.session_state:
    st.session_state["theme"] = DEFAULT_THEME
if "theme_name" not in st.session_state:
    st.session_state["theme_name"] = "akYtec Default"

T = st.session_state["theme"]

# ── SIDEBAR — theme selector ──
with st.sidebar:
    st.markdown("### ⚡ Tema")
    theme_name = st.selectbox(
        "Izaberi temu",
        get_theme_names(),
        index=get_theme_names().index(st.session_state["theme_name"]),
        label_visibility="collapsed",
    )
    if theme_name != st.session_state["theme_name"]:
        st.session_state["theme_name"] = theme_name
        st.session_state["theme"] = get_theme(theme_name)
        st.rerun()

    st.markdown("---")
    st.markdown(f"<div style='font-size:11px;color:{T['muted']};font-family:JetBrains Mono,monospace;'>{datetime.now().strftime('%d.%m.%Y %H:%M')}</div>", unsafe_allow_html=True)

# ── CSS ──
def get_css(t):
    return f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; }}
        .stApp {{ background: {t['bg']}; color: {t['text']}; font-family: 'Outfit', sans-serif; }}
        [data-testid="stHeader"] {{ display: none !important; }}
        [data-testid="stToolbar"] {{ display: none !important; }}
        [data-testid="stDeployButton"] {{ display: none !important; }}
        #MainMenu {{ display: none !important; }}
        header {{ display: none !important; }}
        footer {{ display: none !important; }}

        /* Sidebar styling */
        section[data-testid="stSidebar"] {{
            background: {t['bg']} !important;
            border-right: 2px solid {t['border']};
            width: 300px !important;
        }}
        section[data-testid="stSidebar"] .stMarkdown h3 {{
            color: {t['accent1']} !important;
            font-family: 'Outfit', sans-serif !important;
        }}

        /* 4K HEADER */
        .tv-header {{
            background: linear-gradient(135deg, {t['bg']} 0%, rgba(0,0,0,0.3) 100%);
            border-bottom: 2px solid {t['border']};
            padding: 30px 60px;
            display: flex; justify-content: space-between; align-items: center;
            margin: -2rem -2rem 2.5rem -2rem;
        }}
        .tv-logo {{ font-family: 'Outfit', sans-serif; font-size: 52px; font-weight: 700; color: {t['accent1']}; letter-spacing: 0.04em; }}
        .tv-subtitle {{ font-family: 'JetBrains Mono', monospace; font-size: 22px; color: {t['muted']}; margin-top: 6px; }}
        .tv-time {{ font-family: 'JetBrains Mono', monospace; font-size: 38px; color: {t['text']}; text-align: right; }}
        .tv-date {{ font-size: 20px; color: {t['muted']}; text-align: right; }}
        .tv-status {{ display: inline-flex; align-items: center; gap: 10px; background: rgba(34,197,94,0.1); border: 2px solid rgba(34,197,94,0.3); color: {t['green']}; padding: 8px 20px; border-radius: 6px; font-size: 18px; font-family: 'JetBrains Mono', monospace; }}
        .tv-pulse {{ width: 14px; height: 14px; border-radius: 50%; background: {t['green']}; animation: pulse 1.5s infinite; }}
        @keyframes pulse {{ 0%,100% {{ opacity:1; transform:scale(1); }} 50% {{ opacity:0.5; transform:scale(1.3); }} }}

        /* 4K KPI CARD */
        .kpi-card {{
            background: {t['surface']}; backdrop-filter: blur(12px);
            border: 2px solid {t['border']}; border-radius: 20px;
            padding: 50px; position: relative; overflow: hidden;
        }}
        .kpi-card .accent {{ position: absolute; left: 0; top: 0; width: 8px; height: 100%; }}
        .kpi-label {{ font-size: 22px; color: {t['muted']}; text-transform: uppercase; letter-spacing: 0.12em; font-family: 'JetBrains Mono', monospace; margin-bottom: 14px; }}
        .kpi-value {{ font-size: 96px; font-weight: 700; font-family: 'JetBrains Mono', monospace; line-height: 1; }}
        .kpi-sub {{ font-size: 22px; color: {t['muted']}; margin-top: 12px; }}
        .kpi-rag {{ font-size: 20px; font-family: 'JetBrains Mono', monospace; margin-top: 16px; }}
        .kpi-bar {{ height: 10px; background: {t['border']}; border-radius: 5px; margin-top: 24px; }}
        .kpi-bar-fill {{ height: 100%; border-radius: 5px; transition: width 0.5s; }}

        /* 4K SECTION TITLE */
        .section-title {{ font-size: 20px; color: {t['muted']}; text-transform: uppercase; letter-spacing: 0.12em; font-family: 'JetBrains Mono', monospace; margin: 30px 0 20px 0; display: flex; align-items: center; gap: 12px; }}

        /* 4K PROGRAM TABLE */
        .prog-table {{ width: 100%; border-collapse: collapse; }}
        .prog-table th {{ text-align: left; padding: 16px 20px; color: {t['muted']}; border-bottom: 2px solid {t['border']}; font-family: 'JetBrains Mono', monospace; font-size: 16px; text-transform: uppercase; letter-spacing: 0.08em; }}
        .prog-table td {{ padding: 18px 20px; border-bottom: 1px solid rgba(12,28,48,0.5); font-size: 20px; }}
        .prog-table tr:hover {{ background: rgba(0,166,156,0.04); }}
    </style>
    """


# ── HELPERS ──
def rag(v, tgt=85):
    if v >= tgt: return T["green"], "✓ OK"
    elif v >= tgt - 5: return T["amber"], "⚠ WARN"
    else: return T["red"], "✗ ALERT"

def fmt_sec(s): return f"{int(s)//60}m {int(s)%60}s"


# ── RENDER ──
def render_dashboard():
    now = datetime.now()

    # Header
    st.markdown(f"""
    <div class="tv-header">
        <div style="display:flex; align-items:center; gap:14px;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 125 100" width="50" height="40">
                <path d="M 0 0 L 25 0 L 75 50 L 25 100 L 0 100 L 0 75 L 25 75 L 50 50 L 25 25 L 0 25 Z" fill="{T['accent1']}"/>
                <path d="M 67.5 32.5 L 80 45 L 100 25 L 125 25 L 125 0 L 100 0 Z" fill="{T['accent2']}"/>
            </svg>
            <div>
                <div class="tv-logo">akYtec — SMT PRODUCTION DASHBOARD</div>
                <div class="tv-subtitle">Linija 1 · M1 + M2 · SQL Server</div>
            </div>
        </div>
        <div style="text-align:right;">
            <div class="tv-time">{now.strftime('%H:%M:%S')}</div>
            <div class="tv-date">{now.strftime('%d.%m.%Y')}</div>
            <div style="margin-top:6px;"><span class="tv-status"><span class="tv-pulse"></span>ONLINE</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fetch data
    df_daily = run_query(DAILY_OEE)
    df_weekly = run_query(WEEKLY_OEE)
    df_prog = run_query(PROGRAM_HISTORY_PIVOT)

    # ── KPI CARDS ──
    st.markdown('<div class="section-title">📈 OEE DANAŠNJI DAN — Linija 1</div>', unsafe_allow_html=True)

    if not df_daily.empty:
        line_oee = df_daily["OEE"].mean() * 100
        line_a = df_daily["Availability"].mean() * 100
        line_p = df_daily["Performance"].mean() * 100
        line_q = df_daily["Quality"].mean() * 100
    else:
        line_oee = line_a = line_p = line_q = 0

    line_avg = df_weekly["OEE"].mean() * 100 if not df_weekly.empty else 0

    # Line KPI (big)
    st.markdown(f"""
    <div class="kpi-card" style="margin-bottom:24px; border-color:{T['accent1']}33;">
        <div class="accent" style="background:{T['accent1']};"></div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div class="kpi-label">Linija 1 — OEE DANAS</div>
                <div class="kpi-value" style="color:{T['accent1']}; font-size:120px;">{line_oee:.1f}%</div>
                <div class="kpi-sub">Avail {line_a:.0f}% · Perf {line_p:.0f}% · Qual {line_q:.0f}%</div>
            </div>
            <div style="text-align:right;">
                <div class="kpi-sub">7-dnevni prosek</div>
                <div style="font-size:48px; font-family:'JetBrains Mono',monospace; color:{T['accent1']};">{line_avg:.1f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── CHARTS ──
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown('<div class="section-title">📈 OEE TREND — Linija 1</div>', unsafe_allow_html=True)
        if not df_weekly.empty:
            fig = go.Figure()
            # Line average (bold)
            line_daily = df_weekly.groupby("WorkDate")["OEE"].mean().reset_index()
            fig.add_trace(go.Scatter(x=line_daily["WorkDate"], y=line_daily["OEE"]*100,
                name="Linija (prosek)", line=dict(color=T["text"], width=4), mode="lines+markers",
                marker=dict(size=10), opacity=0.9))
            # M1
            d1 = df_weekly[df_weekly["MachineNm"] == "M1"]
            if not d1.empty:
                fig.add_trace(go.Scatter(x=d1["WorkDate"], y=d1["OEE"]*100, name="M1",
                    line=dict(color=T["accent1"], width=2, dash="dot"), mode="markers", marker=dict(size=6)))
            # M2
            d2 = df_weekly[df_weekly["MachineNm"] == "M2"]
            if not d2.empty:
                fig.add_trace(go.Scatter(x=d2["WorkDate"], y=d2["OEE"]*100, name="M2",
                    line=dict(color=T["accent2"], width=2, dash="dot"), mode="markers", marker=dict(size=6)))
            fig.add_hline(y=85, line_dash="dash", line_color=T["green"], annotation_text="Target 85%", annotation_position="right", annotation_font_size=12)
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="JetBrains Mono", color=T["text"]), xaxis=dict(gridcolor=T["border"], tickfont=dict(size=12)),
                yaxis=dict(gridcolor=T["border"], range=[30,100], tickfont=dict(size=12)),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=12)),
                margin=dict(l=0,r=0,t=30,b=0), height=450)
            st.plotly_chart(fig, use_container_width=True)

    with ch2:
        st.markdown('<div class="section-title">⚡ AVAILABILITY — Linija 1</div>', unsafe_allow_html=True)
        if not df_weekly.empty:
            fig2 = go.Figure()
            line_daily_a = df_weekly.groupby("WorkDate")["Availability"].mean().reset_index()
            fig2.add_trace(go.Bar(x=line_daily_a["WorkDate"], y=line_daily_a["Availability"]*100,
                name="Linija (prosek)", marker_color=T["text"], opacity=0.3))
            fig2.add_trace(go.Scatter(x=line_daily_a["WorkDate"], y=line_daily_a["Availability"]*100,
                name="Prosek", line=dict(color=T["accent1"], width=3), mode="lines+markers", marker=dict(size=8)))
            fig2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="JetBrains Mono", color=T["text"], size=14), xaxis=dict(gridcolor=T["border"], tickfont=dict(size=14)),
                yaxis=dict(gridcolor=T["border"], range=[70,100], tickfont=dict(size=14)),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=14)),
                margin=dict(l=0,r=0,t=30,b=0), height=450)
            st.plotly_chart(fig2, use_container_width=True)

    # ── PROGRAM HISTORY ──
    st.markdown('<div class="section-title">📋 ISTORIJA PROGRAMA — Linija 1</div>', unsafe_allow_html=True)
    if not df_prog.empty:
        # Kombinovano po programima (M1 + M2 zajedno)
        df_combined = df_prog.groupby("Program").agg({
            "Danas": "sum", "Juce": "sum", "Pre 2d": "sum", "Pre 3d": "sum",
            "Pre 4d": "sum", "Pre 5d": "sum", "Pre 6d": "sum", "Ukupno": "sum"
        }).reset_index().sort_values("Ukupno", ascending=False)

        # Ukupan red
        totals = {day: df_combined[day].sum() for day in ["Danas","Juce","Pre 2d","Pre 3d","Pre 4d","Pre 5d","Pre 6d","Ukupno"]}

        prog_html = '<table class="prog-table"><thead><tr>'
        prog_html += '<th>Program</th><th>Danas</th><th>Juče</th><th>Pre 2d</th><th>Pre 3d</th><th>Pre 4d</th><th>Pre 5d</th><th>Pre 6d</th><th style="color:' + T['accent1'] + ';">Ukupno</th>'
        prog_html += '</tr></thead><tbody>'

        # Ukupan red (bold)
        prog_html += f'<tr style="font-weight:700; border-bottom:3px solid {T["border"]};">'
        prog_html += f'<td style="color:{T["accent1"]}; font-size:22px;">UKUPNO — Linija 1</td>'
        for day in ["Danas","Juce","Pre 2d","Pre 3d","Pre 4d","Pre 5d","Pre 6d"]:
            val = totals[day]
            prog_html += f'<td style="font-family:"JetBrains Mono",monospace;color:{T["accent1"]}; font-size:20px;">{val if val > 0 else "—"}</td>'
        prog_html += f'<td style="color:{T["accent1"]};font-family:"JetBrains Mono",monospace;font-size:28px;">{totals["Ukupno"]}</td>'
        prog_html += '</tr>'

        # Po programima
        for _, row in df_combined.iterrows():
            total = row["Ukupno"]
            prog_html += '<tr>'
            prog_html += f'<td style="font-size:20px;">{row["Program"]}</td>'
            for day in ["Danas","Juce","Pre 2d","Pre 3d","Pre 4d","Pre 5d","Pre 6d"]:
                val = row[day]
                color = T["text"] if val > 0 else T["muted"]
                prog_html += f'<td style="color:{color};font-family:"JetBrains Mono",monospace; font-size:20px;">{val if val > 0 else "—"}</td>'
            prog_html += f'<td style="color:{T["accent1"]};font-family:"JetBrains Mono",monospace;font-weight:700; font-size:22px;">{total}</td>'
            prog_html += '</tr>'

        prog_html += '</tbody></table>'
        st.markdown(prog_html, unsafe_allow_html=True)
    else:
        st.info("Nema podataka o programima za ovu nedelju.")

    # Auto-refresh
    st.markdown(f'<script>setTimeout(function(){{window.location.reload();}},{DEFAULT_REFRESH});</script>', unsafe_allow_html=True)


# ── RUN ──
st.markdown(get_css(T), unsafe_allow_html=True)
render_dashboard()

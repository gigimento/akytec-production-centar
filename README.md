# SMT Production Centar

A **Streamlit**-based SMT production monitoring dashboard with OEE tracking, downtime analysis, AI-powered root cause analysis, and a TV-optimized read-only view.

## Features

### Production Centar (Full App)
- **Dashboard** — Real-time OEE, Availability, Performance, Quality KPIs with RAG status
- **OEE Trends** — Weekly OEE and availability charts (Plotly)
- **Stop History** — Top stop events with duration analysis
- **SQL Library** — 9+ categorized queries with copy-to-clipboard
- **AI RCA** — Root Cause Analysis powered by Anthropic Claude
- **KPI Calculator** — OEE calculator with target comparison
- **Downtime Analysis** — Stop event distribution by machine

### TV Dashboard
- **4K-optimized** — Large fonts, full-screen layout
- **Theme support** — Multiple color themes (Default, Star Wars, Destiny 2, StarCraft 2, Formula 1)
- **Auto-refresh** — 30-second auto-refresh for live display

## Requirements

- Python 3.8+
- SQL Server database with SMT production views
- [Anthropic Claude API key](https://console.anthropic.com/) (optional, for AI RCA)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and configure:

```env
SQL_SERVER=localhost\SQLEXPRESS
SQL_DATABASE=DatabaseName
ANTHROPIC_API_KEY=sk-ant-...
```

## Running

### Full App (port 8501)
```bash
streamlit run centar/app.py --server.port 8501
```
Or double-click: `run_centar.bat`

### TV Dashboard (port 8502)
```bash
streamlit run tv/app.py --server.port 8502
```
Or double-click: `run_tv.bat`

## Expected Database Views

The app expects a SQL Server database with these views:

| View | Purpose |
|---|---|
| `VW_OEE_DAILY` | Daily OEE by machine |
| `VW_STOP_HIST` | Stop event history |
| `VW_FEEDER` | Feeder status |
| `VW_PLACE_COUNT` | Placement counts and errors |
| `VW_REEL` | Reel inventory |
| `ITS_Part` | Component master data |
| `Custom_ProgramCycleTime` | Program cycle times |

Refer to `centar/lib/queries.py` for exact view schemas.

## Project Structure

```
akytec-production-centar/
├── centar/                 — Full App
│   ├── app.py              — Main Streamlit application
│   ├── config.py           — Configuration and env vars
│   └── lib/
│       ├── db.py           — SQL Server connection
│       └── queries.py      — SQL query definitions
├── tv/                     — TV Dashboard
│   ├── app.py              — Streamlit application
│   ├── queries.py          — TV-specific queries
│   └── themes.py           — UI themes
├── assets/                 — Static assets
│   └── akytec_logo.svg
├── requirements.txt
├── .env.example            — Environment variable template
├── .gitignore
├── run_centar.bat          — Quick launch (full app)
└── run_tv.bat              — Quick launch (TV dashboard)
```

## License

MIT

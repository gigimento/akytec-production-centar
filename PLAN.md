# SMT Production Centar — Project Overview

## Two Applications

| App | Content | Users |
|---|---|---|
| **SMT Production Centar** | Full app (5 tabs) | Process, QC, Supervisor, PM, CEO |
| **SMT TV Dashboard** | Read-only dashboard | CEO, PM, TV display |

## Tech Stack

| Component | Technology |
|---|---|
| **Framework** | Streamlit (Python) |
| **Database** | SQL Server via pyodbc |
| **Charts** | Plotly |
| **AI** | Anthropic Claude API |

## Project Structure

```
akytec-production-centar/
├── centar/                 — Full App (5 tabs)
│   ├── app.py              — Main Streamlit app
│   ├── config.py           — Configuration
│   └── lib/
│       ├── db.py           — SQL connection
│       └── queries.py      — SQL queries
├── tv/                     — TV Dashboard
│   ├── app.py              — Streamlit app
│   ├── queries.py          — TV-specific queries
│   └── themes.py           — Theme definitions
├── assets/
│   └── akytec_logo.svg
├── requirements.txt
├── run_centar.bat
├── run_tv.bat
└── README.md
```

## Running

### Full App
```bash
pip install -r requirements.txt
cd centar
streamlit run app.py --server.port 8501
```

### TV Dashboard
```bash
cd tv
streamlit run app.py --server.port 8502
```

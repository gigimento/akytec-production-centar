import os

# Database
DB_SERVER = os.getenv("SQL_SERVER", r"localhost\SQLEXPRESS")
DB_NAME = os.getenv("SQL_DATABASE", "DatabaseName")

# App
APP_PORT_CENTAR = 8501
APP_PORT_TV = 8502

# Claude API (za AI RCA)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# OEE Targets
OEE_TARGET = 85.0
AVAIL_TARGET = 90.0
PERF_TARGET = 95.0
QUAL_TARGET = 99.0

# Auto-refresh intervals (ms)
REFRESH_OPTIONS = [10000, 20000, 30000, 60000]
DEFAULT_REFRESH = 30000

# Machines
MACHINES = ["MACHINE_1", "MACHINE_2"]
M1, M2 = MACHINES

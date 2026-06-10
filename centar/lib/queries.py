"""SQL queries for akYtec SMT Production Centar."""

DAILY_OEE = """
SELECT WorkDate, MachineNm, BaseProgramNm,
  TotalBoard, WorkedPcb, RunSec, StopSec,
  Availability, Performance, Quality,
  CAST(Availability * Performance * Quality AS float) AS OEE
FROM VW_OEE_DAILY
WHERE WorkDate = CAST(GETDATE() AS DATE)
ORDER BY MachineNm;
"""

WEEKLY_OEE = """
SELECT WorkDate, MachineNm,
  CAST(Availability * Performance * Quality AS float) AS OEE,
  Availability, Performance, Quality
FROM VW_OEE_DAILY
WHERE WorkDate BETWEEN DATEADD(DAY, -7, GETDATE()) AND GETDATE()
ORDER BY WorkDate, MachineNm;
"""

WEEKLY_OEE_AVG = """
SELECT MachineNm,
  AVG(CAST(Availability * Performance * Quality AS float)) AS avg_oee,
  MIN(CAST(Availability * Performance * Quality AS float)) AS min_oee,
  MAX(CAST(Availability * Performance * Quality AS float)) AS max_oee,
  AVG(Availability) AS avg_avail,
  AVG(Performance) AS avg_perf,
  AVG(Quality) AS avg_qual
FROM VW_OEE_DAILY
WHERE WorkDate BETWEEN DATEADD(DAY, -7, GETDATE()) AND GETDATE()
GROUP BY MachineNm;
"""

STOP_HISTORY = """
SELECT TOP 20 EQMT_ID, ERR_CD, ERR_MESG,
  STRT_DT, END_DT, DURATION_SEC
FROM VW_STOP_HIST
WHERE STRT_DT >= DATEADD(DAY, -7, GETDATE())
ORDER BY DURATION_SEC DESC;
"""

FEEDER_TOP = """
SELECT TOP 20 FeederCd, PartNo, SlotNo, EqpNm,
  TotalOdometerCnt, RemainCnt, NGYN
FROM VW_FEEDER
WHERE EqpNm = ?
ORDER BY TotalOdometerCnt DESC;
"""

PLACEMENT_ERRORS = """
SELECT JOB_NAME, EQMT_NAME,
  SUM(PICKUP_CNT) AS total_pickups,
  SUM(ERROR_CNT) AS total_errors,
  CAST(SUM(ERROR_CNT) AS FLOAT) / NULLIF(SUM(PICKUP_CNT),0) * 100 AS error_rate_pct,
  AVG(ERROR_PPM) AS avg_error_ppm
FROM VW_PLACE_COUNT
WHERE WorkDate BETWEEN DATEADD(DAY, -7, GETDATE()) AND GETDATE()
GROUP BY JOB_NAME, EQMT_NAME
HAVING SUM(PICKUP_CNT) > 100
ORDER BY error_rate_pct DESC;
"""

MSL_COMPONENTS = """
SELECT PartNo, MSLLevel, PartType
FROM ITS_Part
WHERE MSLLevel IN ('3','4')
  AND PartNo NOT LIKE '[_]%'
ORDER BY PartNo;
"""

REEL_INVENTORY = """
SELECT TOP 20 ReelCd, PartNo, CurrentCnt, MSLLevel,
  LocationCd, EqpNm, SlotNo, FeederCd
FROM VW_REEL
WHERE LocationCd IS NOT NULL
ORDER BY LastLoadDt DESC;
"""

IDEAL_CYCLE = """
SELECT BaseProgramNm, IdealCycleSec, TotalPlaceCount, PartCnt
FROM Custom_ProgramCycleTime
ORDER BY BaseProgramNm;
"""

ALL_QUERIES = {
    "OEE": [
        {"title": "Daily OEE — sve mašine", "sql": DAILY_OEE},
        {"title": "Weekly OEE — avg/min/max po mašini", "sql": WEEKLY_OEE_AVG},
    ],
    "Downtime": [
        {"title": "Top stop eventi — ova nedelja", "sql": STOP_HISTORY},
    ],
    "Feeders": [
        {"title": "Top 20 feedera po odometru", "sql": FEEDER_TOP},
    ],
    "Placements": [
        {"title": "Failure rate po programu — 7 dana", "sql": PLACEMENT_ERRORS},
    ],
    "MSL": [
        {"title": "MSL 3/4 komponente", "sql": MSL_COMPONENTS},
        {"title": "Reel inventar sa lokacijama", "sql": REEL_INVENTORY},
        {"title": "Idealni ciklus po programu", "sql": IDEAL_CYCLE},
    ],
}

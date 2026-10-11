"""Run the portfolio SQL against saved row-level outputs in in-memory SQLite."""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / "reports" / "sql"
out.mkdir(parents=True, exist_ok=True)
with sqlite3.connect(":memory:") as connection:
    for table, source in {
        "demand_predictions": "demand/holdout_predictions.csv",
        "campaign_predictions": "campaign/holdout_predictions.csv",
        "customer_segments": "segments/customer_segments.csv",
    }.items():
        pd.read_csv(ROOT / "reports" / source).to_sql(table, connection, index=False)
    for query in sorted((ROOT / "sql").glob("*.sql")):
        result = pd.read_sql_query(query.read_text(encoding="utf-8"), connection)
        result.to_csv(out / f"{query.stem}.csv", index=False)
        print(f"Verified {query.name}: {len(result)} output rows")


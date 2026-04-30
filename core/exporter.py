"""导出下载记录。"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.database import list_history


async def export_history_csv(path: str = "exports/history.csv") -> str:
    rows = await list_history()
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    return str(out)


async def export_history_excel(path: str = "exports/history.xlsx") -> str:
    rows = await list_history()
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_excel(out, index=False)
    return str(out)

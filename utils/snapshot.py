"""
Snapshot persistence and weekly diff.

Snapshots are stored as JSON files under ./snapshots/
with filenames like  snapshots/2024-03-09_fintech.json

The diff surface shows:
  - new companies (not seen in the previous snapshot)
  - companies that changed funding stage
  - companies that gained/lost trend tags
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

SNAPSHOT_DIR = Path("snapshots")
SNAPSHOT_DIR.mkdir(exist_ok=True)


def _snapshot_path(industry_key: str) -> Path:
    today = datetime.today().strftime("%Y-%m-%d")
    return SNAPSHOT_DIR / f"{today}_{industry_key}.json"


def _latest_previous_snapshot(industry_key: str) -> Optional[Path]:
    """Return the most recent snapshot file that is NOT today's."""
    today = datetime.today().strftime("%Y-%m-%d")
    files = sorted(SNAPSHOT_DIR.glob(f"*_{industry_key}.json"), reverse=True)
    for f in files:
        if not f.name.startswith(today):
            return f
    return None


def save_snapshot(df: pd.DataFrame, industry_key: str) -> None:
    """Persist today's dataframe as a JSON snapshot."""
    path = _snapshot_path(industry_key)
    df.to_json(path, orient="records", indent=2)


def load_snapshot(path: Path) -> pd.DataFrame:
    with open(path, "r") as f:
        return pd.DataFrame(json.load(f))


def compute_diff(current_df: pd.DataFrame, industry_key: str) -> dict:
    """
    Compare current run against the most recent previous snapshot.

    Returns a dict with:
        new_companies    – DataFrame of companies not seen before
        stage_changes    – DataFrame of companies whose funding_stage changed
        trend_changes    – DataFrame of companies whose trend tag changed
        previous_date    – str date of the snapshot being compared against
        has_previous     – bool
    """
    prev_path = _latest_previous_snapshot(industry_key)

    if prev_path is None:
        return {
            "new_companies": current_df,
            "stage_changes": pd.DataFrame(),
            "trend_changes": pd.DataFrame(),
            "previous_date": None,
            "has_previous": False,
        }

    prev_df = load_snapshot(prev_path)
    previous_date = prev_path.name.split("_")[0]

    prev_names = set(prev_df["name"].str.lower()) if "name" in prev_df.columns else set()
    current_df["_name_lower"] = current_df["name"].str.lower()

    # New companies
    new_mask = ~current_df["_name_lower"].isin(prev_names)
    new_companies = current_df[new_mask].drop(columns=["_name_lower"], errors="ignore")

    # Stage changes
    if "funding_stage" in prev_df.columns:
        prev_stage = prev_df.set_index(prev_df["name"].str.lower())["funding_stage"].to_dict()
        merged = current_df[~new_mask].copy()
        merged["prev_stage"] = merged["_name_lower"].map(prev_stage)
        stage_changes = merged[
            merged["funding_stage"] != merged["prev_stage"]
        ][["name", "prev_stage", "funding_stage"]]
    else:
        stage_changes = pd.DataFrame()

    # Trend changes
    if "trend" in prev_df.columns:
        prev_trend = prev_df.set_index(prev_df["name"].str.lower())["trend"].to_dict()
        merged2 = current_df[~new_mask].copy()
        merged2["prev_trend"] = merged2["_name_lower"].map(prev_trend)
        trend_changes = merged2[
            merged2["trend"] != merged2["prev_trend"]
        ][["name", "prev_trend", "trend"]]
    else:
        trend_changes = pd.DataFrame()

    current_df.drop(columns=["_name_lower"], inplace=True, errors="ignore")

    return {
        "new_companies": new_companies,
        "stage_changes": stage_changes,
        "trend_changes": trend_changes,
        "previous_date": previous_date,
        "has_previous": True,
    }
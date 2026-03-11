"""
Core analysis utilities:
  - clean_data              — deduplicate and normalize a list of DataFrames
  - semantic_overlap        — cosine similarity between company descriptions and portfolio
  - portfolio_overlap       — score companies against a known portfolio dict
  - competitor_overlap      — identify which competitor VC is most likely to invest
  - deal_flow_radar         — predict next investor per company
  - generate_deal_heatmap   — build a VC × Startup likelihood matrix
  - generate_market_map     — reduce description embeddings to 2D (x, y) for scatter plot
  - save_snapshot           — legacy alias (use utils.snapshot.save_snapshot instead)
  - generate_memo           — legacy stub
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD


# ------------------------------------------------------------------ #
#  clean_data                                                          #
# ------------------------------------------------------------------ #

def clean_data(dfs: List[pd.DataFrame]) -> pd.DataFrame:
    """Concatenate, deduplicate, and normalise a list of DataFrames."""
    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)

    # Normalise column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Drop rows with no name
    df = df.dropna(subset=["name"])
    df["name"] = df["name"].astype(str).str.strip()
    df = df[df["name"].str.len() >= 3]

    # Case-insensitive dedup on name
    df["_name_lower"] = df["name"].str.lower()
    df = df.drop_duplicates(subset=["_name_lower"]).drop(columns=["_name_lower"])

    df = df.reset_index(drop=True)
    return df


# ------------------------------------------------------------------ #
#  semantic_overlap                                                    #
# ------------------------------------------------------------------ #

def semantic_overlap(df: pd.DataFrame, portfolio: Dict[str, str]) -> pd.DataFrame:
    """
    For each company in df, compute cosine similarity against portfolio
    company descriptions using TF-IDF.

    Adds columns:
      portfolio_overlap_score   – float 0-1
      closest_portfolio_company – str name of the best-matching portfolio company
    """
    if df.empty or not portfolio:
        df["portfolio_overlap_score"] = 0.0
        df["closest_portfolio_company"] = ""
        return df

    company_texts = df["description"].fillna(df["name"]).tolist()
    portfolio_names = list(portfolio.keys())
    portfolio_texts = [str(v) if v else k for k, v in portfolio.items()]

    all_texts = company_texts + portfolio_texts

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2),
            min_df=1,
        )
        tfidf_matrix = vectorizer.fit_transform(all_texts)

        company_vecs = tfidf_matrix[: len(company_texts)]
        portfolio_vecs = tfidf_matrix[len(company_texts):]

        sim_matrix = cosine_similarity(company_vecs, portfolio_vecs)  # (n_companies, n_portfolio)

        df["portfolio_overlap_score"] = sim_matrix.max(axis=1).round(4)
        best_idx = sim_matrix.argmax(axis=1)
        df["closest_portfolio_company"] = [portfolio_names[i] for i in best_idx]

    except Exception:
        df["portfolio_overlap_score"] = 0.0
        df["closest_portfolio_company"] = ""

    return df


# ------------------------------------------------------------------ #
#  portfolio_overlap                                                   #
# ------------------------------------------------------------------ #

def portfolio_overlap(df: pd.DataFrame, portfolio: Dict[str, str]) -> pd.DataFrame:
    """Boolean flag — is this company already in the portfolio?"""
    df["is_portfolio"] = df["name"].isin(portfolio.keys())
    return df


# ------------------------------------------------------------------ #
#  competitor_overlap                                                  #
# ------------------------------------------------------------------ #

def competitor_overlap(df: pd.DataFrame, competitor_portfolios: Dict[str, Dict]) -> pd.DataFrame:
    """
    For each company, score against each competitor VC's portfolio using TF-IDF.

    Adds columns:
      competitor_overlap_score  – float, max similarity across all competitor VCs
      predicted_investor        – str, name of most likely competitor VC
    """
    if df.empty or not competitor_portfolios:
        df["competitor_overlap_score"] = 0.0
        df["predicted_investor"] = ""
        return df

    company_texts = df["description"].fillna(df["name"]).tolist()
    vc_names = list(competitor_portfolios.keys())

    competitor_scores = np.zeros((len(df), len(vc_names)))

    for j, (vc_name, portfolio) in enumerate(competitor_portfolios.items()):
        if not portfolio:
            continue
        portfolio_texts = [str(v) if v else k for k, v in portfolio.items()]
        all_texts = company_texts + portfolio_texts

        try:
            vectorizer = TfidfVectorizer(
                stop_words="english",
                max_features=3000,
                ngram_range=(1, 2),
                min_df=1,
            )
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            company_vecs = tfidf_matrix[: len(company_texts)]
            portfolio_vecs = tfidf_matrix[len(company_texts):]
            sim = cosine_similarity(company_vecs, portfolio_vecs)
            competitor_scores[:, j] = sim.max(axis=1)
        except Exception:
            pass

    df["competitor_overlap_score"] = competitor_scores.max(axis=1).round(4)
    best_vc_idx = competitor_scores.argmax(axis=1)
    df["predicted_investor"] = [vc_names[i] for i in best_vc_idx]

    return df


# ------------------------------------------------------------------ #
#  deal_flow_radar                                                     #
# ------------------------------------------------------------------ #

def deal_flow_radar(df: pd.DataFrame, competitor_portfolios: Dict[str, Dict]) -> pd.DataFrame:
    """
    Alias that ensures both competitor_overlap_score and predicted_investor
    are present. Calls competitor_overlap if the columns are missing.
    """
    if "competitor_overlap_score" not in df.columns or "predicted_investor" not in df.columns:
        df = competitor_overlap(df, competitor_portfolios)
    return df


# ------------------------------------------------------------------ #
#  generate_deal_heatmap                                               #
# ------------------------------------------------------------------ #

def generate_deal_heatmap(df: pd.DataFrame, competitor_portfolios: Dict[str, Dict]) -> pd.DataFrame:
    """
    Build a VC × Startup similarity matrix for the heatmap chart.

    Returns a DataFrame with:
      rows    = top-N startups (by score)
      columns = VC fund names
      values  = cosine similarity (0-1)
    """
    if df.empty or not competitor_portfolios:
        return pd.DataFrame()

    top_n = min(20, len(df))
    if "score" in df.columns:
        top_df = df.nlargest(top_n, "score").reset_index(drop=True)
    else:
        top_df = df.head(top_n).reset_index(drop=True)

    company_texts = top_df["description"].fillna(top_df["name"]).tolist()
    vc_names = list(competitor_portfolios.keys())

    heatmap_data = {}

    for vc_name, portfolio in competitor_portfolios.items():
        if not portfolio:
            heatmap_data[vc_name] = [0.0] * len(top_df)
            continue

        portfolio_texts = [str(v) if v else k for k, v in portfolio.items()]
        all_texts = company_texts + portfolio_texts

        try:
            vectorizer = TfidfVectorizer(
                stop_words="english",
                max_features=3000,
                ngram_range=(1, 2),
                min_df=1,
            )
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            company_vecs = tfidf_matrix[: len(company_texts)]
            portfolio_vecs = tfidf_matrix[len(company_texts):]
            sim = cosine_similarity(company_vecs, portfolio_vecs)
            heatmap_data[vc_name] = sim.max(axis=1).round(4).tolist()
        except Exception:
            heatmap_data[vc_name] = [0.0] * len(top_df)

    heatmap_df = pd.DataFrame(heatmap_data, index=top_df["name"].tolist())
    return heatmap_df


# ------------------------------------------------------------------ #
#  generate_market_map                                                 #
# ------------------------------------------------------------------ #

def generate_market_map(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reduce TF-IDF description embeddings to 2D (x, y) using TruncatedSVD
    for the market map scatter plot.
    """
    if df.empty:
        df["x"] = []
        df["y"] = []
        return df

    texts = df["description"].fillna(df["name"]).tolist()

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=3000,
            ngram_range=(1, 2),
            min_df=1,
        )
        tfidf_matrix = vectorizer.fit_transform(texts)

        n_components = min(2, tfidf_matrix.shape[1], tfidf_matrix.shape[0] - 1)
        if n_components < 2:
            df["x"] = np.random.rand(len(df))
            df["y"] = np.random.rand(len(df))
            return df

        svd = TruncatedSVD(n_components=2, random_state=42)
        coords = svd.fit_transform(tfidf_matrix)

        df["x"] = coords[:, 0].round(6)
        df["y"] = coords[:, 1].round(6)

    except Exception:
        df["x"] = np.random.rand(len(df))
        df["y"] = np.random.rand(len(df))

    return df


# ------------------------------------------------------------------ #
#  Legacy stubs                                                        #
# ------------------------------------------------------------------ #

def save_snapshot(df: pd.DataFrame, industry_key: str = "unknown") -> None:
    """Legacy alias — delegates to utils.snapshot.save_snapshot."""
    from utils.snapshot import save_snapshot as _save
    _save(df, industry_key)


def generate_memo(df: pd.DataFrame) -> str:
    """Legacy stub — use utils.export.export_pdf for PDF memos."""
    lines = [f"Deal Flow Memo — {datetime.today().strftime('%Y-%m-%d')}", "=" * 50]
    for _, row in df.head(10).iterrows():
        lines.append(f"- {row.get('name', '')} | {row.get('funding_stage', '')} | {row.get('trend', '')}")
    return "\n".join(lines)

import json
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
ARTIFACT_DIR = PROJECT_ROOT / "artifacts"


@st.cache_data
def load_data_objects():
    with open(ARTIFACT_DIR / "deployment_metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)

    data = {
        "app_static": pd.read_csv(ARTIFACT_DIR / "app_static_aligned.csv"),
        "seq_panel": pd.read_csv(ARTIFACT_DIR / "seq_panel_v2.csv"),
        "risk_table": pd.read_csv(ARTIFACT_DIR / "risk_table_test_set.csv"),
        "top_high_risk": pd.read_csv(ARTIFACT_DIR / "top_high_risk_borrowers.csv"),
        "credit_grade_summary": pd.read_csv(ARTIFACT_DIR / "credit_grade_summary.csv"),
        "decision_grade_summary": pd.read_csv(ARTIFACT_DIR / "decision_grade_summary.csv"),
        "threshold_policy_summary": pd.read_csv(ARTIFACT_DIR / "threshold_policy_summary.csv"),
        "executive_summary": pd.read_csv(ARTIFACT_DIR / "executive_summary.csv"),
        "grade_group_summary": pd.read_csv(ARTIFACT_DIR / "grade_group_summary.csv"),
        "borrower_profile_ui": pd.read_csv(ARTIFACT_DIR / "borrower_profile_ui.csv"),
        "selected_static_features": joblib.load(ARTIFACT_DIR / "selected_static_features.joblib"),
        "static_feature_columns": joblib.load(ARTIFACT_DIR / "static_feature_columns.joblib"),
        "num_impute_values": joblib.load(ARTIFACT_DIR / "num_impute_values.joblib"),
        "cat_impute_values": joblib.load(ARTIFACT_DIR / "cat_impute_values.joblib"),
        "temporal_feature_cols_v2": joblib.load(ARTIFACT_DIR / "temporal_feature_cols_v2.joblib"),
        "emb_cols_v2": joblib.load(ARTIFACT_DIR / "embedding_cols_v2.joblib"),
        "metadata": metadata,
    }

    optional_csvs = {
        "shap_global_importance": "shap_global_importance.csv",
        "shap_global_business": "shap_global_business.csv",
        "shap_local_values_test": "shap_local_values_test.csv",
        "borrower_explanation_summary": "borrower_explanation_summary.csv",
    }

    for key, filename in optional_csvs.items():
        path = ARTIFACT_DIR / filename
        data[key] = pd.read_csv(path) if path.exists() else pd.DataFrame()

    return data


def assign_credit_grade_from_summary(pd_value: float, grade_summary: pd.DataFrame) -> str:
    grade_summary = grade_summary.copy()
    grade_summary["credit_grade"] = grade_summary["credit_grade"].astype(str)

    for _, row in grade_summary.iterrows():
        if row["min_pd"] <= pd_value <= row["max_pd"]:
            return row["credit_grade"]

    if pd_value < grade_summary["min_pd"].min():
        return grade_summary.sort_values("min_pd").iloc[0]["credit_grade"]

    return grade_summary.sort_values("max_pd").iloc[-1]["credit_grade"]


def assign_decision_from_grade(credit_grade: str) -> str:
    mapping = {
        "AAA": "Approve",
        "AA": "Approve",
        "A": "Approve",
        "BBB": "Review",
        "BB": "Review",
        "B": "Reject",
        "C": "Reject",
        "D": "Reject",
    }
    return mapping.get(str(credit_grade), "Review")


def format_pct(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "-"
    return f"{value * 100:.{digits}f}%"


def format_pd(value: float, digits: int = 4) -> str:
    if pd.isna(value):
        return "-"
    return f"{value:.{digits}f}"

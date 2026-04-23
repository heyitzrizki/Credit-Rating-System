import json
import pickle
import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st
import torch
import torch.nn as nn


APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
ARTIFACT_DIR = PROJECT_ROOT / "artifacts"


class Chomp1d(nn.Module):
    def __init__(self, chomp_size: int):
        super().__init__()
        self.chomp_size = chomp_size

    def forward(self, x):
        if self.chomp_size == 0:
            return x
        return x[:, :, :-self.chomp_size].contiguous()


class TemporalBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, dilation, dropout=0.1):
        super().__init__()
        padding = (kernel_size - 1) * dilation

        self.conv1 = nn.Conv1d(
            in_channels, out_channels, kernel_size=kernel_size, padding=padding, dilation=dilation
        )
        self.chomp1 = Chomp1d(padding)
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.dropout1 = nn.Dropout(dropout)

        self.conv2 = nn.Conv1d(
            out_channels, out_channels, kernel_size=kernel_size, padding=padding, dilation=dilation
        )
        self.chomp2 = Chomp1d(padding)
        self.bn2 = nn.BatchNorm1d(out_channels)
        self.dropout2 = nn.Dropout(dropout)

        self.downsample = nn.Conv1d(in_channels, out_channels, kernel_size=1) if in_channels != out_channels else None
        self.relu = nn.ReLU()

    def forward(self, x):
        out = self.conv1(x)
        out = self.chomp1(out)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.dropout1(out)

        out = self.conv2(out)
        out = self.chomp2(out)
        out = self.bn2(out)
        out = self.relu(out)
        out = self.dropout2(out)

        res = x if self.downsample is None else self.downsample(x)
        return self.relu(out + res)


class AttentionPooling(nn.Module):
    def __init__(self, hidden_size):
        super().__init__()
        self.attn = nn.Sequential(
            nn.Linear(hidden_size, max(hidden_size // 2, 1)),
            nn.Tanh(),
            nn.Linear(max(hidden_size // 2, 1), 1),
        )

    def forward(self, h, mask=None):
        scores = self.attn(h)
        if mask is not None:
            mask_bool = mask.bool() if mask.dtype != torch.bool else mask
            scores = scores.masked_fill(~mask_bool, float("-inf"))

        weights = torch.softmax(scores, dim=1)
        weights = torch.where(torch.isnan(weights), torch.zeros_like(weights), weights)
        context = (h * weights).sum(dim=1)
        return context, weights


class TCNEncoder(nn.Module):
    def __init__(self, input_dim, channel_sizes=(32, 64), kernel_size=3, dropout=0.2, embedding_dim=64):
        super().__init__()
        layers = []
        in_ch = input_dim
        for i, out_ch in enumerate(channel_sizes):
            dilation = 2 ** i
            layers.append(
                TemporalBlock(
                    in_channels=in_ch,
                    out_channels=out_ch,
                    kernel_size=kernel_size,
                    dilation=dilation,
                    dropout=dropout,
                )
            )
            in_ch = out_ch

        self.tcn = nn.Sequential(*layers)
        self.attn_pool = AttentionPooling(channel_sizes[-1])
        self.proj = nn.Linear(channel_sizes[-1], embedding_dim)

    def forward(self, x, mask=None):
        x = x.transpose(1, 2)
        h = self.tcn(x)
        h = h.transpose(1, 2)
        context, attn_weights = self.attn_pool(h, mask=mask)
        embedding = self.proj(context)
        return embedding, attn_weights, h


@st.cache_resource
def load_models():
    xgb_model = joblib.load(ARTIFACT_DIR / "xgb_hybrid_tuned.joblib")
    platt = joblib.load(ARTIFACT_DIR / "platt_calibrator.joblib")

    with open(ARTIFACT_DIR / "tcn_encoder_config.pkl", "rb") as f:
        tcn_config = pickle.load(f)

    encoder = TCNEncoder(**tcn_config)
    state_dict = torch.load(ARTIFACT_DIR / "tcn_encoder_state.pt", map_location="cpu")
    encoder.load_state_dict(state_dict)
    encoder.eval()

    return xgb_model, platt, encoder, tcn_config


def sanitize_feature_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [re.sub(r"[^A-Za-z0-9_]+", "_", str(c)).strip("_") for c in df.columns]
    return df


def preprocess_static_row(raw_df: pd.DataFrame, data_dict: dict) -> pd.DataFrame:
    df = raw_df.copy()
    num_impute_values = data_dict["num_impute_values"]
    cat_impute_values = data_dict["cat_impute_values"]
    static_feature_columns = data_dict["static_feature_columns"]
    selected_static_features = data_dict["selected_static_features"]

    cols_with_missing = list(num_impute_values.index) + list(cat_impute_values.keys())
    cols_with_missing = [c for c in cols_with_missing if c in df.columns]

    for col in cols_with_missing:
        df[f"{col}_is_missing"] = df[col].isna().astype(int)

    numeric_cols = [c for c in num_impute_values.index if c in df.columns]
    categorical_cols = [c for c in cat_impute_values.keys() if c in df.columns]

    if numeric_cols:
        df[numeric_cols] = df[numeric_cols].fillna(pd.Series(num_impute_values))
    for col in categorical_cols:
        df[col] = df[col].fillna(cat_impute_values[col])

    df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
    df = sanitize_feature_names(df)
    df = df.reindex(columns=static_feature_columns, fill_value=0)
    df = df[selected_static_features]
    return df


def build_existing_borrower_sequence(sk_id: int, data_dict: dict):
    seq_panel = data_dict["seq_panel"]
    temporal_cols = data_dict["temporal_feature_cols_v2"]

    borrower_df = seq_panel[seq_panel["SK_ID_CURR"] == sk_id].copy().sort_values("MONTHS_BALANCE")
    if borrower_df.empty:
        seq = np.zeros((12, len(temporal_cols)), dtype=np.float32)
        mask = np.zeros((12, 1), dtype=bool)
        return seq, mask

    seq = borrower_df[temporal_cols].values.astype(np.float32)
    mask = borrower_df[["time_mask"]].values.astype(bool)
    return seq, mask


def build_temporal_preset(data_dict: dict, preset_name: str):
    seq_panel = data_dict["seq_panel"]
    temporal_cols = data_dict["temporal_feature_cols_v2"]

    base = (
        seq_panel.groupby("MONTHS_BALANCE")[temporal_cols]
        .median(numeric_only=True)
        .reindex(list(range(-11, 1)))
        .fillna(0)
    )

    seq = base.values.astype(np.float32)
    mask = np.ones((12, 1), dtype=bool)
    col_index = {c: i for i, c in enumerate(temporal_cols)}

    def safe_add(col, values):
        if col in col_index:
            seq[:, col_index[col]] = values

    if preset_name == "Stable payer":
        safe_add("pos_dpd_max", np.zeros(12))
        safe_add("cc_dpd_max", np.zeros(12))
        safe_add("inst_late_rate", np.zeros(12))
        safe_add("inst_underpay_rate", np.zeros(12))
        safe_add("bureau_any_delinquent", np.zeros(12))
    elif preset_name == "Mild deterioration":
        trend = np.linspace(0, 2, 12)
        safe_add("pos_dpd_max", trend)
        safe_add("cc_dpd_max", trend)
        safe_add("inst_late_rate", np.linspace(0.02, 0.18, 12))
        safe_add("inst_underpay_rate", np.linspace(0.01, 0.10, 12))
    elif preset_name == "High delinquency":
        safe_add("pos_dpd_max", np.repeat(5.0, 12))
        safe_add("cc_dpd_max", np.repeat(5.0, 12))
        safe_add("inst_late_rate", np.repeat(0.40, 12))
        safe_add("inst_underpay_rate", np.repeat(0.30, 12))
        safe_add("bureau_any_delinquent", np.repeat(1.0, 12))
    elif preset_name == "Recovering borrower":
        rev = np.linspace(4, 0, 12)
        safe_add("pos_dpd_max", rev)
        safe_add("cc_dpd_max", rev)
        safe_add("inst_late_rate", np.linspace(0.30, 0.05, 12))
        safe_add("inst_underpay_rate", np.linspace(0.20, 0.03, 12))

    return seq.astype(np.float32), mask


def get_tcn_embedding(encoder, seq: np.ndarray, mask: np.ndarray):
    x = torch.tensor(seq[None, :, :], dtype=torch.float32)
    m = torch.tensor(mask[None, :, :], dtype=torch.bool)
    with torch.no_grad():
        emb, attn, _ = encoder(x, mask=m)
    return emb.numpy().reshape(1, -1), attn.numpy().reshape(-1)


def score_borrower(static_processed, embedding, xgb_model, platt, emb_cols):
    emb_df = pd.DataFrame(embedding, columns=emb_cols)
    fused = pd.concat([static_processed.reset_index(drop=True), emb_df], axis=1)
    fused = sanitize_feature_names(fused)

    raw_pd = float(xgb_model.predict_proba(fused)[:, 1][0])
    calibrated_pd = float(platt.predict_proba(np.array([[raw_pd]]))[:, 1][0])
    return raw_pd, calibrated_pd

from decimal import Decimal, InvalidOperation
import pandas as pd
import streamlit as st


def apply_text_filters(df, filters):
    for col, value in filters.items():
        if value and value.strip():
            df = df[df[col].astype(str).str.contains(value.strip(), case=False)]
    return df


def apply_date_filters(df, col, date_from, date_to):
    if date_from:
        df = df[df[col] >= pd.to_datetime(date_from)]
    if date_to:
        df = df[df[col] < (pd.to_datetime(date_to) + pd.Timedelta(days=1))]
    return df


def _to_decimal_safe(x):
    try:
        return Decimal(str(x))
    except (InvalidOperation, TypeError, ValueError):
        return None


def apply_decimal_filters(df, col, min_val, max_val):
    df[col + "_dec"] = df[col].apply(_to_decimal_safe)

    if min_val:
        dec = _to_decimal_safe(min_val)
        if dec is not None:
            df = df[df[col + "_dec"].notna() & (df[col + "_dec"] >= dec)]
        else:
            st.warning(f"Min value for {col} is invalid — skipped.")

    if max_val:
        dec = _to_decimal_safe(max_val)
        if dec is not None:
            df = df[df[col + "_dec"].notna() & (df[col + "_dec"] <= dec)]
        else:
            st.warning(f"Max value for {col} is invalid — skipped.")

    df.drop(columns=[col + "_dec"], inplace=True)
    return df


def parse_datetime_column(df, col):

    def _parse(x):
        if pd.isna(x):
            return pd.NaT
        return pd.to_datetime(str(x).replace("Z", "").replace("z", ""), errors="coerce")

    df[col] = df[col].apply(_parse)
    return df


def format_datetime_column(df, col):

    def _fmt(x):
        if pd.isna(x):
            return "—"
        return x.strftime("%H:%M %d/%m/%Y")

    df[col] = df[col].apply(_fmt)
    return df

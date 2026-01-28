import pandas as pd

from helpers import (
    apply_date_filters,
    apply_decimal_filters,
    apply_text_filters,
    format_datetime_column,
    parse_datetime_column,
)


import streamlit as st


def prepare_transaction_df(txs):

    df = pd.DataFrame(txs)

    rename_map = {
        "transaction_id": "Transaction ID",
        "client_id": "Client ID",
        "type": "Type",
        "amount": "Amount",
        "timestamp": "Timestamp",
        "is_reversed": "Reversed",
        "reversal_of_id": "Reversal of",
        "reversed_by_id": "Reversed by",
    }

    df.rename(columns=rename_map, inplace=True)

    df = parse_datetime_column(df, "Timestamp")

    return df[
        [
            "Transaction ID",
            "Client ID",
            "Type",
            "Amount",
            "Timestamp",
            "Reversed",
            "Reversal of",
            "Reversed by",
        ]
    ]


def build_transaction_filters(prefix="tx_", filter_by_id=True):
    if filter_by_id:

        client_id = st.text_input("Client ID", key=f"{prefix}client")

    types = st.multiselect(
        "Type",
        ["deposit", "withdrawal"],
        help="Leave empty to include all",
        key=f"{prefix}types",
    )

    c1, c2 = st.columns(2)
    with c1:
        date_from = st.date_input(
            "Date from", value=None, format="DD/MM/YYYY", key=f"{prefix}date_from"
        )
    with c2:
        date_to = st.date_input(
            "Date to", value=None, format="DD/MM/YYYY", key=f"{prefix}date_to"
        )

    a1, a2 = st.columns(2)
    with a1:
        amount_min = st.text_input("Min amount", key=f"{prefix}amount_min")
    with a2:
        amount_max = st.text_input("Max amount", key=f"{prefix}amount_max")

    sort_desc = st.checkbox("Sort by newest first", value=True, key=f"{prefix}sort")

    if filter_by_id:
        return {
            "client_id": client_id,
            "type": types,
            "date_from": date_from,
            "date_to": date_to,
            "amount_min": amount_min,
            "amount_max": amount_max,
            "sort_desc": sort_desc,
        }
    else:
        return {
            "type": types,
            "date_from": date_from,
            "date_to": date_to,
            "amount_min": amount_min,
            "amount_max": amount_max,
            "sort_desc": sort_desc,
        }


def filter_and_display_transactions(
    df,
    columns,
    text_filter_map,
    types=None,
    date_col=None,
    date_from=None,
    date_to=None,
    decimal_col=None,
    decimal_min=None,
    decimal_max=None,
    sort_desc=True,
):

    df_small = df[columns].copy()

    df_small = apply_text_filters(df_small, text_filter_map)

    if types:
        df_small = df_small[df_small["Type"].isin(types)]

    if date_col:
        df_small = parse_datetime_column(df_small, date_col)
        df_small = apply_date_filters(df_small, date_col, date_from, date_to)

    if decimal_col:
        df_small = apply_decimal_filters(
            df_small, decimal_col, decimal_min, decimal_max
        )

    if date_col:
        df_small = df_small.sort_values(by=date_col, ascending=not sort_desc)
        df_small = format_datetime_column(df_small, date_col)

    st.dataframe(df_small, use_container_width=True, hide_index=True)

    return df_small

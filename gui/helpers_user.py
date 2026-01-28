import pandas as pd
import streamlit as st

from helpers import (
    apply_date_filters,
    apply_decimal_filters,
    apply_text_filters,
    format_datetime_column,
    parse_datetime_column,
)


def build_user_filters(prefix="", include_balance=False):

    f_id = st.text_input("ID", placeholder="e.g. 123456789098", key=f"{prefix}id")
    f_name = st.text_input("Name", placeholder="e.g. John", key=f"{prefix}name")
    f_surname = st.text_input("Surname", placeholder="e.g. Doe", key=f"{prefix}surname")
    f_email = st.text_input(
        "Email", placeholder="e.g. john@doe.com", key=f"{prefix}email"
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

    if include_balance:
        a1, a2 = st.columns(2)
        with a1:
            bal_min = st.text_input("Min balance", key=f"{prefix}bal_min")
        with a2:
            bal_max = st.text_input("Max balance", key=f"{prefix}bal_max")
    else:
        bal_min = None
        bal_max = None

    sort_desc = st.checkbox(
        "Sort by newest first", value=True, key=f"{prefix}sort_desc"
    )

    return {
        "id": f_id,
        "name": f_name,
        "surname": f_surname,
        "email": f_email,
        "date_from": date_from,
        "date_to": date_to,
        "balance_min": bal_min,
        "balance_max": bal_max,
        "sort_desc": sort_desc,
    }


def filter_and_display_table(
    df,
    columns,
    text_filter_map,
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


def prepare_user_df(df, rename_map, columns, parse_date=True):

    df = df.rename(columns=rename_map)

    if parse_date and "Created" in df.columns:
        df = parse_datetime_column(df, "Created")

    df = df[columns]

    return df


def prepare_client_df(clients):
    rename_map = {
        "id": "ID",
        "name": "Name",
        "surname": "Surname",
        "email": "Email",
        "role": "Role",
        "created_at": "Created",
        "_balance": "Balance",
    }

    return prepare_user_df(
        pd.DataFrame(clients),
        rename_map,
        ["ID", "Name", "Surname", "Email", "Balance", "Created"],
        parse_date=True,
    )


def prepare_manager_df(managers):
    rename_map = {
        "id": "ID",
        "name": "Name",
        "surname": "Surname",
        "email": "Email",
        "role": "Role",
        "created_at": "Created",
    }

    return prepare_user_df(
        pd.DataFrame(managers),
        rename_map,
        ["ID", "Name", "Surname", "Email", "Created"],
        parse_date=True,
    )


import streamlit as st
from datetime import datetime


def render_profile_base(data, person_id, title="Profile", extra_fields=None):

    st.subheader(title)

    name = data.get("name", "—")
    surname = data.get("surname", "—")
    email = data.get("email", "—")
    role = data.get("role", "—")
    created_at = data.get("created_at", "—")

    try:
        dt = datetime.fromisoformat(created_at.replace("Z", ""))
        created_fmt = dt.strftime("%H:%M %d/%m/%Y")
    except:
        created_fmt = created_at

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Name:**", name)
        st.write("**Surname:**", surname)
        st.write("**Email:**", email)

    with col2:
        st.write("**ID:**", person_id)
        st.write("**Role:**", role)
        st.write("**Created at:**", created_fmt)

        if extra_fields:
            for label, value in extra_fields.items():
                st.write(f"**{label}:**", value)


def render_manager_profile(manager_id, get_data_fn):

    try:
        data = get_data_fn(manager_id)
    except Exception as e:
        st.error(f"Load manager data error: {e}")
        return

    render_profile_base(
        data=data, person_id=manager_id, title="Manager Profile", extra_fields=None
    )


def render_client_profile(client_id, get_data_fn):

    try:
        data = get_data_fn(client_id)
    except Exception as e:
        st.error(f"Load client data error: {e}")
        return

    balance = data.get("_balance", "—")

    render_profile_base(
        data=data,
        person_id=client_id,
        title="Client Profile",
        extra_fields={"Balance": balance},
    )

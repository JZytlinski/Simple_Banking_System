from decimal import Decimal

import streamlit as st
from api_client import (
    deposit_money,
    withdraw_money,
    transfer_money,
    get_transactions,
    get_personal_data,
    get_statement_pdf_response,
)

from helpers_transaction import (
    build_transaction_filters,
    filter_and_display_transactions,
    prepare_transaction_df,
)
from helpers_user import render_client_profile


def page_client_profile(client_id: str):
    st.subheader("My profile")

    if not client_id:
        st.info("Client ID not provided.")
        return
    render_client_profile(client_id, get_personal_data)


def page_client_deposit(client_id: str):
    st.subheader("Deposit")
    with st.form("form_client_deposit"):
        amount_str = st.text_input("Amount", value="0.00")
        submit = st.form_submit_button("Deposit")
        if submit:
            try:
                amt = Decimal(str(amount_str))
                data = deposit_money(client_id, amt)
                st.success(f"Deposit succeded. Updated balance: {data.get('_balance')}")
            except Exception as e:
                st.error(f"Deposit error: {e}")


def page_client_withdraw(client_id: str):
    st.subheader("Withdrawal")
    with st.form("form_client_withdraw"):
        amount_str = st.text_input("Amount", value="0.00")
        submit = st.form_submit_button("Withdraw")
        if submit:
            try:
                amt = Decimal(str(amount_str))
                data = withdraw_money(client_id, amt)
                st.success(
                    f"Withdrawal succeded. Updated balance: {data.get('_balance')}"
                )
            except Exception as e:
                st.error(f"Withdrawal error: {e}")


def page_client_transfer(client_id: str):
    st.subheader("Transfer")
    with st.form("form_client_withdraw"):
        receiver_str = st.text_input("Receiver ID")
        amount_str = st.text_input("Amount", value="0.00")
        submit = st.form_submit_button("Transfer")
        if submit:
            try:
                amt = Decimal(str(amount_str))
                data = transfer_money(client_id, receiver_str, amt)
                st.success(
                    f"Transfer succeded. Updated balance: {data.get('_balance')}"
                )
            except Exception as e:
                st.error(f"Transfer error: {e}")


def page_client_transactions(client_id: str):
    st.subheader("My transactions")

    with st.expander("Filters", expanded=False):
        filters = build_transaction_filters(filter_by_id=False)

    if st.button("Show my transactions"):
        try:
            txs = get_transactions(client_id)
            if not txs:
                st.info("No transactions.")
                return

            df = prepare_transaction_df(txs)

            filter_and_display_transactions(
                df,
                [
                    "Transaction ID",
                    "Type",
                    "Amount",
                    "Timestamp",
                    "Reversed",
                    "Reversal of",
                    "Reversed by",
                ],
                text_filter_map={},
                types=filters["type"],
                date_col="Timestamp",
                date_from=filters["date_from"],
                date_to=filters["date_to"],
                decimal_col="Amount",
                decimal_min=filters["amount_min"],
                decimal_max=filters["amount_max"],
                sort_desc=filters["sort_desc"],
            )
        except Exception as e:
            st.error(f"Loading transactions error: {e}")


def page_client_statement_pdf(client_id: str):
    st.subheader("My PDF transactions statement")
    if st.button("Generate PDF"):
        try:
            resp = get_statement_pdf_response(client_id)
            pdf_bytes = resp.content
            st.success("Statement was generated.")
            st.download_button(
                "Download PDF file",
                data=pdf_bytes,
                file_name=f"statement_{client_id}.pdf",
                mime="application/pdf",
            )
        except Exception as e:
            st.error(f"Downloaing PDF error: {e}")

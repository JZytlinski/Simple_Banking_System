import streamlit as st

from api_client import (
    get_all_clients,
    delete_person,
    add_client,
)
from api_manager import (
    get_all_managers,
    add_manager,
    get_all_transactions_manager,
    get_manager_personal_data,
    reverse_transaction,
)
from helpers import _to_decimal_safe
from helpers_transaction import (
    build_transaction_filters,
    filter_and_display_transactions,
    prepare_transaction_df,
)
from helpers_user import (
    build_user_filters,
    filter_and_display_table,
    prepare_client_df,
    prepare_manager_df,
    render_manager_profile,
)


def page_manager_list_users():
    st.subheader("Show list of Users")

    tab1, tab2 = st.tabs(["Clients", "Managers"])

    with tab1:

        try:
            clients = get_all_clients()
        except Exception as e:
            st.error(f"Unable to retrieve Client list: {e}")
            clients = []

        if not clients:
            st.info("No clients.")
        else:

            df = prepare_client_df(clients)

            with st.expander("Filters", expanded=False):
                filters = build_user_filters(prefix="client_", include_balance=True)

            if st.button("Show", key="show_clients"):

                filter_and_display_table(
                    df=df,
                    columns=["ID", "Name", "Surname", "Email", "Balance", "Created"],
                    text_filter_map={
                        "ID": filters["id"],
                        "Name": filters["name"],
                        "Surname": filters["surname"],
                        "Email": filters["email"],
                    },
                    date_col="Created",
                    date_from=filters["date_from"],
                    date_to=filters["date_to"],
                    decimal_col="Balance",
                    decimal_min=filters["balance_min"],
                    decimal_max=filters["balance_max"],
                    sort_desc=filters["sort_desc"],
                )

    with tab2:

        try:
            mgrs = get_all_managers()
        except Exception as e:
            st.error(f"Unable to retrieve Managers list: {e}")
            mgrs = []

        if not mgrs:
            st.info("No managers.")
        else:

            df = prepare_manager_df(mgrs)

            with st.expander("Filters", expanded=False):
                filters = build_user_filters(prefix="manager_", include_balance=False)

            if st.button("Show", key="show_managers"):

                filter_and_display_table(
                    df=df,
                    columns=["ID", "Name", "Surname", "Email", "Created"],
                    text_filter_map={
                        "ID": filters["id"],
                        "Name": filters["name"],
                        "Surname": filters["surname"],
                        "Email": filters["email"],
                    },
                    date_col="Created",
                    date_from=filters["date_from"],
                    date_to=filters["date_to"],
                    sort_desc=filters["sort_desc"],
                )


def page_manager_add_user():
    st.subheader("Add User")

    user_type = st.radio("User type", options=["Client", "Manager"], horizontal=True)

    with st.form("form_add_user"):
        id_ = st.text_input("ID", placeholder="e.g. 123456789098")
        name = st.text_input("Name", placeholder="John")
        surname = st.text_input("Surname", placeholder="Doe")
        email = st.text_input("Email", placeholder="john.doe@example.com")

        if user_type == "Client":
            init_balance_str = st.text_input("Initial balance", value="0.00")

        submitted = st.form_submit_button("Create")

        if submitted:
            try:
                if user_type == "Client":
                    init_balance = _to_decimal_safe(init_balance_str)
                    data = add_client(id_, name, surname, email, init_balance)
                    st.success(f"Client created: {data.get('id', id_)}")
                    st.session_state["clients_cache"] = None
                else:
                    data = add_manager(id_, name, surname, email)
                    st.success(f"Manager created: {data.get('id', id_)}")
            except Exception as e:
                st.error(f"Create user error: {e}")


def page_manager_client_transactions():
    st.subheader("All transactions")

    try:
        txs = get_all_transactions_manager()
    except Exception as e:
        st.error(f"Error loading transactions: {e}")
        return

    if not txs:
        st.info("No transactions found.")
        return

    df = prepare_transaction_df(txs)
    with st.expander("Filters", expanded=False):

        filters = build_transaction_filters()

    if st.button("Show"):

        filter_and_display_transactions(
            df,
            [
                "Transaction ID",
                "Client ID",
                "Type",
                "Amount",
                "Timestamp",
                "Reversed",
                "Reversal of",
                "Reversed by",
            ],
            text_filter_map={"Client ID": filters["client_id"]},
            types=filters["type"],
            date_col="Timestamp",
            date_from=filters["date_from"],
            date_to=filters["date_to"],
            decimal_col="Amount",
            decimal_min=filters["amount_min"],
            decimal_max=filters["amount_max"],
            sort_desc=filters["sort_desc"],
        )


def page_manager_delete_user():
    st.subheader("Delete User")
    with st.form("form_delete_user"):
        person_id = st.text_input("User ID", placeholder="e.g. 123456789098")
        submitted = st.form_submit_button("Delete")

        if submitted:
            if not person_id:
                st.warning("Provide User ID.")
                return
            try:
                res = delete_person(person_id)
                st.success(f"Deleted.")
                st.session_state["clients_cache"] = None
            except Exception as e:
                st.error(f"Delete error: {e}")


def page_manager_profile(manager_id: str | None):
    st.subheader("My profile")

    if not manager_id:
        st.info("Manager ID not provided.")
        return

    render_manager_profile(manager_id, get_manager_personal_data)


def page_manager_reverse_transaction():
    st.subheader("Reverse transaction")
    with st.form("form_reverse_tx"):
        tx_id_str = st.text_input("Transaction ID", placeholder="e.g. 123")
        submitted = st.form_submit_button("Reverse")

        if submitted:
            try:
                tx_id = int(tx_id_str)
            except Exception:
                st.warning("Invalid Transaction ID.")
                return

            try:
                res = reverse_transaction(tx_id)
                st.success(f"Reversed.")
            except Exception as e:
                st.error(f"Reverse error: {e}")

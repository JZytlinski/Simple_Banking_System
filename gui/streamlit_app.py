import streamlit as st

from api_client import (
    add_client,
    get_all_clients,
    client_exists,
)

from client_pages import (
    page_client_deposit,
    page_client_profile,
    page_client_statement_pdf,
    page_client_transactions,
    page_client_transfer,
    page_client_withdraw,
)

from api_manager import add_manager, manager_exists
from manager_pages import (
    page_manager_list_users,
    page_manager_add_user,
    page_manager_client_transactions,
    page_manager_delete_user,
    page_manager_profile,
    page_manager_reverse_transaction,
)

st.set_page_config(page_title="Simple Banking System", layout="wide")

st.markdown(
    """
    <style>
        header {visibility: hidden;}
        .block-container { padding-top: 0rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Simple Banking System")


def ensure_session():
    ss = st.session_state
    ss.setdefault("authed", False)
    ss.setdefault("role", None)
    ss.setdefault("user_id", None)
    ss.setdefault("clients_cache", None)
    ss.setdefault("auth_view", "login")


ensure_session()


def logout():
    st.session_state["authed"] = False
    st.session_state["role"] = None
    st.session_state["user_id"] = None
    st.session_state["clients_cache"] = None
    st.success("Wylogowano.")


def login_view():
    st.subheader("Login Page")
    role = st.radio(
        "Choose role", options=["Manager", "Client"], index=0, horizontal=True
    )
    if role == "Client":
        client_id = st.text_input(
            "Provide your Client ID", placeholder="e.g. 12345678901"
        )
    else:
        manager_id = st.text_input(
            "Provide your Manager ID", placeholder="e.g. 12345678901"
        )

    c1, c2 = st.columns([1, 1])
    with c1:

        if st.button("Log in"):
            try:
                if role == "Client":
                    if not client_id:
                        st.error("Provide Client ID.")
                        return
                    if not client_exists(client_id):
                        st.error("Client with this ID doesn't exist.")
                        return
                    st.session_state["authed"] = True
                    st.session_state["role"] = "Client"
                    st.session_state["user_id"] = client_id
                    st.success(f"Logged in as a Client with ID: {client_id}.")
                    st.rerun()

                else:
                    if not manager_id:
                        st.error("Provide Manager ID.")
                        return
                    if not manager_exists(manager_id):
                        st.error("Manager with this ID doesn't exist.")
                        return
                    st.session_state["authed"] = True
                    st.session_state["role"] = "Manager"
                    st.session_state["user_id"] = manager_id
                    st.success(f"Logged in as a Manager with ID: {manager_id}.")
                    st.rerun()
            except Exception as e:
                st.error(f"Login error: {e}")

    with c2:
        if st.button("Register"):
            st.session_state["auth_view"] = "register"
            st.rerun()


def register_view():
    st.subheader("Register")
    role = st.radio(
        "Choose role", options=["Client", "Manager"], index=0, horizontal=True
    )

    col1, col2 = st.columns(2)
    with col1:
        id_ = st.text_input("ID", placeholder="np. 12345678901")
        name = st.text_input("Name")
        surname = st.text_input("Surname")
    with col2:
        email = st.text_input("Email", placeholder="name@example.com")
        if role == "Client":
            balance = st.text_input("Initial balance", value="0.00")

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Create account"):
            if not all([id_, name, surname, email]):
                st.warning("Fill out all fields")
                return

            try:
                if role == "Client":
                    r = add_client(id_, name, surname, email, balance)
                else:
                    r = add_manager(id_, name, surname, email)

                st.success(f"Account {role.lower()} created. Logging in process…")
                st.session_state["authed"] = True
                st.session_state["role"] = role
                st.session_state["user_id"] = id_
                st.rerun()

            except Exception as e:
                st.error(f"Registration error: {e}")

    with c2:
        if st.button("Back to login"):
            st.session_state["auth_view"] = "login"
            st.rerun()


def refresh_clients_cache():
    try:
        st.session_state["clients_cache"] = get_all_clients()
    except Exception as e:
        st.session_state["clients_cache"] = []
        st.error(f"Unable to retrieve Client list : {e}")


def manager_sidebar():
    st.sidebar.subheader("Manager – Actions")
    return st.sidebar.radio(
        "Choose action",
        [
            "View your profile",
            "Show list of Users",
            "Add User",
            "Delete User",
            "Show all transactions",
            "Reverse transaction/transfer",
            "Log out",
        ],
        index=0,
    )


def client_sidebar(client_id: str):
    st.sidebar.subheader(f"Client ID: {client_id}")
    return st.sidebar.radio(
        "Choose action",
        [
            "View your profile",
            "Deposit",
            "Withdrawal",
            "Transfer",
            "View your transactions",
            "Generate your transaction statement",
            "Log out",
        ],
        index=0,
    )


if not st.session_state["authed"]:
    with st.sidebar:
        st.info("Log in to continue...")

    if st.session_state["auth_view"] == "register":
        register_view()
    else:
        login_view()

else:
    role = st.session_state["role"]
    user_id = st.session_state["user_id"]

    if role == "Manager":
        choice = manager_sidebar()
        if choice == "Show list of Users":
            page_manager_list_users()
        elif choice == "Add User":
            page_manager_add_user()
        elif choice == "Show all transactions":
            page_manager_client_transactions()
        elif choice == "Delete User":
            page_manager_delete_user()
        elif choice == "Reverse transaction/transfer":
            page_manager_reverse_transaction()
        elif choice == "Log out":
            logout()
            st.rerun()
        elif choice == "View your profile":
            page_manager_profile(user_id)

    elif role == "Client":
        choice = client_sidebar(user_id)
        if choice == "View your profile":
            page_client_profile(user_id)
        elif choice == "Deposit":
            page_client_deposit(user_id)
        elif choice == "Withdrawal":
            page_client_withdraw(user_id)
        elif choice == "Transfer":
            page_client_transfer(user_id)
        elif choice == "View your transactions":
            page_client_transactions(user_id)
        elif choice == "Generate your transaction statement":
            page_client_statement_pdf(user_id)
        elif choice == "Log out":
            logout()
            st.rerun()

import streamlit as st
from utils.auth import get_user_auth

st.set_page_config(page_title="Audit App - Login", layout="wide")

def main():
    authenticated, user_role, username = get_user_auth()
    st.title("Welcome to the Audit App")
    if authenticated:
        st.success(f"Logged in as {username} ({user_role}) via Windows login.")
        st.info("You are automatically logged in with your Windows account.")
        if st.button("Logout"):
            st.warning("Logout is not supported for Windows login. Please close the browser or app to end your session.")
    else:
        st.error("Could not detect Windows user. Please contact your administrator.")

if __name__ == "__main__":
    main()

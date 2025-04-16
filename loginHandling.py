import json
import streamlit as st
#import firebase_admin
from firebase_admin import credentials, auth
#import pyrebase
from firebase_setup import FireBaseApp

class FireBaseAuth:
    def __init__(self):
        #self._setup_firebase_admin()
        #self.firebase_config = st.secrets["firebase_config"]
        #self.firebase = pyrebase.initialize_app(self.firebase_config)
        #self.auth_client = self.firebase.auth()
        self._setup_firebase_admin()
        self._setup_session_state()

    def _setup_session_state(self):
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.user_id = None
            st.session_state.id_token = None
            st.session_state.screen = "login"

    def login(self):
        st.title("Login to the Sponge Hydration Dashboard")
        with st.form('login'):
            email = st.text_input("Email", key="email_input")
            password = st.text_input("Password", type="password", key="password_input")
            login = st.form_submit_button("Login")
            if login:
                try:
                    user = self.auth_client.sign_in_with_email_and_password(email, password)
                    st.session_state["authenticated"] = True  #only set to true if login successfull
                    st.session_state["user_email"] = user["email"]
                    st.session_state["id_token"] = user["idToken"]
                    st.session_state["user_id"] = user["localId"]
                    #print(st.session_state)
                    st.session_state["screen"] = "dashboard"

                except Exception as e:
                    st.error(f"Authentication failed. Please check your credentials.")
                    st.session_state["authenticated"] = False  #force back to false
                    print(f"Login Failure, error: {e}")
        st.rerun()

    def userID(self):
        user_id = st.session_state.get("user_id", None)
        #print(f"FireBaseAuth userID: {user_id}")  # debug
        return user_id

    def logout(self):
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.session_state.user_id = None
        st.session_state.id_token = None
        st.session_state.screen = "login"
        st.rerun()

if __name__ == "__main__":
    app = FireBaseApp()
    app.run()

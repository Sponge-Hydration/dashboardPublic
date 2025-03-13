import firebase_admin
from firebase_admin import credentials, initialize_app
import streamlit as st
import json

try:
    #if an app is already initialized then get it
    app = firebase_admin.get_app()
except ValueError:
    #otherwise initialize it with the credentials
    firebase_credentials_raw = st.secrets["firebase_credentials"]["credentials"]

    #check if it's a string. if so, parse it, otherwise, convert to a regular dictionary.
    if isinstance(firebase_credentials_raw, str):
        firebase_config_dict = json.loads(firebase_credentials_raw)
    else:
        firebase_config_dict = dict(firebase_credentials_raw)

    cred = credentials.Certificate(firebase_config_dict)
    app = initialize_app(cred)

FireBaseApp = app
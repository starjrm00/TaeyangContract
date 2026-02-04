from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import requests
from datetime import datetime
from Firebase_connect import db
import streamlit as st
import os

CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]

#REDIRECT_URI = "https://taeyang-contract-demo.streamlit.app"
REDIRECT_URI = "http://localhost:8501"
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]

def get_oauth_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

def exchange_code_for_token(flow, code):
    flow.fetch_token(code=code)
    return flow.credentials

def get_user_email(creds):
    res = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {creds.token}"}
    )
    return res.json()["email"]

def save_tokens(email, creds):
    db.collection("oauth_tokens").document(email).set({
        "refresh_token": creds.refresh_token,
        "scopes": creds.scopes,
        "created_at": datetime.utcnow()
    })
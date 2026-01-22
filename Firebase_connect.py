import firebase_admin
import streamlit as st
import json
from firebase_admin import credentials, firestore
import os

if os.path.exists("firebase_service_key.json"):
    #for local
    cred = credentials.Certificate("firebase_service_key.json")
else:
    #for release
    cred_dict = json.loads(st.secrets["firebase_service_key"])
    cred = credentials.Certificate(cred_dict)

db = firestore.client(database_id = "(default)")

#TODO 12시 땡하면 한달남은 거래, 일주일 남은 거래, 하루남은 거래, 오늘 마감인 거래 등록된 구글 캘린더로 알림쏴주기
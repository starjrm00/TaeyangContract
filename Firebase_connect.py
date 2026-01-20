import firebase_admin
import json
from firebase_admin import credentials, firestore
import os

#for local
cred = credentials.Certificate("firebase_service_key.json")

#for distribution
#cred = json.loads(st.secrets["firebase_service_key"])

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client(database_id = "default")

#TODO 12시 땡하면 한달남은 거래, 일주일 남은 거래, 하루남은 거래, 오늘 마감인 거래 등록된 구글 캘린더로 알림쏴주기
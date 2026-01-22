from flask import Request
from google.cloud import firestore
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

def notify_contracts(request: Request):
    #db = firestore.Client()
    db = firestore.Client.from_service_account_json("service-account.json")

    print(db.project)
    credentials = service_account.Credentials.from_service_account_file(
        "service-account.json",
        scopes=["https://www.googleapis.com/auth/calendar"]
    )

    calendar = build("calendar", "v3", credentials=credentials)

    alert_settings = [30, 7, 1]
    trade_query = db.collection("Trade").where("calendar_notify", "==", False)
    trades = trade_query.stream()

    print("")
    for doc in trades:
        data = doc.to_dict()
        trade_company = data["trade_company"]
        trade_item = data["trade_item"]
        end_date = data["trade_end_date"].date()
        reminders = [{"method": "popup", "minutes": 60*24*days} for days in alert_settings]

        print(f"{trade_company}와 거래하는 {trade_item}의 종료일은 {end_date}입니다")

        event = {
            "summary": f"계약 종료 예정: {trade_company}, {trade_item}",
            "description": "계약 종료 전 팝업알림, 계약이 변동되었다면 삭제해주세요",
            "start": {"date": end_date.isoformat()},
            "end": {"date": end_date.isoformat()},
            "reminders": {
                "useDefault": False,
                "overrides": reminders
            }
        }

        created_event = calendar.events().insert(
            calendarId="starjrm00@gmail.com",
            body=event
        ).execute()

        doc.reference.update({
            "calendar_notify": True
        })

    return "OK"

if __name__ == "__main__":
    notify_contracts(None)
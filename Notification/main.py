from flask import Flask, Request, redirect, request, session, url_for
from google.cloud import firestore
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import datetime
import os

app = Flask(__name__)
app.secret_key = "YOUR_SECRET_KEY"

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# =========================
# OAuth 로그인
# =========================
@app.route("/authorize")
def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for("oauth2callback", _external=True)
    )
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )
    session["state"] = state
    return redirect(authorization_url)

@app.route("/oauth2callback")
def oauth2callback():
    state = session["state"]
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for("oauth2callback", _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    session["credentials"] = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    }
    return "OAuth 완료! 이제 캘린더 이벤트 자동 등록 가능."

# =========================
# Firestore 기반 알림 자동 등록
# =========================
@app.route("/notify_contracts")
def notify_contracts():
    if "credentials" not in session:
        return redirect(url_for("authorize"))

    creds = Credentials(**session["credentials"])
    calendar = build("calendar", "v3", credentials=creds)
    db = firestore.Client.from_service_account_json("service-account.json")

    alert_settings = [28, 7, 1]  # days before
    trade_query = db.collection("Trade").where("calendar_notify", "==", False)
    trades = trade_query.stream()

    now = datetime.datetime.now(datetime.timezone.utc)

    for doc in trades:
        data = doc.to_dict()
        trade_company = data["trade_company"]
        trade_item = data["trade_item"]
        end_date = data["trade_end_date"].date()

        start_dt = datetime.datetime.combine(end_date, datetime.time(9, 0))
        end_dt = datetime.datetime.combine(end_date, datetime.time(10, 0))

        # KST timezone
        import pytz
        KST = pytz.timezone("Asia/Seoul")
        start_dt = KST.localize(start_dt)
        end_dt = KST.localize(end_dt)

        # reminders 계산
        reminders = []
        for days in alert_settings:
            remind_time = start_dt - datetime.timedelta(days=days)
            if remind_time > now:
                minutes = int((start_dt - remind_time).total_seconds() / 60)
                reminders.append({"method": "popup", "minutes": minutes})

        print(f"{trade_company} {trade_item} 종료일 {end_date} → reminders: {reminders}")

        event = {
            "summary": f"계약 종료 예정: {trade_company}, {trade_item}",
            "description": "계약 종료 전 팝업 알림",
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "Asia/Seoul"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "Asia/Seoul"},
            "reminders": {"useDefault": False, "overrides": reminders}
        }

        created_event = calendar.events().insert(
            calendarId="primary",
            body=event
        ).execute()

        # Firestore flag 업데이트
        doc.reference.update({"calendar_notify": True})

    return "모든 계약 알림 등록 완료!"

# =========================
# Flask 실행
# =========================
if __name__ == "__main__":
    app.run(debug=True)

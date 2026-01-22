from Firebase_connect import db
from google.cloud import firestore
from datetime import datetime

def upload_new_trade(df):
    for _, row in df.iterrows():
        data = {
            "trade_company": row["계약업체"],
            "trade_item": row["계약항목"],
            "trade_start_date": row["계약시작일"],
            "trade_end_date": row["계약종료일"],
            "trade_amount": row["계약금액"],
            "memo": "",
            "calendar_notify": False
        }

        db.collection("Trade").add(data)



def edit_trade_data(origin_df, edited_df):
    for i in edited_df.index:
        origin = origin_df.loc[i]
        edited = edited_df.loc[i]

        origin["계약금액"] = int(origin["계약금액"].replace("₩", "").replace(",", "").strip())
        edited["계약금액"] = int(edited["계약금액"].replace("₩", "").replace(",", "").strip())

        update_data = {
            "trade_company": edited["계약업체"],
            "trade_item": edited["계약항목"],
            "trade_start_date": datetime.combine(edited["계약시작일"], datetime.min.time()),
            "trade_end_date": datetime.combine(edited["계약종료일"], datetime.min.time()),
            "trade_amount": edited["계약금액"],
            "memo": edited["메모"],
            "calendar_notify": False
        }

        is_changed = (
            origin["계약업체"] != edited["계약업체"] or
            origin["계약항목"] != edited["계약항목"] or
            origin["계약시작일"] != edited["계약시작일"] or
            origin["계약종료일"] != edited["계약종료일"] or
            origin["계약금액"] != edited["계약금액"] or
            origin["메모"] != edited["메모"]
        )
            
        if is_changed:
            db.collection("Trade").document(origin["doc_id"]).update(update_data)
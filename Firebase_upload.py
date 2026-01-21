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
            "memo": ""
        }

        db.collection("Trade").add(data)



def edit_trade_data(origin_df, edited_df):
    for i in edited_df.index:
        origin = origin_df.loc[i]
        edited = edited_df.loc[i]

        edited["계약금액"] = int(edited["계약금액"].replace("₩", "").replace(",", "").strip())

        update_data = {
            "trade_company": edited["계약업체"],
            "trade_item": edited["계약항목"],
            "trade_start_date": datetime.combine(edited["계약시작일"], datetime.min.time()),
            "trade_end_date": datetime.combine(edited["계약종료일"], datetime.min.time()),
            "trade_amount": edited["계약금액"],
            "memo": edited["메모"]
        }

        db.collection("Trade").document(origin["doc_id"]).update(update_data)
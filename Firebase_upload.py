from Firebase_connect import db
from google.cloud import firestore

def upload_new_trade(df):
    for _, row in df.iterrows():
        doc_id = f"{row['거래업체']}_{row['거래항목']}_{row['거래시작일']}_{row['거래종료일']}_{row['거래금액']}".replace("/", "")
        trade_ref = db.collection("Trade").document(doc_id)

        trade_ref.set({
            "trade_company": row["거래업체"],
            "trade_item": row["거래항목"],
            "trade_start_date": row["거래시작일"],
            "trade_end_date": row["거래종료일"],
            "trade_amount": row["거래금액"],
            "memo": ""
        }, merge = True)
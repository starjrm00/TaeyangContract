from Firebase_connect import db
import pandas as pd

def get_trade_data(trade_company, trade_item):
    trade_ref = db.collection("Trade")
    if trade_company == "" and trade_item == "":
        query = trade_ref
    elif trade_company == "":
        query = trade_ref.where("trade_item", "==", trade_item)
    elif trade_item == "":
        query = trade_ref.where("trade_company", "==", trade_company)
    else:
        query = trade_ref.where("trade_company", "==", trade_company).where("trade_item", "==", trade_item)
    docs = query.stream()

    data_list = []
    for doc in docs:
        d = doc.to_dict()
        d["doc_id"] = doc.id
        data_list.append(d)
    
    if not data_list:
        return pd.DataFrame()
    
    df = pd.DataFrame(data_list)

    if "trade_company" in df.columns:
        df = df.rename(columns={"trade_company": "계약업체"})
    if "trade_item" in df.columns:
        df = df.rename(columns={"trade_item": "계약항목"})
    if "trade_start_date" in df.columns:
        df = df.rename(columns={"trade_start_date": "계약시작일"})
    if "trade_end_date" in df.columns:
        df = df.rename(columns={"trade_end_date": "계약종료일"})
    if "trade_amount" in df.columns:
        df = df.rename(columns={"trade_amount": "계약금액"})
    if "memo" in df.columns:
        df = df.rename(columns={"memo": "메모"})
    
    cols = ["계약업체", "계약항목", "계약시작일", "계약종료일", "계약금액", "메모", "doc_id"]
    df = df[cols]
    return df

def get_accumulate_trade_data(trade_company, trade_item):
    trade_ref = db.collection("Trade")
    if trade_company == "" and trade_item == "":
        query = trade_ref
    elif trade_company == "":
        query = trade_ref.where("trade_item", "==", trade_item)
    elif trade_item == "":
        query = trade_ref.where("trade_company", "==", trade_company)
    else:
        query = trade_ref.where("trade_company", "==", trade_company).where("trade_item", "==", trade_item)
    docs = query.stream()

    data_list = [doc.to_dict() for doc in docs]
    
    if not data_list:
        return pd.DataFrame()
    
    df = pd.DataFrame(data_list)

    if "trade_company" in df.columns:
        df = df.rename(columns={"trade_company": "계약업체"})
    if "trade_item" in df.columns:
        df = df.rename(columns={"trade_item": "계약항목"})
    if "trade_start_date" in df.columns:
        df = df.rename(columns={"trade_start_date": "계약시작일"})
    if "trade_end_date" in df.columns:
        df = df.rename(columns={"trade_end_date": "계약종료일"})
    if "trade_amount" in df.columns:
        df = df.rename(columns={"trade_amount": "계약금액"})
    if "memo" in df.columns:
        df = df.rename(columns={"memo": "메모"})
    
    cols = ["계약업체", "계약항목", "계약시작일", "계약종료일", "계약금액", "메모"]
    df = df[cols]

    total_amount = df["계약금액"].sum()
    sum_row = {
        "계약업체": "합계",
        "계약항목": "",
        "계약시작일": "",
        "계약종료일": "",
        "계약금액": total_amount,
        "메모": ""
    }
    df = pd.concat([df, pd.DataFrame([sum_row])], ignore_index=True)

    return df
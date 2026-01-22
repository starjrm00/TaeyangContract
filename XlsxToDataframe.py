import pandas as pd

def xlsxToDf(xlsx):
    df_pandas = pd.read_excel(xlsx, header = 3)
    print(df_pandas.columns.tolist())

    #필요한 column만 추출하기
    df_pandas = df_pandas[["계약업체", "계약항목", "계약시작일", "계약종료일", "계약금액"]]
    df_pandas = df_pandas.dropna(subset = ["계약업체", "계약항목", "계약시작일", "계약종료일", "계약금액"])

    #날짜 data들 강제 형변환
    for col in ["계약시작일", "계약종료일"]:
        df_pandas[col] = pd.to_datetime(df_pandas[col], errors = "coerce")

    print(df_pandas)
    return df_pandas

def makeNewTrade(xlsx):
    df_pandas = pd.read_excel(xlsx)
    df_pandas = df_pandas[["계약업체", "계약항목", "계약시작일", "계약종료일", "계약금액"]]
    df_pandas = df_pandas.dropna(subset = ["계약업체", "계약항목", "계약시작일", "계약종료일", "계약금액"])

    print(df_pandas)
    #날짜 data들 강제 형변환
    for col in ["계약시작일", "계약종료일"]:
        df_pandas[col] = pd.to_datetime(df_pandas[col], errors = "coerce")

    print(df_pandas)
    return df_pandas
import streamlit as st
import pandas as pd
from datetime import datetime
from Firebase_upload import upload_new_trade
from Firebase_download import get_trade_data, get_accumulate_trade_data
from Firebase_connect import db
from XlsxToDataframe import makeNewTrade

st.set_page_config(page_title="태양메디 거래관리 시스템", layout="wide")
st.title("태양메디 거래관리 시스템")

#버튼 세팅
col1, col2 = st.columns([1, 1])
with col1:
    btn1 = st.button("거래내역 검색")

with col2:
    btn2 = st.button("거래내역 등록")
#page 세팅
if 'page' not in st.session_state:
    st.session_state.page = 1

if btn1:
    st.session_state.page = 1
elif btn2:
    st.session_state.page = 2

if st.session_state.page == 1:

    st.markdown("거래내역 검색창")
    st.markdown("둘 다 입력시 하단에 누적 거래금액이 추가로 출력됩니다.")
    
    col1, col2 = st.columns(2)
    with col1:
        거래업체 = st.text_input("거래업체", placeholder="예: LG")
    with col2:
        거래항목 = st.text_input("거래항목", placeholder="예: 정수기")
    
    if st.button("조회하기"):
        if 거래업체 != "" and 거래항목 != "":
            df = get_accumulate_trade_data(거래업체, 거래항목)
            if df.empty:
                st.info("해당하는 거래 데이터가 존재하지 않습니다.")
            else:
                df["거래시작일"] = pd.to_datetime(df["거래시작일"], errors='coerce').dt.date
                df["거래종료일"] = pd.to_datetime(df["거래종료일"], errors='coerce').dt.date
                df["거래금액"] = df["거래금액"].apply(lambda x: f"₩{x:,}")
                st.success(f"{len(df)-1}개의 거래내역 존재")
                st.dataframe(df)
        else:
            df = get_trade_data(거래업체, 거래항목)

            if df.empty:
                st.info("해당하는 거래 데이터가 존재하지 않습니다.")
            else:
                df["거래시작일"] = df["거래시작일"].dt.date
                df["거래종료일"] = df["거래종료일"].dt.date
                df["거래금액"] = df["거래금액"].apply(lambda x: f"₩{x:,}")
                st.success(f"{len(df)}개의 거래내역 존재")
                st.dataframe(df)

elif st.session_state.page == 2:

    st.markdown("거래내역 입력창")

    with st.form("upload-form", clear_on_submit=True):
        uploaded_file = st.file_uploader("데이터를 설정할 엑셀파일을 업로드 해주세요", type=["xlsx"])
        submitted_upload = st.form_submit_button("업로드")
        if submitted_upload and uploaded_file is not None:
            df = makeNewTrade(uploaded_file)
            upload_new_trade(df)
            st.success(f"데이터{uploaded_file.name}가 DB에 적용되었습니다.")
        elif submitted_upload:
            st.error("엑셀 파일을 먼저 업로드해주세요")

    with st.form("product input form"):
        st.markdown("직접 하나씩 입력하기")
        거래업체 = st.text_input("거래업체", placeholder="예: 후문약국")
        거래항목 = st.text_input("거래항목", placeholder="예: 하모닐란액")
        거래시작일 = st.text_input("거래시작일", placeholder="YYYYMMDD형식으로 입력해주세요")
        거래종료일 = st.text_input("거래종료일", placeholder="YYYYMMDD형식으로 입력해주세요")
        거래금액 = st.number_input("거래금액", min_value=0, step=1)

        submitted = st.form_submit_button("데이터 생성")

        if submitted:
            if not all([거래업체, 거래항목, 거래시작일, 거래종료일]):
                st.error("모든 텍스트 항목을 입력해주세요")
            elif 거래금액 == 0:
                st.error("거래 금액 관련 칸이 0입니다. 다시한번 확인해주세요")
            else:
                try:
                    start_date = datetime.strptime(거래시작일, "%Y%m%d")
                    end_date = datetime.strptime(거래종료일, "%Y%m%d")
                except ValueError:
                    st.error("거래기간 양식을 정확히 맞춰주세요")
                    st.stop()
                df = pd.DataFrame([{
                    "거래업체": 거래업체,
                    "거래항목": 거래항목,
                    "거래시작일": start_date,
                    "거래종료일": end_date,
                    "거래금액": 거래금액
                }])

                upload_new_trade(df)
                st.success("해당 데이터가 DB에 적용되었습니다.")
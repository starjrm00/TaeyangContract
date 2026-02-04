import streamlit as st
import pandas as pd
from datetime import datetime
from google_auth_oauthlib.flow import Flow
import os
from Firebase_upload import upload_new_trade, edit_trade_data
from Firebase_download import get_trade_data, get_accumulate_trade_data
from Firebase_connect import db
from XlsxToDataframe import makeNewTrade
from openpyxl.utils import get_column_letter
from set_notification import notify_contracts
import io

st.set_page_config(page_title="태양메디 계약관리 시스템", layout="wide")
st.title("태양메디 계약관리 시스템")

#버튼 세팅
col1, col2,  col4 = st.columns([1, 1, 1])
with col1:
    btn1 = st.button("계약내역 검색")

with col2:
    btn2 = st.button("계약내역 누적 검색")

#with col3:
#    btn3 = st.button("계약 구글 캘린더에 등록")

with col4:
    btn4 = st.button("신규계약 등록")

#page 세팅
if 'page' not in st.session_state:
    st.session_state.page = 1

if btn1:
    st.session_state.page = 1
if btn2:
    st.session_state.page = 2

#if btn3:
#    notify_contracts()

if btn4:
    st.session_state.page = 4

if st.session_state.page == 1:
    st.markdown("계약내역 검색창")
    
    col1, col2 = st.columns(2)
    with col1:
        계약업체 = st.text_input("계약업체", placeholder="예: LG")
    with col2:
        계약항목 = st.text_input("계약항목", placeholder="예: 정수기")
    
    if st.button("조회하기"):
        df = get_trade_data(계약업체, 계약항목)
        if df.empty:
            st.info("해당하는 계약 데이터가 존재하지 않습니다.")
        else:
            df["계약시작일"] = df["계약시작일"].dt.date
            df["계약종료일"] = df["계약종료일"].dt.date
            df["계약금액"] = df["계약금액"].apply(lambda x: f"₩{x:,}")
            df_display = df.drop(columns=["doc_id"], errors='ignore')
            
            st.session_state["df_display"] = df_display
            st.session_state["df_original"] = df

            st.success(f"{len(df)}개의 계약내역 존재")
    if "df_display" in st.session_state:
        edited_df = st.data_editor(st.session_state["df_display"], num_rows = "fixed")
        
        # 엑셀 다운로드 버튼
        output = io.BytesIO()
        df_to_download = st.session_state["df_display"].copy()
        # index 제외하고 저장
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_to_download.to_excel(writer, index=False, sheet_name='계약내역')
            # 시트 가져오기
            worksheet = writer.sheets['계약내역']

            # 각 컬럼 폭 자동 조정
            for i, col in enumerate(df_to_download.columns, 1):
                max_length = max(
                    df_to_download[col].astype(str).map(len).max(),  # 데이터 길이
                    len(col)  # 헤더 길이
                )
                worksheet.column_dimensions[get_column_letter(i)].width = max_length + 2  # 여유 2칸


        processed_data = output.getvalue()

        st.download_button(
            label="엑셀 다운로드",
            data=processed_data,
            file_name="계약내역.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        if st.button("수정 내용 저장"):
            edit_trade_data(st.session_state["df_original"], edited_df)
            st.success("수정 사항이 저장되었습니다 다시 조회해주세요")

            del st.session_state["df_display"]
            del st.session_state["df_original"]


elif st.session_state.page == 2:
    st.markdown("계약내역 누적 검색창")
    
    col1, col2 = st.columns(2)
    with col1:
        계약업체 = st.text_input("계약업체", placeholder="예: LG")
    with col2:
        계약항목 = st.text_input("계약항목", placeholder="예: 정수기")
    
    if st.button("조회하기"):
        df = get_accumulate_trade_data(계약업체, 계약항목)
        if df.empty:
            st.info("해당하는 계약 데이터가 존재하지 않습니다.")
        else:
            df["계약시작일"] = pd.to_datetime(df["계약시작일"], errors='coerce').dt.date
            df["계약종료일"] = pd.to_datetime(df["계약종료일"], errors='coerce').dt.date
            df["계약금액"] = df["계약금액"].apply(lambda x: f"₩{x:,}")
            st.success(f"{len(df)-1}개의 계약내역 존재")
            st.dataframe(df)

        # 엑셀 다운로드 버튼
        output = io.BytesIO()
        df_to_download = df.copy()
        # index 제외하고 저장
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_to_download.to_excel(writer, index=False, sheet_name='계약내역')
        processed_data = output.getvalue()

        st.download_button(
            label="엑셀 다운로드",
            data=processed_data,
            file_name="계약내역.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

elif st.session_state.page == 4:

    st.markdown("계약내역 입력창")

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
        계약업체 = st.text_input("계약업체", placeholder="예: 후문약국")
        계약항목 = st.text_input("계약항목", placeholder="예: 하모닐란액")
        계약시작일 = st.text_input("계약시작일", placeholder="YYYYMMDD형식으로 입력해주세요")
        계약종료일 = st.text_input("계약종료일", placeholder="YYYYMMDD형식으로 입력해주세요")
        계약금액 = st.number_input("계약금액", min_value=0, step=1)

        submitted = st.form_submit_button("데이터 생성")

        if submitted:
            if not all([계약업체, 계약항목, 계약시작일, 계약종료일]):
                st.error("모든 텍스트 항목을 입력해주세요")
            elif 계약금액 == 0:
                st.error("계약 금액 관련 칸이 0입니다. 다시한번 확인해주세요")
            else:
                try:
                    start_date = datetime.strptime(계약시작일, "%Y%m%d")
                    end_date = datetime.strptime(계약종료일, "%Y%m%d")
                except ValueError:
                    st.error("계약기간 양식을 정확히 맞춰주세요")
                    st.stop()
                df = pd.DataFrame([{
                    "계약업체": 계약업체,
                    "계약항목": 계약항목,
                    "계약시작일": start_date,
                    "계약종료일": end_date,
                    "계약금액": 계약금액
                }])

                upload_new_trade(df)
                st.success("해당 데이터가 DB에 적용되었습니다.")
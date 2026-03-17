import streamlit as st
import google.generativeai as genai
import pandas as pd

# Gemini 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.0-flash')
except:
    st.error("API 키 설정이 필요합니다. Settings > Secrets를 확인하세요.")

st.set_page_config(page_title="Shopee Sourcing Tool", layout="wide")
st.title("🚀 Shopee AI 상품 마스터")

# --- UI 섹션 ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. 정보 입력 (URL 또는 수동)")
    method = st.radio("입력 방식 선택", ["직접 입력 (추천)", "URL 자동 수집 (네이버/다이소 전용)"])
    
    input_title = ""
    input_price = 0
    
    if method == "직접 입력 (추천)":
        input_title = st.text_input("상품명 입력", "신일 탁상용 선풍기")
        input_price = st.number_input("한국 원가(KRW)", value=25000, step=1000)
    else:
        st.warning("쿠팡은 차단 정책으로 인해 수동 입력을 권장합니다.")
        url = st.text_input("상품 URL 입력")
        st.info("URL 수집 기능은 구글 API 한도에 따라 작동이 멈출 수 있습니다.")

with col2:
    st.subheader("2. 쇼피용 최적화 결과")
    if st.button("✨ 쇼피용으로 변환하기"):
        if input_title:
            with st.spinner("AI가 상품명을 영어로 번역하고 최적화 중..."):
                try:
                    # AI에게 번역 및 키워드 추출 요청
                    prompt = f"상품명 '{input_title}'을 쇼피 싱가포르 판매용 영어 제목으로 변환해줘. 브랜드명이 있다면 포함하고, 상품의 특징 키워드 3개를 조합해서 80자 이내로 만들어줘. 결과만 딱 한 줄로 말해."
                    response = model.generate_content(prompt)
                    eng_title = response.text.strip()
                    
                    # 쇼피 가격 계산기 (환율 1,000원 기준 / 마진 30%)
                    # 식: (원가 * 마진배수) / 환율
                    sgd_price = round((input_price * 1.35) / 1000, 2)
                    
                    st.success("변환 성공!")
                    st.markdown(f"### 🇬🇧 영어 상품명\n`{eng_title}`")
                    st.markdown(f"### 🇸🇬 권장 판매가\n`$ {sgd_price} SGD` (마진/수수료 포함)")
                    
                    # 엑셀 저장용 데이터 준비
                    st.session_state['final_data'] = {
                        "Original": input_title,
                        "English": eng_title,
                        "Price_KRW": input_price,
                        "Price_SGD": sgd_price
                    }
                except Exception as e:
                    st.error(f"API 한도 초과 또는 오류: 1분 뒤에 다시 시도해주세요. ({str(e)})")
        else:
            st.warning("상품명을 입력해주세요.")

# --- 하단 미리보기 ---
if 'final_data' in st.session_state:
    st.divider()
    st.subheader("📊 엑셀 등록용 데이터 미리보기")
    df = pd.DataFrame([st.session_state['final_data']])
    st.table(df)

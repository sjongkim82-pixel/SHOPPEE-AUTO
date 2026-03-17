import streamlit as st
import pandas as pd
from googlesearch import search
import re

# 페이지 설정
st.set_page_config(page_title="Shopee Sourcing Master", layout="wide")

def scrape_via_google(url):
    """쇼핑몰 직접 접속 대신 구글 검색 데이터를 활용"""
    try:
        # 구글에서 해당 URL을 검색 (최상단 결과 1개만 가져옴)
        query = f"info:{url}"
        results = list(search(query, num_results=1, advanced=True))
        
        if results:
            res = results[0]
            # 구글 검색 결과의 제목 (쇼핑몰이 설정한 상품명)
            title = res.title.split(":")[0].replace(" - 네이버 스마트스토어", "").strip()
            
            # 설명글(Snippet)에서 가격 패턴(숫자+원) 추출 시도
            description = res.description
            price = "0"
            price_match = re.search(r'([\d,]+)원', description)
            if price_match:
                price = price_match.group(1).replace(",", "")
            
            return {
                "title": title,
                "price": price,
                "description": description
            }
        else:
            return None
    except Exception as e:
        st.error(f"우회 시도 중 오류: {e}")
        return None

# --- UI 레이아웃 ---
st.title("🛡️ Shopee Sourcing (Google Cache Mode)")
st.info("쇼핑몰의 직접 차단을 피해 구글 검색 엔진 데이터로 정보를 읽어옵니다.")

url_input = st.text_input("수집할 상품 URL을 입력하세요 (네이버, 쿠팡, 다이소 등)")

if st.button("🚀 데이터 수집 시작"):
    if url_input:
        with st.spinner("구글 서버에서 정보를 안전하게 가져오는 중..."):
            data = scrape_via_google(url_input)
            
            if data:
                st.success("정보 수집 성공!")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("✅ 수집 결과")
                    final_title = st.text_input("수정된 상품명", data['title'])
                    
                    # 가격이 0으로 나올 경우 직접 입력 유도
                    current_price = int(data['price']) if data['price'].isdigit() else 0
                    final_price = st.number_input("한국 원가(KRW)", value=current_price, step=1000)
                
                with col2:
                    st.subheader("🇸🇬 쇼피 판매가 계산")
                    # 마진 35% + 환율 1000원 가정 (필요시 수정 가능)
                    sgd_price = round((final_price * 1.35) / 1000, 2)
                    st.metric("권장 판매가", f"${sgd_price} SGD")
                    
                # 엑셀 저장용 데이터 구성
                st.divider()
                st.subheader("📊 엑셀 등록용 데이터 미리보기")
                res_df = pd.DataFrame([{
                    "Original Title": data['title'],
                    "Price (KRW)": final_price,
                    "Price (SGD)": sgd_price,
                    "URL": url_input
                }])
                st.table(res_df)
            else:
                st.error("구글 검색 결과에서 정보를 찾지 못했습니다. URL이 정확한지 확인해 주세요.")
    else:
        st.warning("URL을 먼저 입력해 주세요.")

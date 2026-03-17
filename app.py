import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def scrape_ant_engine(target_url):
    """ScraperAnt 엔진을 사용하여 차단을 우회하고 정보를 수집합니다."""
    api_key = st.secrets["ANT_API_KEY"]
    # ScraperAnt API 호출 주소
    api_url = f"https://api.scraperant.com/v2/general?url={target_url}&x-api-key={api_key}&browser=true"
    
    try:
        res = requests.get(api_url, timeout=20)
        if res.status_code != 200:
            return {"title": f"수집 실패 (Error {res.status_code})", "price": "0", "img_url": ""}
        
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 1. 제목 추출 (최적화)
        title = "제목 없음"
        og_title = soup.find("meta", property="og:title")
        if og_title:
            title = og_title['content']
        else:
            title = soup.title.string if soup.title else "제목 없음"
            
        # 2. 가격 추출 (패턴 매칭)
        price = "0"
        # 쿠팡/네이버 등의 가격 태그들 공통 패턴
        price_text = soup.get_text()
        price_match = re.search(r'(\d{1,3}(?:,\d{3})+)', price_text)
        if price_match:
            price = price_match.group(1).replace(",", "")

        # 3. 이미지 추출
        img_url = ""
        og_img = soup.find("meta", property="og:image")
        if og_img:
            img_url = og_img['content']

        return {"title": title, "price": price, "img_url": img_url}
    except Exception as e:
        return {"title": f"연결 오류: {str(e)}", "price": "0", "img_url": ""}

# --- UI ---
st.set_page_config(page_title="Ultimate Sourcing Tool", layout="wide")
st.title("🛡️ 차단 없는 무제한 수집기")

st.info("ScraperAnt 엔진을 사용하여 쿠팡, 네이버, 다이소몰을 뚫습니다.")
url_input = st.text_input("수집할 상품 URL을 입력하세요")

if st.button("🚀 강력 수집 시작"):
    if url_input:
        with st.spinner("전문 엔진이 차단을 우회하여 정보를 가져오는 중..."):
            data = scrape_ant_engine(url_input)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                if data['img_url']:
                    st.image(data['img_url'], use_container_width=True)
            with col2:
                st.subheader("✅ 수집 결과")
                st.write(f"**상품명:** {data['title']}")
                st.write(f"**가격:** {data['price']}원")
                
                # 쇼피 가격 계산 (간단 예시)
                sgd = round((int(data['price']) * 1.3) / 1000, 2)
                st.metric("🇸🇬 쇼피 예상 판매가", f"${sgd} SGD")
    else:
        st.warning("URL을 입력해주세요.")

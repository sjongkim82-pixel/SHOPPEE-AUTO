import streamlit as st
import cloudscraper
from bs4 import BeautifulSoup
import re

def scrape_fast(url):
    """차단 방지 레이어를 입힌 초간단 수집기"""
    try:
        # 브라우저처럼 보이게 해주는 스크래퍼 생성
        scraper = cloudscraper.create_scraper()
        res = scraper.get(url, timeout=10)
        
        if res.status_code != 200:
            return {"title": f"접속 실패 ({res.status_code})", "price": "0", "img_url": ""}
        
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 1. 제목 (og:title 최우선)
        title = "제목 없음"
        og_title = soup.find("meta", property="og:title")
        if og_title:
            title = og_title['content']
        else:
            title = soup.title.string if soup.title else "제목 없음"
            
        # 2. 가격 (숫자 패턴)
        price = "0"
        price_match = re.search(r'(\d{1,3}(?:,\d{3})+)', res.text)
        if price_match:
            price = price_match.group(1).replace(",", "")

        # 3. 이미지
        img_url = ""
        og_img = soup.find("meta", property="og:image")
        if og_img:
            img_url = og_img['content']

        return {"title": title, "price": price, "img_url": img_url}
    except Exception as e:
        return {"title": f"오류 발생: {str(e)}", "price": "0", "img_url": ""}

# --- UI ---
st.set_page_config(page_title="Shopee Sourcing", layout="wide")
st.title("🛡️ 3초 완성 상품 수집기")

url_input = st.text_input("수집할 상품 URL (네이버, 쿠팡 등)")

if st.button("🚀 정보 가져오기"):
    if url_input:
        with st.spinner("정보를 읽어오는 중입니다..."):
            data = scrape_fast(url_input)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                if data['img_url'] and "http" in data['img_url']:
                    st.image(data['img_url'], use_container_width=True)
            with col2:
                st.subheader("✅ 수집 결과")
                st.write(f"**상품명:** {data['title']}")
                st.write(f"**한국 원가:** {data['price']}원")
                
                # 쇼피 싱가포르 가격 (마진 30%, 환율 1000원 기준)
                if data['price'].isdigit():
                    sgd = round((int(data['price']) * 1.3) / 1000, 2)
                    st.metric("🇸🇬 쇼피 예상 판매가", f"${sgd} SGD")
    else:
        st.warning("URL을 입력해 주세요.")

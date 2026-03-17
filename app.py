import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

def scrape_naver_by_f12(url):
    """F12에서 확인된 클래스명을 직접 타격하여 수집"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8"
    }
    
    try:
        # 네이버 차단 방지를 위한 세션 생성
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=10)
        
        if res.status_code != 200:
            return {"error": f"접속 실패 (에러코드: {res.status_code})"}
            
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 1. 상품명 추출 (F12에서 본 h3 태그의 클래스 사용)
        # 클래스명이 바뀔 수 있으므로 여러 후보를 넣었습니다.
        title = "제목 없음"
        title_tag = soup.select_one("h3.DCVBeA8ZB") # 스크린샷 속 바로 그 클래스
        if not title_tag:
            title_tag = soup.select_one("h3._copyable") # 대체 클래스
        
        if title_tag:
            title = title_tag.get_text().strip()

        # 2. 가격 추출 (스크린샷 속 span 클래스 e1DMQNBPJ_)
        price = "0"
        price_tag = soup.select_one("span.e1DMQNBPJ_")
        if not price_tag:
            # 가격 정보가 숨겨진 다른 위치 탐색
            price_tag = soup.find("span", string=lambda x: x and "199,000" in x) 
        
        if price_tag:
            price = price_tag.get_text().replace(",", "").strip()

        return {
            "title": title,
            "price": price
        }
        
    except Exception as e:
        return {"error": f"수집 실패: {str(e)}"}

# --- UI ---
st.title("🎯 F12 정밀 타격 수집기")
st.info("스크린샷의 HTML 구조를 분석하여 데이터를 추출합니다.")

url_input = st.text_input("수집할 네이버 상품 URL")

if st.button("데이터 뽑아오기"):
    if url_input:
        with st.spinner("네이버 서버에서 정보를 찾는 중..."):
            data = scrape_naver_by_f12(url_input)
            
            if "error" in data:
                st.error(data["error"])
                st.write("네이버가 일시적으로 IP를 차단했을 수 있습니다. 1분 뒤 다시 시도해 주세요.")
            else:
                st.success("정보 추출 성공!")
                st.subheader(f"📦 상품명: {data['title']}")
                st.write(f"**수집 원가:** {data['price']}원")
                
                # 쇼피 계산 (환율 1,000원 기준)
                if data['price'].isdigit():
                    sgd = round((int(data['price']) * 1.35) / 1000, 2)
                    st.metric("🇸🇬 쇼피 예상가", f"${sgd} SGD")
    else:
        st.warning("URL을 입력해 주세요.")

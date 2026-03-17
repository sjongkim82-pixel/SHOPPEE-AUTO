import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def get_driver():
    """브라우저 설정 (차단 방지 옵션 포함)"""
    options = Options()
    options.add_argument("--headless") # 화면 없이 실행
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrape_with_browser(url):
    driver = get_driver()
    try:
        driver.get(url)
        time.sleep(3) # 페이지 로딩 대기
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # 1. 제목 추출 (다양한 쇼핑몰 공통 메타데이터 활용)
        title = "정보 없음"
        title_tag = soup.find("meta", property="og:title")
        if title_tag:
            title = title_tag['content']
        else:
            title = soup.title.string if soup.title else "제목 없음"

        # 2. 가격 추출 (숫자 패턴 찾기)
        import re
        page_text = soup.get_text()
        # '원' 앞의 숫자나 가격처럼 보이는 패턴 추출
        price_matches = re.findall(r'(\d{1,3}(?:,\d{3})+)', page_text)
        price = price_matches[0].replace(",", "") if price_matches else "0"

        # 3. 이미지 추출
        img_url = ""
        img_tag = soup.find("meta", property="og:image")
        if img_tag:
            img_url = img_tag['content']

        return {"title": title, "price": price, "img_url": img_url}
    except Exception as e:
        return {"title": f"수집 실패: {str(e)}", "price": "0", "img_url": ""}
    finally:
        driver.quit()

# --- UI ---
st.set_page_config(page_title="Universal Crawler", layout="wide")
st.title("🌐 무제한 URL 정보 수집기 (No AI)")

url_input = st.text_input("수집할 상품 URL을 입력하세요 (쿠팡, 네이버, 다이소 등)")

if st.button("강력 수집 시작"):
    if url_input:
        with st.spinner("브라우저를 실행하여 정보를 읽어오는 중..."):
            data = scrape_with_browser(url_input)
            
            if "http" in data['img_url']:
                st.image(data['img_url'], width=300)
            
            st.subheader("📋 수집 데이터")
            st.write(f"**상품명:** {data['title']}")
            st.write(f"**가격:** {data['price']}원")
            
            st.success("AI 한도 소모 없이 수집에 성공했습니다!")
    else:
        st.warning("URL을 입력해 주세요.")

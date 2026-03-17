import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# 네이버 스마트스토어 정보 수집 함수
def scrape_naver(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return {"title": "접속 실패", "price": 0, "img_url": ""}
        
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 상품명 추출 (다양한 네이버 테마 대응)
        title = "상품명 없음"
        title_tag = soup.select_one("h3._22u_hy7H9V") or soup.select_one("h3")
        if title_tag:
            title = title_tag.text.strip()
        
        # 가격 추출
        price = 0
        price_tag = soup.select_one("span._1LY7CqU9sN") or soup.select_one(".price_real")
        if price_tag:
            price_text = price_tag.text.replace(",", "").replace("원", "").strip()
            price = int(price_text) if price_text.isdigit() else 0
        
        # 이미지 URL 추출
        img_url = ""
        img_tag = soup.select_one("img._27_2_y8Y_q") or soup.select_one("._25_r8_97-X img")
        if img_tag and img_tag.has_attr('src'):
            img_url = img_tag['src']
        
        return {"title": title, "price": price, "img_url": img_url}
    except Exception as e:
        return {"title": f"에러: {str(e)}", "price": 0, "img_url": ""}

# --- UI 레이아웃 ---
st.set_page_config(page_title="Shopee Auto Tool", layout="wide")
st.title("🕵️‍♂️ Shopee Search & Collect")

urls_input = st.text_area("수집할 네이버 스마트스토어 URL을 한 줄에 하나씩 입력하세요", height=150)

if st.button("데이터 수집 시작"):
    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]
    
    if not urls:
        st.warning("URL을 먼저 입력해주세요.")
    else:
        results = []
        progress_bar = st.progress(0)
        
        for i, url in enumerate(urls):
            with st.spinner(f"상품 수집 중... ({i+1}/{len(urls)})"):
                data = scrape_naver(url)
                data['url'] = url
                results.append(data)
                time.sleep(1.2) # 네이버 차단 방지용 딜레이
            progress_bar.progress((i + 1) / len(urls))
            
        st.subheader("✅ 수집 결과 미리보기")
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
        
        # 수집된 데이터를 세션에 저장 (나중에 엑셀 만들 때 사용)
        st.session_state['scraped_df'] = df

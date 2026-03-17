import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

def scrape_universal(url):
    """검색 엔진용 메타 데이터를 긁어오는 범용 수집기"""
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return {"title": f"접속 실패({res.status_code})", "price": 0, "img_url": ""}
        
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 1. 메타 데이터에서 제목 찾기
        title = "제목 없음"
        title_tag = soup.find("meta", property="og:title") or soup.find("title")
        if title_tag:
            title = title_tag.get("content", title_tag.text).split(":")[0].strip()

        # 2. 메타 데이터에서 이미지 찾기
        img_url = ""
        img_tag = soup.find("meta", property="og:image")
        if img_tag:
            img_url = img_tag.get("content", "")

        # 3. 가격 찾기 (네이버 쇼핑 특화 데이터 파싱)
        price = 0
        # 스크립트 내에 숨겨진 가격 데이터 찾기 시도
        if "price" in res.text:
            import re
            price_match = re.search(r'"price":"(\d+)"', res.text) or re.search(r'priceContent":"([\d,]+)', res.text)
            if price_match:
                price = int(price_match.group(1).replace(",", ""))

        return {"title": title, "price": price, "img_url": img_url}
    except Exception as e:
        return {"title": f"에러: {str(e)}", "price": 0, "img_url": ""}

# --- UI 설정 ---
st.set_page_config(page_title="Shopee Auto Tool", layout="wide")
st.title("🕵️‍♂️ Shopee Search & Collect (Universal)")

urls_input = st.text_area("수집할 상품 URL (네이버, 일반 쇼핑몰 등)을 입력하세요", height=150)

if st.button("데이터 수집 시작"):
    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]
    
    if not urls:
        st.warning("URL을 먼저 입력해주세요.")
    else:
        results = []
        progress_bar = st.progress(0)
        
        for i, url in enumerate(urls):
            with st.spinner(f"AI 수집 엔진 가동 중... ({i+1}/{len(urls)})"):
                data = scrape_universal(url)
                data['url'] = url
                results.append(data)
                time.sleep(2) # 차단 방지를 위해 조금 더 천천히
            progress_bar.progress((i + 1) / len(urls))
            
        st.subheader("✅ 수집 결과 미리보기")
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
        st.session_state['scraped_df'] = df

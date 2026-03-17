import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import re

# Gemini 설정
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def get_product_info_ai(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 페이지에서 텍스트와 이미지 태그만 추출해서 AI에게 전달
        page_content = soup.get_text()[:3000] # 너무 길면 잘림
        img_tags = [img['src'] for img in soup.find_all('img', src=True) if 'product' in img['src'] or 'goods' in img['src']][:5]
        
        prompt = f"""
        아래는 어느 쇼핑몰의 상품 페이지 내용이야. 
        여기서 1.상품명, 2.정확한 판매가격(숫자만), 3.대표 상품 이미지 URL을 찾아서 
        형식에 맞춰 대답해줘. 다른 말은 하지마.
        
        형식: 상품명|가격|이미지URL
        내용: {page_content}
        이미지후보: {img_tags}
        """
        
        response = model.generate_content(prompt)
        ai_res = response.text.strip().split('|')
        
        return {
            "title": ai_res[0] if len(ai_res) > 0 else "실패",
            "price": ai_res[1] if len(ai_res) > 1 else "0",
            "img_url": ai_res[2] if len(ai_res) > 2 else ""
        }
    except Exception as e:
        return {"title": f"에러: {str(e)}", "price": "0", "img_url": ""}

# --- UI ---
st.title("🚀 AI 기반 쇼피 소싱 마스터")

url_input = st.text_input("상품 URL을 입력하세요 (다이소, 네이버 등)")

if st.button("AI로 정보 긁어오기"):
    if url_input:
        with st.spinner("AI가 페이지 분석 중..."):
            data = get_product_info_ai(url_input)
            st.success("수집 완료!")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                if data['img_url']:
                    st.image(data['img_url'], width=200)
            with col2:
                st.write(f"**상품명:** {data['title']}")
                st.write(f"**가격:** {data['price']}원")
    else:
        st.warning("URL을 입력해주세요.")

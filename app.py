import streamlit as st
import requests
import re
import json

def get_naver_product_data(url):
    """네이버 스마트스토어의 숨겨진 JSON 데이터 API를 직접 호출"""
    try:
        # 1. URL에서 상품 번호(Product ID) 추출
        product_id_match = re.search(r'/products/(\count_digits\d+)', url)
        if not product_id_match:
            # 11730189206 같은 형태가 아닐 경우 대비
            product_id_match = re.search(r'products/(\d+)', url)
            
        if not product_id_match:
            return {"error": "상품 번호를 찾을 수 없는 URL입니다."}
            
        product_id = product_id_match.group(1)
        
        # 2. 네이버 내부 API 주소로 직접 요청 (F12에서 확인되는 그 주소)
        api_url = f"https://smartstore.naver.com/i/v1/contents/pc/products/{product_id}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # F12에서 보셨던 데이터 구조대로 파싱
            product_name = data.get('base', {}).get('name', "제목 없음")
            sale_price = data.get('base', {}).get('salePrice', 0)
            rep_image = data.get('base', {}).get('representativeImageUrl', "")
            
            return {
                "title": product_name,
                "price": sale_price,
                "img_url": rep_image
            }
        else:
            return {"error": f"네이버 API 응답 에러 ({response.status_code})"}
            
    except Exception as e:
        return {"error": f"수집 중 오류 발생: {str(e)}"}

# --- UI ---
st.set_page_config(page_title="Naver Specialist", layout="wide")
st.title("🎯 네이버 스마트스토어 전용 정밀 수집기")
st.markdown("F12 개발자 도구에 나타나는 **실제 원본 데이터**를 직접 추출합니다.")

target_url = st.text_input("네이버 스마트스토어 주소를 입력하세요")

if st.button("데이터 정밀 추출"):
    if target_url:
        with st.spinner("비밀 API 통로로 데이터 가져오는 중..."):
            result = get_naver_product_data(target_url)
            
            if "error" in result:
                st.error(result["error"])
            else:
                col1, col2 = st.columns([1, 2])
                with col1:
                    if result["img_url"]:
                        st.image(result["img_url"], use_container_width=True)
                with col2:
                    st.success("데이터 추출 성공!")
                    st.subheader(f"📦 {result['title']}")
                    st.write(f"**실제 판매가:** {result['price']:,}원")
                    
                    # 쇼피 계산기
                    sgd = round((result['price'] * 1.35) / 1000, 2)
                    st.metric("🇸🇬 쇼피 예상가", f"${sgd} SGD")
    else:
        st.warning("URL을 입력해주세요.")

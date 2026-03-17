import streamlit as st
import requests
import re
import time

def get_naver_product_data_stealth(url):
    """네이버의 차단을 피하기 위해 더 정교하게 위장하여 호출"""
    product_id_match = re.search(r'products/(\d+)', url)
    if not product_id_match:
        return {"error": "네이버 상품 번호를 찾을 수 없습니다."}
    
    p_id = product_id_match.group(1)
    api_url = f"https://smartstore.naver.com/i/v1/contents/pc/products/{p_id}"
    
    # 실제 사람이 크롬 브라우저를 쓰는 것처럼 속이는 '위장막'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": url, # 어디서 왔는지 알려줌 (중요!)
        "Cache-Control": "no-cache"
    }
    
    try:
        # 네이버가 의심하지 않게 1초 정도 쉬었다가 요청 (매너)
        time.sleep(1)
        res = requests.get(api_url, headers=headers, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            base = data.get('base', {})
            return {
                "title": base.get('name'),
                "price": base.get('salePrice'),
                "img": base.get('representativeImageUrl')
            }
        elif res.status_code == 429:
            return {"error": "네이버가 잠시 문을 닫았습니다(429). 1~2분 뒤에 다시 시도하거나, 주소창의 URL을 다시 확인해주세요."}
        else:
            return {"error": f"네이버 응답 에러: {res.status_code}"}
            
    except Exception as e:
        return {"error": f"연결 실패: {str(e)}"}

# --- UI ---
st.title("🎯 네이버 차단 우회 수집기")
url_input = st.text_input("네이버 스마트스토어 URL 입력")

if st.button("데이터 추출 시작"):
    if url_input:
        with st.spinner("네이버 보안망을 조심스럽게 통과 중..."):
            result = get_naver_product_data_stealth(url_input)
            
            if "error" in result:
                st.error(result["error"])
                st.info("💡 팁: 네이버는 너무 자주 요청하면 막힙니다. 잠시 쉬었다가 시도해 보세요!")
            else:
                st.success("데이터 추출 성공!")
                st.subheader(result["title"])
                st.write(f"**수집 원가:** {result['price']:,}원")
                
                # 쇼피 환율 계산
                sgd = round((result['price'] * 1.35) / 1000, 2)
                st.metric("🇸🇬 쇼피 권장 판매가", f"${sgd} SGD")

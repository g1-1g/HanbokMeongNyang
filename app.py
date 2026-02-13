import streamlit as st
from openai import OpenAI
import base64
from io import BytesIO
from PIL import Image
import requests

# 페이지 설정
st.set_page_config(
    page_title="반려동물 한복 입히기",
    page_icon="👘",
    layout="wide"
)

# 스타일 CSS
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #8B4513;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .sub-title {
        text-align: center;
        color: #A0522D;
        font-size: 1.2em;
        margin-bottom: 30px;
    }
    .keyword-section {
        background-color: #FFF8DC;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# 메인 타이틀
st.markdown('<p class="main-title">🐕 반려동물 한복 입히기 👘🐱</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">AI가 당신의 반려동물에게 멋진 한복을 입혀드립니다</p>', unsafe_allow_html=True)

# 시크릿 키에서 API 키 로드
api_key = st.secrets["API_KEY"]

# 사이드바
with st.sidebar:
    st.header("⚙️ 설정")
    st.markdown("### 📖 사용 방법")
    st.markdown("""
    1. 반려동물 사진 업로드
    2. 원하는 한복 스타일 선택
    3. '한복 입히기' 버튼 클릭
    4. 생성된 이미지 다운로드
    """)

# 키워드 옵션 정의
keyword_options = {
    "동물 종류": {
        "강아지 🐕": "cute puppy dog",
        "고양이 🐱": "cute cat",
        "포메라니안": "Pomeranian dog",
        "치와와": "Chihuahua dog",
        "웰시코기": "Welsh Corgi dog",
        "진돗개": "Jindo dog",
        "페르시안 고양이": "Persian cat",
        "스코티시폴드": "Scottish Fold cat",
        "러시안블루": "Russian Blue cat",
        "샴 고양이": "Siamese cat"
    },
    "성별": {
        "남자 한복 (남아)": "male",
        "여자 한복 (여아)": "female"
    },
    "한복 스타일": {
        "왕족 👑": "royal Korean king/queen hanbok with elaborate gold patterns and jade accessories",
        "세자/공주 ✨": "Korean prince/princess hanbok with elegant silk and jeweled ornaments",
        "양반 🎋": "noble scholar yangban hanbok with refined patterns and traditional hat",
        "신랑신부 💒": "traditional Korean wedding hanbok with vibrant colors and ceremonial decorations",
        "궁녀 🌸": "palace court lady hanbok with simple elegant design and traditional hairpin",
        "무관 ⚔️": "Korean military officer hanbok with armor-inspired details",
        "기생 🎭": "Korean courtesan gisaeng hanbok with artistic patterns and accessories",
        "평민 🌾": "common people hanbok with simple cotton fabric and minimal decoration"
    },
    "색상 조합": {
        "홍청 (빨강+파랑) 🔴🔵": "red and blue traditional colors",
        "분홍+연두 🌸💚": "pink and light green soft colors",
        "보라+노랑 💜💛": "purple and yellow royal colors",
        "흰색+금색 🤍✨": "white and gold elegant colors",
        "검정+금색 🖤✨": "black and gold sophisticated colors",
        "연두+살구 💚🍑": "light green and apricot spring colors",
        "하늘+연분홍 ☁️🌸": "sky blue and light pink soft colors"
    },
    "장신구": {
        "화려한 금관 👑": "elaborate golden crown with jewels",
        "전통 갓 🎩": "traditional Korean gat hat",
        "댕기/비녀 💎": "traditional Korean hair ribbon daenggi or binyeo hairpin",
        "노리개 🎀": "traditional Korean norigae ornamental tassel",
        "꽃 장식 🌺": "flower decorations in hair",
        "장신구 없음": "no accessories, simple and clean"
    },
    "분위기": {
        "위엄있고 당당함 🦁": "dignified and majestic atmosphere",
        "우아하고 품위있음 🦢": "elegant and graceful atmosphere",
        "귀엽고 사랑스러움 🥰": "cute and adorable atmosphere",
        "화려하고 눈부심 ✨": "gorgeous and dazzling atmosphere",
        "단아하고 차분함 🌿": "refined and calm atmosphere",
        "발랄하고 생기있음 🌈": "lively and vibrant atmosphere"
    }
}

# 메인 컨텐츠
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="keyword-section">', unsafe_allow_html=True)
    st.subheader("📸 반려동물 사진 (필수)")
    uploaded_file = st.file_uploader(
        "한복을 입힐 반려동물 사진을 업로드하세요",
        type=['png', 'jpg', 'jpeg'],
        help="원본 사진에 한복을 합성합니다"
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 사진", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 키워드 선택
    st.markdown('<div class="keyword-section">', unsafe_allow_html=True)
    st.subheader("🎨 한복 스타일 선택")

    selected_keywords = {}

    for category, options in keyword_options.items():
        st.markdown(f"**{category}**")
        selected_keywords[category] = st.selectbox(
            f"선택_{category}",
            options=list(options.keys()),
            label_visibility="collapsed",
            key=category
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # 추가 커스텀 프롬프트
    st.markdown('<div class="keyword-section">', unsafe_allow_html=True)
    st.subheader("✍️ 추가 요청사항 (선택)")
    custom_prompt = st.text_area(
        "원하는 추가 스타일이나 요청사항을 입력하세요",
        placeholder="예: 벚꽃 배경, 달빛 아래, 궁궐 앞 등",
        height=100
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="keyword-section">', unsafe_allow_html=True)
    st.subheader("🎨 생성될 이미지 미리보기")

    # 선택된 키워드 요약
    st.markdown("**선택한 스타일:**")
    for category, selected in selected_keywords.items():
        st.markdown(f"- **{category}:** {selected}")

    if custom_prompt:
        st.markdown(f"- **추가 요청:** {custom_prompt}")

    st.markdown('</div>', unsafe_allow_html=True)

    # 이미지 생성 버튼
    if st.button("🎨 한복 입히기!", type="primary", use_container_width=True):
        with st.spinner("✨ AI가 한복을 입히는 중입니다... 잠시만 기다려주세요!"):
            try:
                # OpenAI 클라이언트 초기화
                client = OpenAI(api_key=api_key)

                # 프롬프트 구성
                animal_type = keyword_options["동물 종류"][selected_keywords["동물 종류"]]
                gender = keyword_options["성별"][selected_keywords["성별"]]
                hanbok_style = keyword_options["한복 스타일"][selected_keywords["한복 스타일"]]
                color_scheme = keyword_options["색상 조합"][selected_keywords["색상 조합"]]
                accessories = keyword_options["장신구"][selected_keywords["장신구"]]
                atmosphere = keyword_options["분위기"][selected_keywords["분위기"]]

                # 최종 프롬프트 (원본 유지 + 한복만 입히기)
                prompt = f"""A realistic phGoogle Imagen 3oto of a {animal_type} wearing a traditional Korean hanbok.
Do NOT change the pet's face, body shape, or pose. Only add hanbok clothing naturally onto the pet.
Keep the background simple and plain. Do not add any fantasy or dramatic elements.

Hanbok: {gender} style, {hanbok_style}
Colors: {color_scheme}
Accessories: {accessories}

{f'Additional request: {custom_prompt}' if custom_prompt else ''}

The result should look like a natural photo of the pet simply dressed in hanbok, not an artistic illustration."""

                # DALL-E-3로 이미지 생성
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    quality="hd",
                    n=1,
                )

                image_url = response.data[0].url

                # 이미지 다운로드
                image_response = requests.get(image_url)
                generated_image = Image.open(BytesIO(image_response.content))

                # 결과 표시
                st.success("✅ 한복 입히기 완료!")
                st.image(generated_image, caption="생성된 이미지", use_container_width=True)

                # 이미지 다운로드 버튼
                buf = BytesIO()
                generated_image.save(buf, format="PNG")
                byte_im = buf.getvalue()

                st.download_button(
                    label="📥 이미지 다운로드",
                    data=byte_im,
                    file_name="hanbok_pet.png",
                    mime="image/png",
                    use_container_width=True
                )

                # 생성에 사용된 프롬프트 표시 (접기)
                with st.expander("🔍 생성에 사용된 상세 프롬프트 보기"):
                    st.code(prompt, language="text")

            except Exception as e:
                st.error(f"❌ 이미지 생성 중 오류가 발생했습니다: {str(e)}")
                st.info("API 키가 올바른지, 그리고 충분한 크레딧이 있는지 확인해주세요.")

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>🎨 OpenAI DALL-E-3를 활용한 반려동물 한복 생성기</p>
    <p>Made with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)

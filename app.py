import streamlit as st
from openai import OpenAI
import base64
from io import BytesIO
from PIL import Image
import requests

# 페이지 설정
st.set_page_config(
    page_title="반려동물 한복 입히기",
    page_icon="🐕🐱",
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
    /* 라디오 버튼 가로 정렬 */
    div[role="radiogroup"] {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }
    div[role="radiogroup"] label {
        background-color: #ffffff;
        border: 3px solid #DDD;
        border-radius: 20px;
        padding: 6px 16px;
        cursor: pointer;
        transition: all 0.2s;
    }
    div[role="radiogroup"] label:hover {
        background-color: #ffffff;
        border-color: #fe786b;
    }
    div[role="radiogroup"] label[data-checked="true"],
    div[role="radiogroup"] label:has(input:checked) {
        background-color: #ffffff;
        color: white;
        border-color: #fe786b;
    }
    </style>
""", unsafe_allow_html=True)

# 메인 타이틀
st.markdown('<p class="main-title">🐕 반려동물 한복 입히기 👘🐱</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">AI가 당신의 반려동물에게 멋진 한복을 입혀드립니다</p>', unsafe_allow_html=True)

# 시크릿 키에서 API 키 로드
api_key = st.secrets["API_KEY"]

# 키워드 옵션 정의
keyword_options = {
    "동물 종류": {
        "강아지 🐕": "cute puppy dog",
        "고양이 🐱": "cute cat",
    },
    "성별": {
        "남자 한복 (남아)": "male",
        "여자 한복 (여아)": "female"
    },
    "한복 스타일": {
        "세자/공주 ✨": "Korean prince/princess hanbok with elegant silk and jeweled ornaments",
        "왕족 👑": "royal Korean king/queen hanbok with elaborate gold patterns and jade accessories",
        "신랑신부 💒": "traditional Korean wedding hanbok with vibrant colors and ceremonial decorations",
        "무관 ⚔️": "Korean military officer hanbok with armor-inspired details",
        "돌쇠 🪵": "traditional Korean servant (dolssoe) hanbok with simple cotton fabric, rolled sleeves, waist belt, straw shoes, and rustic countryside vibe"
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
        "장신구 없음": "no accessories, simple and clean",
        "화려한 금관 👑": "elaborate golden crown with jewels",
        "전통 갓 🎩": "traditional Korean gat hat",
        "댕기/비녀 💎": "traditional Korean hair ribbon daenggi or binyeo hairpin",
        "노리개 🎀": "traditional Korean norigae ornamental tassel",
        "꽃 장식 🌺": "flower decorations in hair",
    },
    "분위기": {
        "귀엽고 사랑스러움 🥰": "cute and adorable atmosphere",
        "위엄있고 당당함 🦁": "dignified and majestic atmosphere",
        "우아하고 품위있음 🦢": "elegant and graceful atmosphere",
        "화려하고 눈부심 ✨": "gorgeous and dazzling atmosphere",
        "단아하고 차분함 🌿": "refined and calm atmosphere",
        "발랄하고 생기있음 🌈": "lively and vibrant atmosphere"
    }
}

# 사진 업로드
st.subheader("📸 반려동물 사진 (필수)")
uploaded_file = st.file_uploader(
    "한복을 입힐 반려동물 사진을 업로드하세요",
    type=['png', 'jpg', 'jpeg'],
    help="원본 사진에 한복을 합성합니다"
)
if uploaded_file:
    image = Image.open(uploaded_file)

st.markdown("---")

# 키워드 선택 (라디오 버튼)
st.subheader("🎨 한복 스타일 선택")

selected_keywords = {}

for category, options in keyword_options.items():
    selected_keywords[category] = st.radio(
        category,
        options=list(options.keys()),
        horizontal=True,
        key=category
    )

st.markdown("---")

# 추가 요청사항
st.subheader("✍️ 추가 요청사항 (선택)")
custom_prompt = st.text_area(
    "원하는 추가 스타일이나 요청사항을 입력하세요",
    placeholder="예: 벚꽃 배경, 달빛 아래, 궁궐 앞 등",
    height=100
)

# 생성 버튼
if st.button("🎨 한복 입히기!", type="primary", use_container_width=True):
    if not uploaded_file:
        st.warning("⚠️ 반려동물 사진을 먼저 업로드해주세요!")
    else:
        with st.spinner("✨ 한복을 입히는 중입니다..."):
            try:
                client = OpenAI(api_key=api_key)

                animal_type = keyword_options["동물 종류"][selected_keywords["동물 종류"]]
                gender = keyword_options["성별"][selected_keywords["성별"]]
                hanbok_style = keyword_options["한복 스타일"][selected_keywords["한복 스타일"]]
                color_scheme = keyword_options["색상 조합"][selected_keywords["색상 조합"]]
                accessories = keyword_options["장신구"][selected_keywords["장신구"]]
                atmosphere = keyword_options["분위기"][selected_keywords["분위기"]]

                prompt = f"""
    Edit this image.

    STRICT RULES:
    Add a realistic traditional Korean hanbok outfit to this pet.
    Preserve the original face, fur texture, lighting, and photo realism.
    Do not redraw the face.
    Only modify the clothing area.
    Keep the image photographic and natural.
    Do not change the background.
    Keep original lighting and shadows.

    Hanbok style: {gender}, {hanbok_style}
    Color: {color_scheme}
    Accessories: {accessories}
    Atmosphere: {atmosphere}

    {custom_prompt if custom_prompt else ""}
    """

                # 업로드 이미지를 바이트로 변환
                buffered = BytesIO()
                image.convert("RGB").save(buffered, format="PNG")
                buffered.seek(0)

                response = client.images.edit(
                    model="gpt-image-1-mini",
                    image=("pet.png", buffered, "image/png"),
                    prompt=prompt,
                )

                image_base64 = response.data[0].b64_json
                generated_image = Image.open(BytesIO(base64.b64decode(image_base64)))

                st.success("✅ 한복 입히기 완료!")
                st.image(generated_image, use_container_width=True)

            except Exception as e:
                st.error(f"❌ 오류 발생: {str(e)}")

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>🎨 반려동물 한복 입히기 </p>
</div>
""", unsafe_allow_html=True)

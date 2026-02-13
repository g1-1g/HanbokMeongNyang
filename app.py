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
        font-size: 4em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .sub-title {
        text-align: center;
        color: #A0522D;
        font-size: 1.5em;
        margin-bottom: 30px;
    }
    /* 라디오 라벨 글자 크기 */
    div[role="radiogroup"] label span {
        font-size: 1.1em;
    }
    /* subheader 크기 */
    h3 {
        font-size: 1.6em !important;
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

# 메인 타이틀 + 사진 업로드
st.markdown('<p class="main-title">🐕 멍냥 한복 대여소 👘🐱</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">당신의 반려동물에게 멋진 한복을 입혀드립니다</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "📸 한복을 입힐 반려동물 사진을 업로드하세요",
    type=['png', 'jpg', 'jpeg'],
)
if uploaded_file:
    image = Image.open(uploaded_file)

st.markdown("---")

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
    "색상 선택": {
    "흰색 🤍": "white",
    "금색 ✨": "gold",
    "하늘색 ☁️": "sky blue",
    "연분홍 🌸": "light pink",
    "빨강 🔴": "red",
    "파랑 🔵": "blue",
    "연두 💚": "light green",
    "보라 💜": "purple",
    "노랑 💛": "yellow",
    "검정 🖤": "black",
    "살구 🍑": "apricot"
},
}

# 좌우 2컬럼 레이아웃
left_col, right_col = st.columns([1, 1])

with left_col:
    # 키워드 선택 (라디오 버튼)
    st.subheader("🎨 한복 스타일 선택")

    selected_keywords = {}

    for category, options in keyword_options.items():
        if category == "색상 선택":
            selected_keywords[category] = st.multiselect(
                "한복 색상 (색상 조합 가능)",
                options=list(options.keys()),
                key=category
            )
        else:
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
            with right_col:
                result_placeholder = st.empty()
                with st.spinner("✨ 환복 중입니다... 잠시만 기다려주세요!"):
                    try:
                        client = OpenAI(api_key=api_key)

                        animal_type = keyword_options["동물 종류"][selected_keywords["동물 종류"]]
                        gender = keyword_options["성별"][selected_keywords["성별"]]
                        hanbok_style = keyword_options["한복 스타일"][selected_keywords["한복 스타일"]]
                        selected_colors = selected_keywords["색상 선택"]

                        if selected_colors:
                            color_list = [keyword_options["색상 선택"][c] for c in selected_colors]
                            color_scheme = ", ".join(color_list)
                        else:
                            color_scheme = "soft pastel colors"

                        prompt = f"""
    Carefully edit this photo.

    This is a clothing overlay task.
    
    CRITICAL INSTRUCTIONS:
    - Keep the exact same pose, body position, camera angle, framing, and proportions.
    - Do NOT change the face in any way.
    - Do NOT change the eyes, nose, mouth, fur texture, or expression.
    - Do NOT change the background.
    - Do NOT change lighting or shadows.
    - Do NOT alter the pet's anatomy or body shape.
    - Only add clothing on top of the existing body.
    - Think of it as dressing the pet, not redrawing it.
    
    Edit area restriction:
    Modify pixels ONLY where the hanbok fabric would naturally exist.
    All other pixels must remain identical to the original image.
    
    Add a realistic traditional Korean hanbok:
    Style: {gender}, {hanbok_style}
    Color: {color_scheme}
    Accessories: match with {hanbok_style}
    Atmosphere: cute and lovely


    {custom_prompt if custom_prompt else ""}
    
    The final result must look like the original photo, 
    with the pet naturally wearing a hanbok.
    The output must look like the original image with clothes composited onto it, not a newly generated image.
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

                    except Exception as e:
                        generated_image = None
                        st.error(f"❌ 오류 발생: {str(e)}")

                # spinner 끝난 후 결과 표시
                if generated_image:
                    result_placeholder.image(generated_image, caption="생성된 이미지", use_container_width=True)

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p> meongnyanghanbok </p>
</div>
""", unsafe_allow_html=True)

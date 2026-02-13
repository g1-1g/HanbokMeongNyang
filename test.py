import os
from openai import OpenAI
import streamlit as st

api_key = st.secrets["API_KEY"]

client = OpenAI(
    api_key=api_key,
)

st.title('🎁 제품 홍보 포스터 생성기')
keyword = st.text_input("키워드를 입력하세요.")

if st.button('생성하기🔥'):
    with st.spinner('생성 중입니다.'):
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "입력 받은 키워드에 대한 150자 이내의 솔깃한 제품 홍보 문구를 작성해줘.",
                },
                {
                    "role": "user",
                    "content": keyword,
                }

            ],
            model="gpt-4o-mini",
        )

        result = chat_completion.choices[0].message.content
        st.write(result)
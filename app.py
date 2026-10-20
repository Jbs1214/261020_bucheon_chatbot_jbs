import os
from importlib import import_module

import streamlit as st

# 배포 환경(Streamlit Cloud)에서는 .env 대신 Secrets에서 키를 가져온다
for key in ("GROQ_API_KEY", "GEMINI_API_KEY"):
    try:
        if key in st.secrets:
            os.environ[key] = st.secrets[key]
    except Exception:
        pass  # 로컬에 secrets.toml이 없으면 .env를 사용

# 모듈 이름이 숫자로 시작해서 import_module로 불러온다
bot = import_module("261020_bucheon_chatbot_jbs")

CHEF = "👨‍🍳"
GREETING = "음... 어서 오세요. 가지고 계신 재료를 말씀해 주시면 됩니다."
EXAMPLES = ["계란, 김치, 대파", "닭가슴살, 양파, 간장", "두부, 애호박, 참치캔", "감자, 베이컨, 우유"]

st.set_page_config(page_title="최강록의 부엌", page_icon="🥢", layout="centered")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600;700&display=swap');
    html, body, [class*="css"], .stMarkdown, button, input, textarea {
        font-family: 'Noto Serif KR', serif !important;
    }
    #MainMenu, footer {visibility: hidden;}
    .block-container {padding-top: 2.5rem; max-width: 720px;}
    .hero {text-align: center; padding: 0.5rem 0 1.2rem; border-bottom: 1px solid #3a342d;
           margin-bottom: 1.2rem;}
    .hero .sub {letter-spacing: 0.35em; font-size: 0.8rem; color: #C8772E; margin: 0;}
    .hero h1 {font-size: 2.2rem; font-weight: 700; margin: 0.3rem 0 0.4rem;}
    .hero .desc {color: #9c9183; font-size: 0.95rem; margin: 0;}
    [data-testid="stChatMessage"] {
        background: #1F1D1B; border: 1px solid #332e28; border-left: 3px solid #C8772E;
        border-radius: 4px; padding: 0.9rem 1.1rem; margin-bottom: 0.7rem;
    }
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li {line-height: 1.85;}
    .stButton > button {border-radius: 2px; border: 1px solid #4a4238; background: transparent;}
    .stButton > button:hover {border-color: #C8772E; color: #C8772E;}
    </style>
    """,
    unsafe_allow_html=True,
)


def new_chat():
    st.session_state.messages = [{"role": "system", "content": bot.SYSTEM_PROMPT}]


if "messages" not in st.session_state:
    new_chat()

# ---------- 사이드바 ----------
with st.sidebar:
    st.header("🥢 최강록의 부엌")
    st.write("냉장고에 있는 재료를 말씀해 주시면, 만들 수 있는 요리 하나를 골라 드립니다.")
    st.button("새 대화 시작", on_click=new_chat, use_container_width=True)
    st.caption("재료를 구체적으로 적으실수록 정확합니다.")
    st.caption("※ 흑백요리사 최강록 셰프의 말투를 AI가 흉내 낸 챗봇입니다.")

# ---------- 헤더 ----------
st.markdown(
    '<div class="hero"><p class="sub">흑 백 요 리 사</p><h1>최강록의 부엌</h1>'
    '<p class="desc">음... 오늘은 뭘 해 드실지, 천천히 생각해 보겠습니다</p></div>',
    unsafe_allow_html=True,
)

history = [m for m in st.session_state.messages if m["role"] != "system"]
picked = None

with st.chat_message("assistant", avatar=CHEF):
    st.write(GREETING)

# 첫 화면에서는 예시 재료를 버튼으로 보여준다
if not history:
    st.caption("이런 재료는 어떠세요")
    cols = st.columns(2)
    for n, ex in enumerate(EXAMPLES):
        if cols[n % 2].button(ex, key=f"ex{n}", use_container_width=True):
            picked = ex

for m in history:
    is_bot = m["role"] == "assistant"
    with st.chat_message(m["role"], avatar=CHEF if is_bot else "🧑"):
        st.markdown(m["content"])

# ---------- 입력 처리 ----------
q = st.chat_input("냉장고에 뭐가 있으신가요") or picked
if q:
    with st.chat_message("user", avatar="🧑"):
        st.markdown(q)
    st.session_state.messages.append({"role": "user", "content": q})

    with st.chat_message("assistant", avatar=CHEF):
        status = st.empty()
        status.caption("음... 졸이는 중입니다")

        def chunks():
            # 첫 글자가 오면 대기 문구를 지우고 이어서 흘려보낸다
            for text in bot.ask_stream(st.session_state.messages):
                status.empty()
                yield text

        try:
            answer = st.write_stream(chunks())
        except Exception as e:
            status.empty()
            st.session_state.messages.pop()  # 실패한 질문은 기록에서 뺀다
            st.error(f"오류: {e}")
            st.stop()
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()

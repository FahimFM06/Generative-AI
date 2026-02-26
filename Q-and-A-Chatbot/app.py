import os
import base64
from pathlib import Path
import streamlit as st

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# ----------------------------
# Basic app setup
# ----------------------------
st.set_page_config(page_title="Groq Q&A Chatbot", page_icon="💬", layout="wide")

# If the key is missing, nothing else will work, so we stop early.
groq_api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
if not groq_api_key:
    st.error("GROQ_API_KEY not found. Add it in Streamlit Cloud → Settings → Secrets.")
    st.stop()

# Groq uses an OpenAI-compatible endpoint.
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Groq changes/retire models sometimes, so I keep the list short and reliable.
# (gemma2-9b-it was removed, that's why we don't show it anymore.)
MODEL_OPTIONS = [
    "llama-3.1-8b-instant",      # fast + best for free-tier usage
    "llama-3.3-70b-versatile",   # stronger answers, can be slower
    "groq/compound-mini",        # Groq system option (nice balance)
    "groq/compound",             # Groq system option (more capable)
]


# ----------------------------
# Prompt + parser
# ----------------------------
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Answer clearly, politely, and accurately."),
        ("user", "Question: {question}"),
    ]
)
parser = StrOutputParser()


# ----------------------------
# Session state (simple page router)
# ----------------------------
if "page" not in st.session_state:
    st.session_state.page = "landing"  # landing -> setup -> chat

if "settings" not in st.session_state:
    st.session_state.settings = {
        "model": "llama-3.1-8b-instant",
        "temperature": 0.7,
        "max_tokens": 512,
    }

if "messages" not in st.session_state:
    st.session_state.messages = []  # [{"role": "...", "content": "..."}]


# ----------------------------
# Assets helpers
# ----------------------------
APP_DIR = Path(__file__).parent
ASSETS_DIR = APP_DIR / "assets"


def img_to_data_uri(img_path: Path) -> str:
    # Streamlit can't use local file paths directly in CSS on Cloud,
    # so we convert the image to a base64 data URI.
    if not img_path.exists():
        return ""
    b64 = base64.b64encode(img_path.read_bytes()).decode("utf-8")
    ext = img_path.suffix.lower().replace(".", "")
    mime = "png" if ext == "png" else ext
    return f"data:image/{mime};base64,{b64}"


def set_page_background(page_name: str):
    # Pick a different background for each page (1,2,3).
    mapping = {
        "landing": ASSETS_DIR / "1.png",
        "setup": ASSETS_DIR / "2.png",
        "chat": ASSETS_DIR / "3.png",
    }
    img_path = mapping.get(page_name, ASSETS_DIR / "1.png")
    data_uri = img_to_data_uri(img_path)

    if not data_uri:
        st.warning(f"Background image missing: {img_path}. Put it inside assets/.")
        data_uri = ""

    st.markdown(
        f"""
        <style>
        /* Hide Streamlit chrome */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}

        /* Background */
        .stApp {{
            background-image: url("{data_uri}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* Dark overlay so text stays readable */
        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            background: radial-gradient(1200px 900px at 20% 15%, rgba(0, 255, 255, 0.12), transparent 55%),
                        radial-gradient(1000px 800px at 85% 25%, rgba(255, 0, 255, 0.10), transparent 55%),
                        linear-gradient(180deg, rgba(0,0,0,0.55), rgba(0,0,0,0.72));
            pointer-events: none;
            z-index: 0;
        }}

        /* Content above overlay */
        .block-container {{
            position: relative;
            z-index: 1;
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 2.5rem;
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(10,10,18,0.92), rgba(5,5,10,0.92));
            border-right: 1px solid rgba(255,255,255,0.08);
        }}
        [data-testid="stSidebar"] * {{
            color: rgba(255,255,255,0.90) !important;
        }}

        /* Glass panels */
        .glass {{
            border-radius: 22px;
            padding: 34px 30px;
            background: rgba(10, 12, 18, 0.55);
            border: 1px solid rgba(255,255,255,0.12);
            box-shadow: 0 18px 55px rgba(0,0,0,0.42);
            backdrop-filter: blur(10px);
        }}
        .glass h1 {{
            margin: 0;
            font-size: 46px;
            line-height: 1.05;
            letter-spacing: -0.02em;
            color: #ffffff;
        }}
        .glass p {{
            margin-top: 12px;
            font-size: 16px;
            line-height: 1.6;
            color: rgba(255,255,255,0.78);
            max-width: 820px;
        }}

        .mini-card {{
            border-radius: 18px;
            padding: 18px 18px;
            background: rgba(10, 12, 18, 0.48);
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: 0 10px 28px rgba(0,0,0,0.30);
            backdrop-filter: blur(10px);
        }}
        .mini-card h3 {{
            margin: 0 0 8px 0;
            font-size: 18px;
            color: #ffffff;
        }}
        .mini-card p {{
            margin: 0;
            font-size: 14px;
            line-height: 1.55;
            color: rgba(255,255,255,0.74);
        }}

        .badges {{
            margin-top: 16px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .badge {{
            padding: 7px 12px;
            border-radius: 999px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.10);
            color: rgba(255,255,255,0.86);
            font-size: 13px;
        }}

        /* Buttons */
        div.stButton > button {{
            width: 100%;
            border-radius: 14px;
            padding: 12px 16px;
            border: 1px solid rgba(255,255,255,0.16);
            background: linear-gradient(135deg, rgba(0, 220, 255, 0.85), rgba(196, 66, 255, 0.82));
            color: #0b0f14;
            font-weight: 800;
            box-shadow: 0 12px 30px rgba(0,0,0,0.25);
        }}

        /* Chat shell */
        .chat-shell {{
            border-radius: 18px;
            padding: 14px;
            background: rgba(10, 12, 18, 0.45);
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: 0 10px 30px rgba(0,0,0,0.28);
            backdrop-filter: blur(10px);
        }}

        /* Make chat input readable */
        [data-testid="stChatInput"] textarea {{
            background: rgba(255,255,255,0.06) !important;
            border: 1px solid rgba(255,255,255,0.16) !important;
            color: rgba(255,255,255,0.92) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def go(page_name: str):
    st.session_state.page = page_name
    st.rerun()


# ----------------------------
# LLM call
# ----------------------------
def generate_response(question: str) -> str:
    cfg = st.session_state.settings

    llm = ChatOpenAI(
        api_key=groq_api_key,
        base_url=GROQ_BASE_URL,
        model=cfg["model"],
        temperature=cfg["temperature"],
        max_tokens=cfg["max_tokens"],
    )

    chain = prompt | llm | parser
    return chain.invoke({"question": question})


# ----------------------------
# Pages
# ----------------------------
def landing_page():
    set_page_background("landing")

    c1, c2 = st.columns([1.35, 1])

    with c1:
        st.markdown(
            """
            <div class="glass">
              <h1>Groq-Powered<br/>Q&A Chatbot</h1>
              <p>
                A modern chatbot built with <b>Streamlit</b> + <b>LangChain</b>, hosted online for free on
                <b>Streamlit Community Cloud</b> and powered by <b>Groq</b>.
              </p>
              <div class="badges">
                <span class="badge">⚡ Fast</span>
                <span class="badge">☁️ Online</span>
                <span class="badge">🔐 Secure Secrets</span>
                <span class="badge">🧠 Multiple Models</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        b1, b2, b3 = st.columns([1, 1, 1])
        with b1:
            if st.button("🚀 Get Started"):
                go("setup")
        with b2:
            if st.button("⚙️ Setup"):
                go("setup")
        with b3:
            if st.button("💬 Chat"):
                go("chat")

    with c2:
        st.markdown(
            """
            <div class="mini-card">
              <h3>What you can do</h3>
              <p>
                • Ask questions and get instant answers<br/>
                • Pick a model and tune creativity<br/>
                • Share your app link with anyone
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        st.markdown(
            """
            <div class="mini-card">
              <h3>Tip</h3>
              <p>
                If the bot feels too random, lower the temperature (0.3–0.5 is a good range).
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def setup_page():
    set_page_background("setup")

    st.markdown(
        """
        <div class="glass">
          <h1>Setup</h1>
          <p>Choose the model and settings. You can also change these later from the chat sidebar.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    left, right = st.columns([1, 1])

    with left:
        st.markdown('<div class="mini-card">', unsafe_allow_html=True)
        st.subheader("Model")

        model = st.selectbox(
            "Select Groq model",
            MODEL_OPTIONS,
            index=MODEL_OPTIONS.index(st.session_state.settings["model"])
            if st.session_state.settings["model"] in MODEL_OPTIONS
            else 0,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="mini-card">', unsafe_allow_html=True)
        st.subheader("Generation")

        temperature = st.slider(
            "Temperature", 0.0, 1.0, float(st.session_state.settings["temperature"]), 0.05
        )
        max_tokens = st.slider(
            "Max tokens", 64, 2048, int(st.session_state.settings["max_tokens"]), 64
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    a1, a2, a3 = st.columns([1, 1, 1])

    with a1:
        if st.button("⬅️ Back"):
            go("landing")

    with a2:
        if st.button("💾 Save Settings"):
            st.session_state.settings.update(
                {"model": model, "temperature": float(temperature), "max_tokens": int(max_tokens)}
            )
            st.success("Saved ✅")

    with a3:
        if st.button("➡️ Continue to Chat"):
            st.session_state.settings.update(
                {"model": model, "temperature": float(temperature), "max_tokens": int(max_tokens)}
            )
            go("chat")


def chat_page():
    set_page_background("chat")

    # Sidebar controls (kept here so chat page stays clean)
    st.sidebar.header("Chat Controls")
    st.sidebar.caption("Changes apply to new messages.")

    st.session_state.settings["model"] = st.sidebar.selectbox(
        "Model",
        MODEL_OPTIONS,
        index=MODEL_OPTIONS.index(st.session_state.settings["model"])
        if st.session_state.settings["model"] in MODEL_OPTIONS
        else 0,
    )
    st.session_state.settings["temperature"] = st.sidebar.slider(
        "Temperature", 0.0, 1.0, float(st.session_state.settings["temperature"]), 0.05
    )
    st.session_state.settings["max_tokens"] = st.sidebar.slider(
        "Max tokens", 64, 2048, int(st.session_state.settings["max_tokens"]), 64
    )

    if st.sidebar.button("🧹 Clear chat"):
        st.session_state.messages = []
        st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("🏠 Home"):
        go("landing")
    if st.sidebar.button("⚙️ Setup"):
        go("setup")

    st.markdown(
        """
        <div class="glass">
          <h1>Chat</h1>
          <p>Ask anything. Your chat stays in this session.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    st.markdown('<div class="chat-shell">', unsafe_allow_html=True)

    # Show history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input + response
    user_text = st.chat_input("Type your message...")

    if user_text:
        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)

        with st.chat_message("assistant"):
            with st.spinner("Generating..."):
                try:
                    answer = generate_response(user_text)
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    # If a model ever gets retired again, the error message can be confusing,
                    # so we show a cleaner hint here.
                    err = str(e)
                    if "model_decommissioned" in err or "decommissioned" in err:
                        st.error("That model was retired by Groq. Pick a different model from the dropdown.")
                    else:
                        st.error(f"Error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------
# Router
# ----------------------------
if st.session_state.page == "landing":
    landing_page()
elif st.session_state.page == "setup":
    setup_page()
else:
    chat_page()

import streamlit as st
import google.generativeai as genai
import time

st.set_page_config(
    page_title="Gemini Agent Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== SESSION STATE ======================
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "model_name" not in st.session_state:
    st.session_state.model_name = "gemini-1.5-pro"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}
if "custom_agents" not in st.session_state:
    st.session_state.custom_agents = {}
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = None

# ====================== DEFAULT AGENTS ======================
DEFAULT_AGENTS = {
    "🔍 Researcher": {
        "role": "Expert Researcher",
        "goal": "Gather accurate, balanced, and well-sourced information",
        "backstory": "You are a meticulous researcher who values evidence and multiple perspectives.",
        "system_prompt": "You are an expert researcher. Provide detailed, accurate, objective information. Use evidence-based reasoning and present balanced views when appropriate."
    },
    "✍️ Creative Writer": {
        "role": "Creative Writer",
        "goal": "Create engaging, original, and high-quality written content",
        "backstory": "You have a vivid imagination and mastery of storytelling and persuasive writing.",
        "system_prompt": "You are a highly creative writer. Use vivid language, strong narratives, and the appropriate tone for the request. Be original and engaging."
    },
    "💻 Code Expert": {
        "role": "Senior Software Engineer",
        "goal": "Write, debug, review, and explain high-quality code",
        "backstory": "You are a seasoned developer who follows best practices and writes clean, efficient code.",
        "system_prompt": "You are an expert software engineer. Write clean, well-commented code. Always explain your reasoning and suggest improvements."
    },
    "📈 Business Strategist": {
        "role": "Business Strategist",
        "goal": "Provide strategic, data-driven business advice",
        "backstory": "You analyze markets, competition, and opportunities with sharp strategic thinking.",
        "system_prompt": "You are a sharp business strategist. Provide structured, actionable advice with clear reasoning and consideration of risks and opportunities."
    },
    "🧐 Critic & Reviewer": {
        "role": "Constructive Critic",
        "goal": "Give honest, balanced, and helpful feedback",
        "backstory": "You see both strengths and weaknesses and help people improve their work.",
        "system_prompt": "You are a constructive critic. Start with positives, then give specific, actionable feedback. Be honest but encouraging."
    }
}

def get_all_agents():
    return {**DEFAULT_AGENTS, **st.session_state.custom_agents}

# ====================== SIDEBAR ======================
with st.sidebar:
    st.title("⚙️ Configuration")
    
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        value=st.session_state.api_key,
        help="Get your key at https://aistudio.google.com/app/apikey"
    )
    if api_key:
        st.session_state.api_key = api_key
        try:
            genai.configure(api_key=api_key)
        except Exception as e:
            st.error(f"Invalid API Key: {e}")

    st.session_state.model_name = st.selectbox(
        "Model",
        ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"],
        index=1
    )

    st.session_state.temperature = st.slider(
        "Temperature", 0.0, 1.0, st.session_state.temperature, 0.05,
        help="Higher = more creative, Lower = more deterministic"
    )

    st.divider()
    if st.button("🗑️ Clear All Chat Histories"):
        st.session_state.chat_histories = {}
        st.rerun()

# ====================== MAIN APP =====================

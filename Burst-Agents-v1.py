import streamlit as st
from openai import OpenAI
import time

st.set_page_config(
    page_title="NVIDIA NIM Grant Writing Studio",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== SESSION STATE ======================
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "model_name" not in st.session_state:
    st.session_state.model_name = "meta/llama-3.1-70b-instruct"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}
if "custom_agents" not in st.session_state:
    st.session_state.custom_agents = {}
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = None

# ====================== GRANT WRITING AGENTS (Specialized) ======================
DEFAULT_AGENTS = {
    "🔍 Grant Researcher": {
        "role": "Grant Opportunity Researcher",
        "goal": "Find and analyze relevant funding opportunities",
        "backstory": "You are an expert grant researcher who scours databases and understands funder priorities.",
        "system_prompt": "You are a professional Grant Researcher. Identify suitable funders, summarize RFPs/RFAs, highlight alignment with the applicant's mission, and note deadlines, eligibility, and past award trends."
    },
    "✍️ Proposal Writer": {
        "role": "Lead Grant Writer",
        "goal": "Draft compelling, persuasive, and funder-aligned proposals",
        "backstory": "You are a seasoned grant writer who knows how to tell powerful stories while meeting strict guidelines.",
        "system_prompt": "You are an expert Grant Writer. Write clear, persuasive, and concise proposal sections. Use strong narratives, evidence-based arguments, and align language with the funder's priorities."
    },
    "📊 Budget & Finance Expert": {
        "role": "Grant Budget Specialist",
        "goal": "Create realistic, compliant, and justified budgets",
        "backstory": "You are a financial expert who builds detailed grant budgets and narratives.",
        "system_prompt": "You are a Grant Budget Specialist. Build line-item budgets, create budget justifications/narratives, calculate indirect costs, and ensure compliance with funder guidelines."
    },
    "📋 Needs Assessor": {
        "role": "Community Needs Analyst",
        "goal": "Develop strong needs statements backed by data",
        "backstory": "You excel at turning statistics and stories into compelling needs statements.",
        "system_prompt": "You are a Needs Assessment Expert. Help craft powerful needs/problem statements using data, statistics, local context, and beneficiary voices. Make the case urgent and solvable."
    },
    "🎯 Goals & Outcomes Expert": {
        "role": "Logic Model & Evaluation Designer",
        "goal": "Design SMART goals, objectives, and evaluation plans",
        "backstory": "You are an evaluation expert who builds measurable and realistic project frameworks.",
        "system_prompt": "You are a Goals & Outcomes Expert. Create SMART objectives, logic models, evaluation plans, and sustainability strategies. Focus on measurable outcomes and data collection methods."
    },
    "🧐 Proposal Reviewer & Editor": {
        "role": "Senior Grant Reviewer",
        "goal": "Review, critique, and strengthen full proposals",
        "backstory": "You review proposals like a foundation program officer.",
        "system_prompt": "You are a rigorous Proposal Reviewer. Score sections against common funder criteria, point out weaknesses, suggest improvements, and ensure clarity, consistency, and compliance."
    },
    "📖 Storyteller & Narrative Expert": {
        "role": "Impact Storyteller",
        "goal": "Create emotionally compelling yet factual narratives",
        "backstory": "You blend human stories with data to create unforgettable proposal narratives.",
        "system_prompt": "You are an Impact Storyteller. Transform project descriptions into compelling, human-centered narratives while maintaining credibility and evidence."
    },
    "⚖️ Compliance & Eligibility Specialist": {
        "role": "Grant Compliance Officer",
        "goal": "Ensure proposals meet all legal, regulatory, and funder requirements",
        "backstory": "You are meticulous about rules, forms, and documentation.",
        "system_prompt": "You are a Grant Compliance Expert. Check eligibility, required attachments, formatting rules, certifications, and risk areas. Flag potential red flags and suggest fixes."
    },
    "🔗 Funder Matchmaker": {
        "role": "Strategic Funder Analyst",
        "goal": "Match projects to the best funding sources",
        "backstory": "You understand hundreds of foundations, government agencies, and corporate funders.",
        "system_prompt": "You are a Funder Matchmaker. Analyze a project and recommend the best funding opportunities (government, foundation, corporate) with rationale and alignment scores."
    },
    "📈 Data & Metrics Analyst": {
        "role": "Grant Metrics & Evidence Expert",
        "goal": "Provide credible data, statistics, and evidence",
        "backstory": "You turn raw data into persuasive evidence for proposals.",
        "system_prompt": "You are a Data & Metrics Analyst for grants. Source credible statistics, interpret data, suggest benchmarks, and help build strong evidence sections."
    },
    "🛠️ LOI & Concept Paper Writer": {
        "role": "Letter of Inquiry Specialist",
        "goal": "Write concise and high-conversion LOIs/Concept Papers",
        "backstory": "You know how to hook funders in 1-2 pages.",
        "system_prompt": "You are an LOI/Concept Paper Expert. Write compelling 1-3 page letters of inquiry that clearly communicate the problem, solution, impact, and ask."
    },
    "🏛️ Government Grants Specialist": {
        "role": "Federal & State Grants Expert",
        "goal": "Navigate complex government funding (SAM.gov, Grants.gov, etc.)",
        "backstory": "You understand federal grant mechanisms, NOFOs, and post-award compliance.",
        "system_prompt": "You are a Government Grants Specialist. Help with federal and state proposals, including SF-424 forms, project narratives, and post-award requirements."
    },
    "🌍 Foundation & Corporate Grants Expert": {
        "role": "Private Philanthropy Expert",
        "goal": "Tailor proposals for foundations and corporate giving programs",
        "backstory": "You understand the nuances of private philanthropy.",
        "system_prompt": "You are a Foundation & Corporate Grants Expert. Help craft proposals that appeal to private funders, emphasizing mission alignment, innovation, and measurable community impact."
    },
    "📝 Final Polish Editor": {
        "role": "Professional Grant Editor",
        "goal": "Polish language, flow, and formatting",
        "backstory": "You make proposals read professionally and error-free.",
        "system_prompt": "You are a professional Grant Editor. Improve clarity, grammar, flow, consistency, and tone. Eliminate jargon and strengthen weak sections."
    },
    "🚀 Sustainability & Scalability Planner": {
        "role": "Long-term Impact Strategist",
        "goal": "Design sustainable and scalable projects",
        "backstory": "You help organizations think beyond the grant period.",
        "system_prompt": "You are a Sustainability & Scalability Expert. Help develop strong exit/sustainability plans, scaling strategies, and future funding diversification approaches."
    }
}

def get_all_agents():
    return {**DEFAULT_AGENTS, **st.session_state.custom_agents}

# ====================== NVIDIA CLIENT ======================
def get_nvidia_client():
    """Returns OpenAI client configured for NVIDIA NIM"""
    if not st.session_state.api_key:
        st.error("⚠️ Please enter your NVIDIA NIM API Key in the sidebar to continue.")
        return None
    try:
        return OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=st.session_state.api_key
        )
    except Exception as e:
        st.error(f"Client Error: {e}")
        return None

# ====================== GENERATE RESPONSE ======================
def generate_response(prompt, agent=None):
    client = get_nvidia_client()
    if not client:
        return None
    
    messages = []
    
    # Add agent system prompt
    if agent and agent.get("system_prompt"):
        messages.append({"role": "system", "content": agent["system_prompt"]})
    
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model=st.session_state.model_name,
            messages=messages,
            temperature=st.session_state.temperature,
            max_tokens=4096,
            stream=True
        )
        return response
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

# ====================== SIDEBAR ======================
with st.sidebar:
    st.title("⚙️ Configuration")
    
    api_key = st.text_input(
        "NVIDIA NIM API Key",
        type="password",
        value=st.session_state.api_key,
        help="Get your free key → https://build.nvidia.com/",
        placeholder="nvapi-..."
    )
    
    if api_key:
        st.session_state.api_key = api_key

    # Model Selection
    nvidia_models = [
        "meta/llama-3.1-70b-instruct",
        "meta/llama-3.1-405b-instruct",
        "nvidia/nemotron-4-340b-instruct",
        "deepseek-ai/deepseek-v3",
        "qwen/qwen2.5-72b-instruct",
        "mistralai/mistral-large",
    ]
    
    st.session_state.model_name = st.selectbox(
        "NVIDIA Model", nvidia_models, index=0
    )

    st.session_state.temperature = st.slider(
        "Temperature", 0.0, 1.0, st.session_state.temperature, 0.05
    )

    st.divider()
    if st.button("🗑️ Clear All Chat Histories"):
        st.session_state.chat_histories = {}
        st.rerun()

    st.caption("Powered by NVIDIA NIM • Grant Writing Studio")

# ====================== MAIN APP ======================
st.title("📄 NVIDIA NIM Grant Writing Studio")
st.markdown("**AI-Powered Grant Writing Agents** — Built for nonprofits, researchers, educators, and social enterprises.")

# Agent Selection
agents = get_all_agents()
agent_names = list(agents.keys())
selected_agent_name = st.selectbox("Select Grant Writing Agent", agent_names, index=0)
st.session_state.selected_agent = agents[selected_agent_name]

st.info(f"**Active Agent:** {selected_agent_name} | **Model:** {st.session_state.model_name}")

# Chat Interface
if "current_chat" not in st.session_state:
    st.session_state.current_chat = []

for msg in st.session_state.current_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Describe your grant project, ask for help with a section, or upload RFP details..."):
    # Add user message
    st.session_state.current_chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        response = generate_response(prompt, st.session_state.selected_agent)
        
        if response:
            # Stream the response
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            
            # Save to history
            st.session_state.current_chat.append({"role": "assistant", "content": full_response})
        else:
            st.warning("Could not get response. Please check your API key.")

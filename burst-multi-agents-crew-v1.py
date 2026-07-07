import streamlit as st
import json
from openai import OpenAI
import time

# ====================== SKILLS & AGENT DATA ======================
skills_data = {
    "software_engineer": [
        {"name": "system_design", "description": "Design scalable software systems and architecture."},
        {"name": "clean_code", "description": "Write maintainable, efficient, and well-documented code."},
        {"name": "api_development", "description": "Build robust RESTful or GraphQL APIs."}
    ],
    "full_stack_developer": [
        {"name": "frontend_development", "description": "Build UIs with React, Vue, or Angular."},
        {"name": "backend_development", "description": "Develop APIs with Node.js, Python, etc."}
    ],
    "data_scientist": [
        {"name": "machine_learning", "description": "Build and deploy ML models."},
        {"name": "data_analysis", "description": "Analyze datasets to extract actionable insights."}
    ],
    "project_manager": [
        {"name": "project_planning", "description": "Create detailed project plans and timelines."},
        {"name": "agile_scrum", "description": "Manage sprints, stand-ups, and blockages."}
    ],
    "marketer": [
        {"name": "content_marketing", "description": "Create and distribute valuable content."},
        {"name": "seo_optimization", "description": "Improve search engine rankings."}
    ],
    "accountant": [
        {"name": "budgeting_and_forecasting", "description": "Develop budgets and monitor performance."},
        {"name": "financial_reporting", "description": "Prepare balance sheets and income statements."}
    ],
    "lawyer": [
        {"name": "legal_research", "description": "Conduct thorough legal research."},
        {"name": "contract_drafting", "description": "Draft and review contracts and compliance terms."}
    ]
}

agents_list = list(skills_data.keys())

# ====================== SESSION STATE ======================
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "model_name" not in st.session_state:
    st.session_state.model_name = "meta/llama-3.1-70b-instruct"
if "crew_tasks" not in st.session_state:
    st.session_state.crew_tasks = {}  # {agent_name: [task_dicts]}

# ====================== NVIDIA CLIENT & LLM LOGIC ======================
def get_nvidia_client():
    if not st.session_state.api_key:
        return None
    try:
        return OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=st.session_state.api_key
        )
    except Exception as e:
        st.error(f"Client Error: {e}")
        return None

def generate_agent_response(agent_name, tasks, master_objective):
    client = get_nvidia_client()
    if not client:
        yield "⚠️ API Client not configured. Please enter your NVIDIA NIM API Key."
        return

    # Construct the System Prompt dynamically based on the assigned tasks
    role_title = agent_name.replace("_", " ").title()
    task_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in tasks])
    
    system_prompt = f"""You are a highly skilled {role_title} operating as part of a multi-agent AI crew.
Your specific assigned responsibilities for this project are:
{task_descriptions}

Execute your duties based on the master objective provided by the user. Focus ONLY on your domain of expertise. Do not do the work of other agents."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Master Project Objective: {master_objective}\n\nPlease provide your specialized contribution based on your assigned tasks."}
    ]
    
    try:
        response = client.chat.completions.create(
            model=st.session_state.model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"⚠️ API Error: {str(e)}"

# ====================== MAIN APP ======================
st.set_page_config(page_title="Burst Multi-Agent Crew", page_icon="🚀", layout="wide")

# -- SIDEBAR --
with st.sidebar:
    st.title("⚙️ Engine Config")
    api_key = st.text_input(
        "NVIDIA NIM API Key", type="password", 
        value=st.session_state.api_key, help="Get your free key at https://build.nvidia.com/"
    )
    if api_key:
        st.session_state.api_key = api_key

    st.session_state.model_name = st.selectbox(
        "NVIDIA Model", 
        ["meta/llama-3.1-70b-instruct", "meta/llama-3.1-405b-instruct", "nvidia/nemotron-4-340b-instruct", "deepseek-ai/deepseek-v3"], 
        index=0
    )
    
    st.divider()
    st.markdown("### Active Crew Members")
    if not st.session_state.crew_tasks:
        st.caption("No agents hired yet.")
    else:
        for agent in st.session_state.crew_tasks.keys():
            st.markdown(f"🧑‍💻 **{agent.replace('_', ' ').title()}** ({len(st.session_state.crew_tasks[agent])} tasks)")
            
    if st.button("🗑️ Disband Crew", use_container_width=True):
        st.session_state.crew_tasks = {}
        st.rerun()

# -- HEADER --
st.title("🚀 Burst Software: Multi-Agent Crew")
st.markdown("Build your team, assign their specialized skills, and deploy them to solve complex objectives.")

# -- TABS --
tab1, tab2, tab3 = st.tabs(["👥 1. Hire Crew & Assign Skills", "📋 2. Review Task Board", "🎯 3. Mission Control"])

# ----------------- TAB 1: HIRE CREW -----------------
with tab1:
    st.subheader("Select an Agent to Add to Your Crew")
    selected_agent = st.selectbox("Available Experts:", ["-- Select an Agent --"] + agents_list)
    
    if selected_agent != "-- Select an Agent --":
        display_name = selected_agent.replace("_", " ").title()
        st.markdown(f"### {display_name} Skills")
        
        # Display skills for the selected agent
        for skill in skills_data.get(selected_agent, []):
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{skill['name'].replace('_', ' ').title()}**")
                    st.caption(skill['description'])
                with col2:
                    if st.button("➕ Assign Task", key=f"add_{selected_agent}_{skill['name']}", use_container_width=True):
                        if selected_agent not in st.session_state.crew_tasks:
                            st.session_state.crew_tasks[selected_agent] = []
                        
                        # Prevent duplicates
                        if not any(s['name'] == skill['name'] for s in st.session_state.crew_tasks[selected_agent]):
                            st.session_state.crew_tasks[selected_agent].append(skill)
                            st.toast(f"Assigned {skill['name']} to {display_name}!")
                        else:
                            st.toast("Skill already assigned!")
                st.divider()

        st.markdown("#### 🔹 Or Assign a Custom Task")
        custom_task_name = st.text_input("Custom Task Name", key=f"ctn_{selected_agent}")
        custom_task_desc = st.text_area("Custom Task Description", key=f"ctd_{selected_agent}", height=68)
        if st.button("➕ Add Custom Task", key=f"act_{selected_agent}"):
            if custom_task_name and custom_task_desc:
                if selected_agent not in st.session_state.crew_tasks:
                    st.session_state.crew_tasks[selected_agent] = []
                st.session_state.crew_tasks[selected_agent].append({
                    "name": custom_task_name,
                    "description": custom_task_desc,
                    "is_custom": True
                })
                st.toast("Custom task assigned!")
                st.rerun()

# ----------------- TAB 2: TASK BOARD -----------------
with tab2:
    st.subheader("📋 Crew Task Board")
    
    if not st.session_state.crew_tasks:
        st.info("Your crew is empty. Go to the 'Hire Crew' tab to assign agents and tasks.")
    else:
        # Download Config Button
        download_data = json.dumps(st.session_state.crew_tasks, indent=2)
        st.download_button(
            label="💾 Download Crew Manifest (JSON)",
            data=download_data,
            file_name="burst_crew_manifest.json",
            mime="application/json"
        )
        st.divider()

        for agent, tasks in st.session_state.crew_tasks.items():
            with st.expander(f"**{agent.replace('_', ' ').title()}** ({len(tasks)} active tasks)", expanded=True):
                for i, task in enumerate(tasks):
                    col_t1, col_t2 = st.columns([5, 1])
                    with col_t1:
                        emoji = "🔹" if task.get("is_custom") else "🛠️"
                        st.markdown(f"{emoji} **{task['name'].replace('_', ' ').title()}** - {task['description']}")
                    with col_t2:
                        if st.button("❌ Remove", key=f"rem_{agent}_{i}"):
                            st.session_state.crew_tasks[agent].pop(i)
                            if not st.session_state.crew_tasks[agent]:
                                del st.session_state.crew_tasks[agent]
                            st.rerun()

# ----------------- TAB 3: MISSION CONTROL -----------------
with tab3:
    st.subheader("🎯 Mission Control Engine")
    
    if not st.session_state.api_key:
        st.warning("⚠️ Please enter your NVIDIA NIM API Key in the sidebar to run missions.")
    elif not st.session_state.crew_tasks:
        st.warning("⚠️ Your crew is currently empty. Please hire agents and assign tasks first.")
    else:
        st.markdown("Define the overarching project for your crew. Each agent will process this objective through the lens of their specific assigned tasks.")
        master_objective = st.text_area("Master Project Objective", placeholder="e.g., We are launching a new AI-powered mobile app for fitness tracking. We need a development plan, a marketing strategy, and a legal privacy policy drafted.")
        
        if st.button("🚀 Execute Mission", type="primary", use_container_width=True):
            if not master_objective.strip():
                st.error("Please enter a master objective.")
            else:
                st.divider()
                st.markdown("### 📡 Live Crew Execution")
                
                # Iterate through the hired crew and execute LLM calls
                for agent_name, tasks in st.session_state.crew_tasks.items():
                    display_name = agent_name.replace('_', ' ').title()
                    
                    st.markdown(f"#### 🧑‍💻 {display_name} is working...")
                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        full_response = ""
                        
                        # Stream the response from the LLM
                        for chunk in generate_agent_response(agent_name, tasks, master_objective):
                            full_response += chunk
                            message_placeholder.markdown(full_response + "▌")
                        
                        message_placeholder.markdown(full_response)
                    st.divider()
                
                st.success("✅ Mission accomplished! All agents have submitted their work.")

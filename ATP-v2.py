import streamlit as st
from fpdf import FPDF
import datetime

# --- PDF Generation Function ---
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Autonomous AI System Configuration", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 10, f"Generated on {datetime.date.today()}", ln=True, align="C")
    pdf.ln(5)
    
    # Section helper
    def add_section(title, content_dict):
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font("Helvetica", "", 10)
        for key, value in content_dict.items():
            # Handle multi-line text cleanly
            safe_value = str(value).replace('\n', ' ')
            pdf.multi_cell(0, 7, txt=f"{key}: {safe_value}")
        pdf.ln(3)

    # Add sections based on user input
    add_section("1. Project Initialization", data['init'])
    add_section("2. Architecture Overview", data['arch'])
    
    # Agents (formatting as a comma-separated list for the PDF)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "3. Core Components (Active Agents)", ln=True)
    pdf.set_font("Helvetica", "", 10)
    active_agents = [agent for agent, active in data['agents'].items() if active]
    pdf.multi_cell(0, 7, txt=", ".join(active_agents) if active_agents else "None selected.")
    pdf.ln(3)
    
    add_section("4. Safeguards & Limits", data['safeguards'])

    # Return PDF as bytes
    return bytes(pdf.output())

# --- Streamlit UI ---
st.set_page_config(page_title="System Configurator", layout="wide")

st.title("Autonomous Multi-Agent System Configurator")
st.markdown("Use this interface to define the parameters for your self-hosted autonomous AI orchestration system.")

# --- Form Inputs ---
with st.form("config_form"):
    
    st.header("1. High-Level Business Process")
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input("Project / Company Name", value="Echoes of a Wasteland")
        target_audience = st.text_input("Target Audience", value="Tactical shooter enthusiasts")
    with col2:
        project_idea = st.text_area(
            "Core Idea & Mission", 
            value="A 3D tactical extraction shooter featuring realistic desert environments across the Americas, complete with complex AI, weapon switching, and survival HUD."
        )

    st.divider()

    st.header("2. Architecture & Tech Stack")
    col3, col4 = st.columns(2)
    with col3:
        orchestrator = st.selectbox("Task Orchestration", ["Celery + Redis", "LangGraph", "CrewAI", "Temporal.io"])
        primary_llm = st.selectbox("Primary LLM Framework", ["Anthropic Claude 3.5 Sonnet", "OpenAI GPT-4o", "Local (Llama 3)"])
        host_environment = st.selectbox("Development Environment", ["M1 Apple Silicon (ARM64)", "Intel/AMD (x86_64)", "Cloud VM"])
    with col4:
        database = st.selectbox("Primary Database", ["PostgreSQL", "MySQL", "SQLite (Dev only)"])
        vector_db = st.selectbox("Vector Memory Store", ["ChromaDB", "pgvector", "Pinecone"])

    st.divider()

    st.header("3. Core Components (The 9 Agents)")
    st.markdown("Select the agents to activate for this initialization cycle.")
    
    # Using columns for checkboxes
    col5, col6, col7 = st.columns(3)
    agent_status = {}
    with col5:
        agent_status["Orchestrator / Strategy"] = st.checkbox("Orchestrator / Strategy", value=True)
        agent_status["Business Planning"] = st.checkbox("Business Planning", value=True)
        agent_status["Competitor Research"] = st.checkbox("Competitor Research", value=True)
    with col6:
        agent_status["Social Media"] = st.checkbox("Social Media", value=False)
        agent_status["Email Outreach"] = st.checkbox("Email Outreach", value=False)
        agent_status["Customer Support"] = st.checkbox("Customer Support", value=False)
    with col7:
        agent_status["Ads Management"] = st.checkbox("Ads Management", value=False)
        agent_status["Code Generation"] = st.checkbox("Code Generation", value=True)
        agent_status["Finance / Ops"] = st.checkbox("Finance / Ops", value=False)

    st.divider()

    st.header("4. Security & Safeguards")
    human_in_loop = st.toggle("Require Human-in-the-Loop for Code Merges", value=True)
    ad_budget = st.slider("Max Autonomous Ad Spend per Day ($)", 0, 500, 50)
    rate_limit = st.number_input("Max LLM API Calls per Hour", min_value=10, max_value=5000, value=500)

    # Submit button
    submitted = st.form_submit_button("Generate Configuration PDF")

# --- Process and Export ---
if submitted:
    # Package data
    config_data = {
        "init": {
            "Project Name": project_name,
            "Target Audience": target_audience,
            "Core Idea": project_idea
        },
        "arch": {
            "Host Architecture": host_environment,
            "Orchestrator": orchestrator,
            "Primary LLM": primary_llm,
            "Relational DB": database,
            "Vector DB": vector_db
        },
        "agents": agent_status,
        "safeguards": {
            "Human-in-the-Loop required": "Yes" if human_in_loop else "No",
            "Max Daily Ad Spend": f"${ad_budget}",
            "Max Hourly API Calls": str(rate_limit)
        }
    }

    # Generate PDF bytes
    pdf_bytes = generate_pdf(config_data)

    st.success("Configuration generated successfully!")
    
    # Provide download button
    st.download_button(
        label="Download Project Spec (PDF)",
        data=pdf_bytes,
        file_name=f"{project_name.replace(' ', '_').lower()}_spec.pdf",
        mime="application/pdf"
    )

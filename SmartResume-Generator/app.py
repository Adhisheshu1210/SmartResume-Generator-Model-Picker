# app.py
import streamlit as st
import os
import io
from datetime import datetime
from docx import Document
from fpdf import FPDF
import resume_generator as rg

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(page_title="SmartResume Generator", layout="centered")
st.title("🧾 SmartResume Generator — Model Picker")

# ---------------------------
# Load API key
# ---------------------------
try:
    API_KEY = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
except Exception:
    API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("⚠️ GEMINI_API_KEY missing. Please add it to Streamlit secrets or environment variables.")
    st.info("Go to: Share → Settings → Secrets and add: `GEMINI_API_KEY = 'your-api-key'`")
    st.stop()

# Configure Gemini SDK
try:
    rg.configure_api(API_KEY)
    st.sidebar.success("✅ API Configured")
except Exception as e:
    st.error(f"❌ API configuration failed: {e}")
    st.stop()

# ---------------------------
# List available models
# ---------------------------
st.sidebar.header("Model Selection")

# Use a default model list as fallback
DEFAULT_MODELS = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]

try:
    models = rg.list_models_via_sdk()
    st.sidebar.success("✅ Models loaded via SDK")
except Exception as sdk_error:
    st.sidebar.warning(f"⚠️ SDK failed: Using default models")
    # Create mock model objects for default models
    models = [{"name": f"models/{m}", "model": m} for m in DEFAULT_MODELS]

if not models:
    st.error("❌ No models available. Using fallback model.")
    models = [{"name": "models/gemini-1.5-flash", "model": "gemini-1.5-flash"}]

# Build readable model names
short_names = []
full_map = {}
for m in models:
    if isinstance(m, dict):
        full = m.get("name") or m.get("model")
    else:
        full = getattr(m, "name", None) or getattr(m, "model", None)
    if not full:
        continue
    short = full.split("/")[-1] if "/" in str(full) else str(full)
    if short not in short_names:  # Avoid duplicates
        short_names.append(short)
        full_map[short] = full

# Pick recommended model
picked = rg.pick_text_model(models)
if picked and picked in short_names:
    default_index = short_names.index(picked)
else:
    default_index = 0

model_choice = st.sidebar.selectbox("Choose model for generation", short_names, index=default_index)
selected_full = full_map.get(model_choice, model_choice)
rg.set_model_name(selected_full)
st.sidebar.info(f"Using: {selected_full}")

# ---------------------------
# UI Inputs
# ---------------------------
st.subheader("Personal Information")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Full Name *", placeholder="Jane Doe")
    email = st.text_input("Email *", placeholder="jane@example.com")
    linkedin = st.text_input("LinkedIn URL *", placeholder="linkedin.com/in/janedoe")
with col2:
    job_title = st.text_input("Job Title *", placeholder="Software Engineer")
    phone = st.text_input("Phone Number *", placeholder="+1234567890")
    github = st.text_input("GitHub URL *", placeholder="github.com/janedoe")

st.subheader("Details")
summary = st.text_area("Professional Summary", placeholder="Brief summary of your professional background...")
skills = st.text_area("Skills (comma-separated)", placeholder="Python, JavaScript, React, Docker...")
experience = st.text_area("Experience", placeholder="Company | Role | Duration\nKey achievements...")
projects = st.text_area("Projects", placeholder="Project Name | Description | Technologies")
education = st.text_area("Education *", placeholder="Degree | University | Year")

style = st.selectbox("Resume style", ["professional", "ats", "creative"])
industry = st.selectbox("Industry", ["General", "Software", "AI/ML", "Finance", "Marketing", "Design", "Other"])

# ---------------------------
# Helpers for downloads
# ---------------------------
def txt_bytes(t): 
    return t.encode("utf-8")

def docx_bytes(t):
    doc = Document()
    for line in t.splitlines():
        p = doc.add_paragraph(line)
        if line.isupper() and p.runs:
            p.runs[0].bold = True
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()

def pdf_bytes(text: str) -> bytes:
    fixes = {"•": "-", "–": "-", "—": "-", "'": "'", "'": "'", """: '"', """: '"', "·": "-"}
    for k, v in fixes.items():
        text = text.replace(k, v)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    for line in text.splitlines():
        try:
            pdf.multi_cell(0, 7, txt=line)
        except Exception:
            # Skip lines that cause encoding issues
            pdf.multi_cell(0, 7, txt=line.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest="S").encode("latin-1")

# ---------------------------
# Generate Resume
# ---------------------------
if st.button("🚀 Generate Resume", type="primary"):
    # Check mandatory fields
    mandatory_fields = {
        "Full Name": name,
        "Job Title": job_title,
        "Email": email,
        "Phone": phone,
        "LinkedIn": linkedin,
        "GitHub": github,
        "Education": education
    }
    empty_fields = [k for k, v in mandatory_fields.items() if not v.strip()]
    if empty_fields:
        st.error(f"❌ Please fill all mandatory fields: {', '.join(empty_fields)}")
        st.stop()

    user = {
        "name": name,
        "job_title": job_title,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "summary": summary,
        "skills": skills,
        "experience": experience,
        "projects": projects,
        "education": education
    }

    prompt = rg.build_resume_prompt(user, style=style, industry=industry)
    with st.spinner("✨ Generating your resume..."):
        try:
            raw = rg.generate_with_model(prompt)
            resume_text = rg.clean_resume_text(raw)
        except Exception as e:
            st.error(f"❌ Failed to generate resume: {e}")
            st.stop()

    st.success("✅ Resume generated successfully!")
    st.markdown("### Preview")
    st.text_area("Resume Content", resume_text, height=400)

    # ---------------------------
    # Download buttons
    # ---------------------------
    st.markdown("### Download Options")
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = name.replace(" ", "_") or "Resume"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("📄 Download TXT", txt_bytes(resume_text), f"{safe}_{now}.txt", mime="text/plain")
    with col2:
        st.download_button(
            "📄 Download DOCX", 
            docx_bytes(resume_text), 
            f"{safe}_{now}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    with col3:
        st.download_button(
            "📄 Download PDF", 
            pdf_bytes(resume_text), 
            f"{safe}_{now}.pdf", 
            mime="application/pdf"
        )

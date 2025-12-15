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
API_KEY = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("GEMINI_API_KEY missing. Add it to secrets or environment variable.")
    st.stop()

# Configure Gemini SDK
try:
    rg.configure_api(API_KEY)
except Exception as e:
    st.error(f"API configuration failed: {e}")
    st.stop()

# ---------------------------
# List available models
# ---------------------------
st.sidebar.header("Model selection")
try:
    models = rg.list_models_via_sdk()
except Exception:
    st.sidebar.info("SDK list_models() failed — using REST fallback")
    models = rg.list_models_via_rest(API_KEY)

if not models:
    st.error("No models available for this API key.")
    st.stop()

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
    short = full.split("/")[-1]
    short_names.append(short)
    full_map[short] = full

# Pick recommended model
picked = rg.pick_text_model(models)
default_index = short_names.index(picked) if picked in short_names else 0
model_choice = st.sidebar.selectbox("Choose model for generation", short_names, index=default_index)
selected_full = full_map.get(model_choice, model_choice)
rg.set_model_name(selected_full)
st.sidebar.write("Using model:", selected_full)

# ---------------------------
# UI Inputs
# ---------------------------
st.subheader("Personal Information")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Full Name *", placeholder="Jane Doe")
    email = st.text_input("Email *")
    linkedin = st.text_input("LinkedIn URL *")
with col2:
    job_title = st.text_input("Job Title *", placeholder="Software Engineer")
    phone = st.text_input("Phone Number *")
    github = st.text_input("GitHub URL *")

st.subheader("Details")
summary = st.text_area("Professional Summary")
skills = st.text_area("Skills (comma-separated)")
experience = st.text_area("Experience")
projects = st.text_area("Projects")
education = st.text_area("Education *")

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
    fixes = {"•": "-", "–": "-", "—": "-", "’": "'", "‘": "'", "“": '"', "”": '"', "·": "-"}
    for k, v in fixes.items():
        text = text.replace(k, v)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    for line in text.splitlines():
        pdf.multi_cell(0, 7, txt=line)
    return pdf.output(dest="S").encode("latin-1")

# ---------------------------
# Generate Resume
# ---------------------------
if st.button("Generate Resume"):
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
    with st.spinner("Generating resume..."):
        try:
            raw = rg.generate_with_model(prompt)
            resume_text = rg.clean_resume_text(raw)
        except Exception as e:
            st.error(f"Failed to generate resume: {e}")
            st.stop()

    st.success("Resume generated successfully!")
    st.markdown("### Preview")
    st.code(resume_text)

    # ---------------------------
    # Download buttons
    # ---------------------------
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = name.replace(" ", "_") or "Resume"

    st.download_button("📄 Download TXT", txt_bytes(resume_text), f"{safe}_{now}.txt")
    st.download_button(
        "📄 Download DOCX", 
        docx_bytes(resume_text), 
        f"{safe}_{now}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    st.download_button(
        "📄 Download PDF", 
        pdf_bytes(resume_text), 
        f"{safe}_{now}.pdf", 
        mime="application/pdf"
    )

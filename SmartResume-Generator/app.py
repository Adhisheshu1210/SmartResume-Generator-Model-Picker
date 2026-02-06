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
el...
# resume_generator.py
import os
import json
import google.generativeai as genai

# Global model name (to be set by app.py)
MODEL_NAME = None

# -------------------------------------------------
# Configure Gemini API
# -------------------------------------------------
def configure_api(api_key: str = None):
    """
    Configure the Google Generative AI SDK with your API key.
    """
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY missing. Set it in secrets or env.")
    genai.configure(api_key=key)

# -------------------------------------------------
# List models via SDK
# -------------------------------------------------
def list_models_via_sdk(page_size: int = 100):
    """
    List models via installed SDK.
    Returns a list of models or raises an error if unsupported.
    """
    try:
        if hasattr(genai, "list_models"):
            return list(genai.list_models(page_size=page_size))
        if hasattr(genai, "models") and hasattr(genai.models, "list"):
            return genai.models.list(page_size=page_size)
    except Exception as e:
        raise RuntimeError(f"SDK list_models() failed: {e}")
    raise RuntimeError("list_models not available in this genai SDK")

# -------------------------------------------------
# List models via REST
# -------------------------------------------------
def list_models_via_rest(api_key: str):
    """
    Fallback REST call to list accessible models.
    """
    import requests
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json().get("models", [])

# -------------------------------------------------
# Pick a valid text-generation model
# -------------------------------------------------
def pick_text_model(models):
    """
    Choose a Gemini model suitable for text generation.
    Skips embeddings, audio, vision models.
    """
    candidates = []

    for m in models:
        # Convert to dict-like
        mdict = {}
        try:
            mdict = dict(m)
        except Exception:
            try:
                mdict = m.__dict__
            except Exception:
                mdict = m

        # Get model name
        name = mdict.get("name") or mdict.get("model") or mdict.get("displayName")
        if not name:
            continue

        lname = name.lower()
        # Skip invalid models
        if any(x in lname for x in ["embedding", "vision", "image", "audio", "speech"]):
            continue

        # Check supported methods / capabilities
        caps = mdict.get("supported_methods") or mdict.get("supportedMethods") or mdict.get("capabilities") or []
        caps_text = json.dumps(caps).lower() if caps else ""
        if "generatecontent" in caps_text or "generate" in caps_text or "text" in caps_text or "chat" in caps_text:
            candidates.append(name)

    # Prioritize Gemini models
    priority = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
    for p in priority:
        for c in candidates:
            if p in c:
                return c.split("/")[-1]

    # Fallback to first candidate
    if candidates:
        return candidates[0].split("/")[-1]

    return None

# -------------------------------------------------
# Set model name
# -------------------------------------------------
def set_model_name(name: str):
    global MODEL_NAME
    if not name:
        raise ValueError("Model name cannot be empty")
    MODEL_NAME = name

# -------------------------------------------------
# Generate content
# -------------------------------------------------
def generate_with_model(prompt: str) -> str:
    if not MODEL_NAME:
        raise RuntimeError("MODEL_NAME is not set. Call set_model_name() first.")

    if any(x in MODEL_NAME.lower() for x in ["embedding", "vision", "audio"]):
        raise RuntimeError(f"Invalid model for generation: {MODEL_NAME}")

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        try:
            response = model.generate_content(prompt)
        except TypeError:
            response = model.generate_content(contents=prompt)
    except Exception as e:
        raise RuntimeError(f"Model generation error: {e}")

    # Extract text
    if hasattr(response, "text") and response.text:
        return response.text.strip()

    try:
        for cand in getattr(response, "candidates", []):
            content = getattr(cand, "content", [])
            for part in content:
                text = getattr(part, "text", None) or (part.get("text") if isinstance(part, dict) else None)
                if text:
                    return text.strip()
    except Exception:
        pass

    return str(response).strip()

# -------------------------------------------------
# Cleanup model placeholders
# -------------------------------------------------
def clean_resume_text(text: str) -> str:
    if not text:
        return ""
    return (text.replace("[Add Email Address]", "")
                .replace("[Add Phone Number]", "")
                .replace("[Add LinkedIn Profile URL (optional)]", "")
                .replace("[Add GitHub URL (optional)]", "")
                .strip())

# -------------------------------------------------
# Build resume prompt
# -------------------------------------------------
def build_resume_prompt(user, style="professional", industry="General"):
    """
    Build a structured prompt for Gemini to generate resume content.
    """
    return f"""
You are an expert resume writer skilled in ATS-friendly formatting.
Write a polished, well-structured resume based on the details below.

--- Personal Details ---
Name: {user.get("name", "")}
Job Title: {user.get("job_title", "")}
Email: {user.get("email", "")}
Phone: {user.get("phone", "")}
LinkedIn: {user.get("linkedin", "")}
GitHub: {user.get("github", "")}

--- Professional Summary ---
{user.get("summary", "")}

--- Skills ---
{user.get("skills", "")}

--- Experience ---
{user.get("experience", "")}

--- Projects ---
{user.get("projects", "")}

--- Education ---
{user.get("education", "")}

--- Requirements ---
• Resume style: {style}
• Industry focus: {industry}
• Format with neat bullet-points
• Include strong action verbs and measurable achievements
• Do NOT add placeholders
• Output only resume content
• Start with candidate's name as heading

Generate only resume content. No explanations.
""".strip()

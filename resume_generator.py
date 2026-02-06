# resume_generator.py
import os
import json
from google import genai

# Global client (to be set by configure_api)
client = None

# Global model name (to be set by app.py)
MODEL_NAME = None

# -------------------------------------------------
# Configure Gemini API
# -------------------------------------------------
def configure_api(api_key: str = None):
    """
    Configure the Google GenAI SDK with your API key.
    """
    global client
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY missing. Set it in secrets or env.")
    client = genai.Client(api_key=key)

# -------------------------------------------------
# List models via SDK
# -------------------------------------------------
def list_models_via_sdk(page_size: int = 100):
    """
    List models via installed SDK.
    Returns a list of models or raises an error if unsupported.
    """
    global client
    if not client:
        raise RuntimeError("Client not configured. Call configure_api() first.")
    try:
        return list(client.models.list())
    except Exception as e:
        raise RuntimeError(f"SDK list_models() failed: {e}")

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
    """
    Generate resume content using the configured model.
    """
    global client, MODEL_NAME
    if not client:
        raise RuntimeError("Client not configured. Call configure_api() first.")
    if not MODEL_NAME:
        raise RuntimeError("Model not set. Call set_model_name() first.")
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text
    except Exception as e:
        raise RuntimeError(f"Generation failed: {e}")

# -------------------------------------------------
# Build resume prompt
# -------------------------------------------------
def build_resume_prompt(user: dict, style: str = "professional", industry: str = "General") -> str:
    """
    Build a prompt for resume generation based on user data.
    """
    prompt = f"""
You are an expert resume writer. Create a {style} resume for the {industry} industry.

**Personal Information:**
- Name: {user.get('name', 'N/A')}
- Job Title: {user.get('job_title', 'N/A')}
- Email: {user.get('email', 'N/A')}
- Phone: {user.get('phone', 'N/A')}
- LinkedIn: {user.get('linkedin', 'N/A')}
- GitHub: {user.get('github', 'N/A')}

**Professional Summary:**
{user.get('summary', 'Write a compelling professional summary highlighting key achievements and skills.')}

**Skills:**
{user.get('skills', 'List relevant technical and soft skills.')}

**Experience:**
{user.get('experience', 'List work experience with company, role, duration, and key achievements.')}

**Projects:**
{user.get('projects', 'List significant projects with descriptions and technologies used.')}

**Education:**
{user.get('education', 'List educational qualifications.')}

Format the resume professionally with clear sections and bullet points. 
Make it ATS-friendly if style is 'ats'. Make it visually appealing if style is 'creative'.
"""
    return prompt

# -------------------------------------------------
# Clean resume text
# -------------------------------------------------
def clean_resume_text(text: str) -> str:
    """
    Clean and format the generated resume text.
    """
    # Remove markdown formatting that might interfere with output
    text = text.replace("```", "")
    text = text.replace("**", "")
    
    # Clean up extra whitespace
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(line for line in lines if line)
    
    return text

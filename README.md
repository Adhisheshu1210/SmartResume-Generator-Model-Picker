# SmartResume-Generator — Model Picker

AI-powered Resume Generator using **Streamlit** + **Google Generative AI (Gemini)**

---

## Project Overview
SmartResume generates professional, **ATS-friendly** resumes by taking user input and using Google's Gemini model to produce tailored resume content. The app allows export to **TXT, DOCX, and PDF** formats.

**Key Features:**
- AI-generated professional resume content
- User-friendly interface with Streamlit
- Customizable resume style and industry focus
- Export resumes in **TXT, DOCX, PDF**
- ATS-friendly formatting
- Optional LinkedIn, GitHub, and contact info integration
- Mandatory fields check for Name, Job Title, Email, Phone, LinkedIn, GitHub, and Education

---

## Repository Structure
SmartResume-Generator/
│
├─ app.py # Streamlit main app
├─ resume_generator.py # AI prompt builder and model interaction
├─ requirements.txt # Python dependencies
├─ README.md # This file
└─ .streamlit/
└─ secrets.toml # Optional local API key storage (not committed)

---

## Prerequisites
- Python 3.8+
- Google Generative AI (Gemini) API key
- Internet connection for AI model access

---

## Installation

1. **Clone the repository**
git clone https://github.com/<your-username>/SmartResume-Generator.git
cd SmartResume-Generator

2. Create and activate virtual environment
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows
venv\Scripts\activate


3. Install dependencies
pip install -r requirements.txt


## API Key Setup
Option A: Streamlit Secrets
Create .streamlit/secrets.toml:
GEMINI_API_KEY = "your_api_key_here"
Option B: Environment Variable
# macOS / Linux
export GEMINI_API_KEY="your_api_key_here"
# Windows
set GEMINI_API_KEY="your_api_key_here"


## Running the App
streamlit run app.py
-Open the URL provided by Streamlit in your browser. Fill in your details, generate the resume, and download it in TXT, DOCX, or PDF.

Usage
1.Enter Full Name, Job Title, Email, Phone, LinkedIn URL, GitHub URL, and Education (mandatory fields)
2.Fill optional fields: Professional Summary, Skills, Experience, Projects
3.Choose Resume style and Industry
4.Click Generate Resume
5.Preview the resume
6.Download your resume in desired format (TXT, DOCX, PDF)

## Requirements
1. Create a requirements.txt file with:
streamlit==1.30.0
google-generativeai==0.2.6
fpdf==1.7.2
python-docx==0.8.12
requests==2.31.0

2. Install with:
pip install -r requirements.txt

## Git Setup (Optional)
echo "# SmartResume-Generator-Model-Picker" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/Adhisheshu1210/SmartResume-Generator-Model-Picker.git
git push -u origin main

# License
MIT License
Youtube link: https://youtu.be/Q3qg_NglykM
## Acknowledgements
Streamlit
Google Generative AI (Gemini)
FPDF & python-docx for document export"# SmartResume-Generator-Model-Picker" 

## 👤 Author

Adhisheshu
Power BI & Data Analytics Project


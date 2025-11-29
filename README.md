# 📞 AI Reception Agent – Call Transcription & Smart Logging
An intelligent virtual receptionist that transcribes call recordings, extracts key details using AI, and manages a searchable call log dashboard.

---

## ✨ Features

### 🎧 Audio Upload  
- Supports MP3, WAV, M4A, OGG  
- Built-in audio player  

### 🗣️ Automatic Transcription  
- Uses Whisper (local or API-based) to convert speech → text  

### 🤖 AI Call Understanding  
Powered by Groq Llama 3  
Extracts:
- Caller Name  
- Phone Number  
- Department  
- Summary  
- Priority (Low / Medium / High)  
- AI-Generated Response  

### 📝 Editable Fields  
All extracted details can be edited before saving.

### 📊 Call Logs Dashboard  
- Clean Streamlit dashboard  
- Priority color tags  
- Phone number masking (e.g., 9876******)  
- Search calls by name, department, summary or transcript  
- Delete entries  
- Duplicate call detection  

### 🔐 Security  
- Password-protected admin login  
- Sensitive information masking  
- Local SQLite storage (no cloud DB)
## 🛠️ Tech Stack

### UI / Frontend
- Streamlit

### AI Engine
- Whisper (speech-to-text)  
- Groq Llama 3 (LLM)

### Backend
- Python  
- Custom agent pipeline (agent.py)

### Database
- SQLite with SQLAlchemy ORM

---

## 📂 Project Structure

reception-agent/
│── streamlit_app.py # Main UI
│── agent.py # Transcription + AI analysis
│── database.py # DB operations
│── models.py # SQLAlchemy models
│── requirements.txt
│── README.md
│── ARCHITECTURE.md
│── calls.db # Auto-created database


---

## 🚀 Getting Started

### 🔧 Prerequisites
- Python 3.9+  
- Groq API Key  
- FFmpeg (recommended)

---

## 💻 Installation

### 1️⃣ Clone the repo
```bash
git clone https://github.com/yourusername/reception-agent.git
cd reception-agent

2️⃣ Create virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Add environment variables

Create .env file or set manually:

GROQ_API_KEY=your_groq_api_key
APP_ADMIN_PASSWORD=your_password

▶️ Run the Application
streamlit run streamlit_app.py


Open in browser:
👉 http://localhost:8501


---

# ✅ **BLOCK 3 — README.md (Part 3/3) + Complete ARCHITECTURE.md**  
Copy & paste this last block:


📞 How It Works

Upload call recording

Whisper transcribes audio

Llama 3 extracts structured fields:

Name

Phone

Department

Summary

Priority

AI response

User reviews & edits

Data saved in SQLite database

Dashboard shows:

Search

Delete

Full transcript

Priority badges

Duplicate prevention alerts if similar call exists

🔐 Security Features

Admin login

Masked phone numbers

Local-only data

No external DB

📋 Usage Instructions
📞 New Call

Upload audio

View transcript

Review AI-extracted details

Edit if needed

Save call

📋 Call Logs

View all call entries

Search using keywords

Expand for details

Delete if needed

⚠️ Troubleshooting
Whisper fails?

Install FFmpeg:

sudo apt install ffmpeg

Groq API error?

Check:

GROQ_API_KEY=your_key

Streamlit audio not playing?

Use MP3 or WAV.

📝 License

MIT License

🙏 Acknowledgments

Streamlit

Whisper

Groq Llama 3

SQLAlchemy

Open-source community


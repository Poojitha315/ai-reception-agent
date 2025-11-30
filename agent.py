import os
import json
import tempfile
from typing import Dict, Any

from groq import Groq

# Create Groq client using your API key from env
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def transcribe_audio(uploaded_file) -> str:
    """
    Transcribe an uploaded audio file using Groq Whisper model.
    This version does NOT require ffmpeg and works on Streamlit Cloud.
    """
    if uploaded_file is None:
        raise ValueError("No audio file uploaded")

    # Save the uploaded file temporarily
    suffix = os.path.splitext(uploaded_file.name)[1] or ".mp3"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name

    # Call Groq audio transcription API
    with open(tmp_path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=f,
            response_format="text",
            temperature=0.0,
        )

    # transcription is already plain text when response_format="text"
    return transcription


def analyze_call(transcript: str) -> Dict[str, Any]:
    """
    Analyze a call transcript using Llama 3 on Groq.
    Returns a dictionary with structured fields.
    """

    system_prompt = (
        "You are an AI assistant that extracts structured information from call transcripts "
        "for a reception/call-center scenario. "
        "Always respond with a valid JSON object only, with no extra text.\n\n"
        "The JSON must have these keys:\n"
        "- caller_name (string or empty)\n"
        "- phone (string, digits only if possible, or empty)\n"
        "- department (string like 'Support', 'Sales', 'Billing', etc.)\n"
        "- priority (one of: Low, Medium, High)\n"
        "- summary (1–2 sentence summary of the call)\n"
        "- response (a short suggested response for the receptionist)\n"
    )

    user_prompt = f"Here is the call transcript:\n\n{transcript}\n\nExtract the fields as JSON."

    # 🔁 IMPORTANT CHANGE: use a current Groq model
    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",   # <- new supported model
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    content = chat.choices[0].message.content.strip()

    # Clean possible ```json ... ``` wrapping
    if content.startswith("```"):
        content = content.strip("`")
        if content.lower().startswith("json"):
            content = content[4:].strip()

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Fallback: if JSON parsing fails, still return something useful
        data = {
            "caller_name": "",
            "phone": "",
            "department": "",
            "priority": "Medium",
            "summary": transcript[:500],
            "response": content,
        }

    # Normalize priority
    data["priority"] = (data.get("priority") or "Medium").capitalize()

    return data

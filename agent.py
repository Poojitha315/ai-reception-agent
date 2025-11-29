import os
import json
import tempfile
import whisper
from groq import Groq
from typing import Dict, Any, Optional
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Groq client
try:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set")
    groq_client = Groq(api_key=GROQ_API_KEY)
    USE_GROQ = True
except Exception as e:
    print(f"Warning: Failed to initialize Groq client: {str(e)}")
    USE_GROQ = False

# Initialize Whisper model
WHISPER_MODEL = None
try:
    WHISPER_MODEL = whisper.load_model("base")  # Using base model for faster processing
    print("Whisper model loaded successfully")
except Exception as e:
    print(f"Warning: Failed to load Whisper model: {str(e)}")
    WHISPER_MODEL = None

def transcribe_audio(audio_file) -> str:
    """
    Transcribe an audio file using local Whisper model.
    
    Args:
        audio_file: File-like object containing the audio data
        
    Returns:
        str: The transcribed text
        
    Raises:
        Exception: If transcription fails
    """
    if not WHISPER_MODEL:
        raise Exception("Whisper model not loaded. Please check the logs for errors.")
    
    try:
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            # Read the file content and write to temp file
            tmp_file.write(audio_file.getvalue())
            tmp_path = tmp_file.name
        
        # Transcribe the audio file
        result = WHISPER_MODEL.transcribe(tmp_path)
        
        # Clean up the temporary file
        try:
            os.unlink(tmp_path)
        except:
            pass
            
        return result["text"]
        
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")

def analyze_call(transcript: str) -> Dict[str, str]:
    """
    Analyze a call transcript using Groq's Llama 3 model.
    
    Args:
        transcript: The call transcript text
        
    Returns:
        Dict containing the extracted information:
        - caller_name: Name of the caller
        - phone: Caller's phone number
        - department: Relevant department
        - priority: Low/Medium/High
        - summary: Brief summary of the call
        - response: Suggested response
        
    Raises:
        Exception: If analysis fails
    """
    if not USE_GROQ:
        raise Exception("Groq client not initialized. Please check your GROQ_API_KEY.")
    
    system_prompt = """
    You are an AI receptionist analyzing a phone call transcript.
    Extract the following information as a JSON object with these exact keys:
    - caller_name: The name of the caller (or "Unknown" if not mentioned)
    - phone: The caller's phone number (or "Unknown" if not mentioned)
    - department: The department the caller is trying to reach (e.g., Sales, Support, Billing)
    - priority: The priority level (Low, Medium, or High)
    - summary: A 1-2 sentence summary of the call
    - response: A suggested response or action for the receptionist
    
    Respond with a valid JSON object only, with no additional text.
    """
    
    try:
        # Call Groq API
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Analyze this call transcript and extract the requested information. Here's the transcript:\n\n{transcript}"
                }
            ],
            model="openai/gpt-oss-20b",  # Using the 8B parameter model which is currently available
            temperature=0.2,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        
        # Extract the JSON response
        response_text = chat_completion.choices[0].message.content
        
        # Clean the response to ensure it's valid JSON
        try:
            # Try to find JSON in the response (in case model added extra text)
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx]
            
            result = json.loads(response_text)
            
            # Validate required fields
            required_fields = ['caller_name', 'phone', 'department', 'priority', 'summary', 'response']
            for field in required_fields:
                if field not in result:
                    result[field] = "Unknown"
            
            # Validate priority
            if result['priority'] not in ['Low', 'Medium', 'High']:
                result['priority'] = 'Medium'
                
            return result
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse model response as JSON: {str(e)}\nResponse: {response_text}")
            
    except Exception as e:
        raise Exception(f"Call analysis failed: {str(e)}")

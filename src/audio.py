import asyncio
import requests
import json
import google.generativeai as genai
from src.config import ELEVENLABS_API_KEY, GEMINI_API_KEY
from src.prompts import SSML_PROMPT

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

async def generate_ssml(text):
    """
    Rewrites text into SSML using Gemini for natural narration.
    """
    print("Generating SSML with Gemini...")
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(SSML_PROMPT.format(text=text))
        ssml_text = response.text
        
        # Basic cleanup to ensure it's just the SSML if the model adds markdown
        if "```xml" in ssml_text:
            ssml_text = ssml_text.split("```xml")[1].split("```")[0].strip()
        elif "```" in ssml_text:
            ssml_text = ssml_text.split("```")[1].split("```")[0].strip()
            
        return ssml_text
    except Exception as e:
        print(f"Error generating SSML: {e}")
        return text # Fallback to original text

async def generate_audio(text, output_path="audiobook.mp3", voice_id="21m00Tcm4TlvDq8ikWAM", stability=0.5, similarity_boost=0.75, style=0.0, use_speaker_boost=True):
    """
    Generates audio using ElevenLabs API.
    """
    print(f"Generating audio for {len(text)} characters using ElevenLabs ({voice_id})...")
    if not ELEVENLABS_API_KEY:
        print("ERROR: ELEVENLABS_API_KEY is missing!")
        raise Exception("ELEVENLABS_API_KEY is missing!")
    else:
        print(f"API Key present: {ELEVENLABS_API_KEY[:4]}...{ELEVENLABS_API_KEY[-4:]}")
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": use_speaker_boost
        }
    }
    
    try:
        # Run the blocking requests call in a thread pool to avoid blocking the event loop
        def make_request():
            return requests.post(url, headers=headers, json=payload)
        
        response = await asyncio.to_thread(make_request)
        
        if response.status_code == 200:
            # Write file in thread pool as well
            def write_file():
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return output_path
            
            result = await asyncio.to_thread(write_file)
            print(f"Audio saved to {result}")
            return result
        else:
            error_msg = f"ElevenLabs Error: {response.status_code} - {response.text}"
            print(error_msg)
            raise Exception(error_msg)
            
    except Exception as e:
        print(f"Exception in ElevenLabs TTS: {e}")
        raise e

def generate_audiobook(text, output_path="audiobook.mp3"):
    """
    Synchronous wrapper to run async generation.
    """
    try:
        return asyncio.run(generate_audio(text, output_path))
    except Exception as e:
        print(f"Error in audio wrapper: {e}")
        return None

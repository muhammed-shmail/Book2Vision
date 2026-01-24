import asyncio
import requests

from google import genai
from src.config import ELEVENLABS_API_KEY, GEMINI_API_KEY, DEEPGRAM_API_KEY
from src.prompts import SSML_PROMPT

# Configure Gemini
# genai.configure(api_key=GEMINI_API_KEY) # Not needed with new SDK client

async def generate_ssml(text):
    """
    Rewrites text into SSML using Gemini for natural narration.
    """
    print("Generating SSML with Gemini...")
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(model='gemini-2.0-flash', contents=SSML_PROMPT.format(text=text))
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

def format_text_for_deepgram(text: str) -> str:
    """
    Format text according to Deepgram best practices for natural speech.
    Based on: https://developers.deepgram.com/docs/improving-aura-2-formatting
    """
    import re
    
    # Preserve emotional markers like [laughs], [gasps], [sighs]
    # We'll temporarily replace them to avoid punctuation changes
    markers = re.findall(r'\[\w+\]', text)
    for i, marker in enumerate(markers):
        text = text.replace(marker, f"__MARKER_{i}__", 1)
    
    # Add comma before direct address names (e.g., "Hello Maria" -> "Hello, Maria")
    # Common names in podcast context
    common_names = ['Jax', 'Emma', 'Maria', 'John', 'Sarah']
    for name in common_names:
        text = re.sub(rf'\b(Hello|Hey|Hi|Wait|Listen)\s+{name}\b', rf'\1, {name}', text, flags=re.IGNORECASE)
    
    # Fix missing commas in common conversational patterns
    text = re.sub(r'\b(you know)\s+([A-Z])', r'\1, \2', text)  # "you know I" -> "you know, I"
    text = re.sub(r'\b(I mean)\s+([A-Z])', r'\1, \2', text)  # "I mean it" -> "I mean, it"
    text = re.sub(r'\b(honestly)\s+([A-Z])', r'\1, \2', text, flags=re.IGNORECASE)  # "honestly I" -> "honestly, I"
    text = re.sub(r'\b(like)\s+([A-Z])', r'\1, \2', text)  # "like I" -> "like, I" (only if followed by capital)
    
    # Ensure space before punctuation where needed
    text = re.sub(r'(\w)(\?|!)', r'\1 \2', text)  # Add space before ? and ! if missing
    text = re.sub(r'\s{2,}', ' ', text)  # Remove double spaces
    
    # Restore emotional markers
    for i, marker in enumerate(markers):
        text = text.replace(f"__MARKER_{i}__", marker)
    
    return text.strip()

def get_deepgram_voice(voice_id: str) -> str:
    """
    Map ElevenLabs/generic voice IDs to Deepgram Aura-2 voices.
    Uses Arcas (masculine) and Andromeda (feminine) - optimized for natural podcast conversations.
    """
    voice_map = {
        "pNInz6obpgDQGcFmaJgB": "aura-2-arcas-en",      # Adam -> Arcas (Masculine, natural, smooth, balanced for podcast hosting)
        "21m00Tcm4TlvDq8ikWAM": "aura-2-andromeda-en",  # Rachel -> Andromeda (Feminine, casual, expressive, warm, engaging)
    }
    return voice_map.get(voice_id, "aura-2-arcas-en")

async def generate_audio_deepgram(text, output_path, voice_id="21m00Tcm4TlvDq8ikWAM"):
    """
    Generates audio using Deepgram Aura-2 TTS API.
    Automatically selects appropriate voice based on voice_id mapping.
    """
    if not DEEPGRAM_API_KEY:
        print("ERROR: DEEPGRAM_API_KEY is missing!")
        raise Exception("DEEPGRAM_API_KEY is missing!")
    
    # Get the appropriate Deepgram voice
    deepgram_voice = get_deepgram_voice(voice_id)
    print(f"Generating audio using Deepgram Aura-2 ({deepgram_voice})...")
    
    url = f"https://api.deepgram.com/v1/speak?model={deepgram_voice}"
    
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Format text for natural speech using Deepgram best practices
    formatted_text = format_text_for_deepgram(text)
    
    payload = {
        "text": formatted_text
    }
    
    try:
        def make_request():
            return requests.post(url, headers=headers, json=payload)
            
        response = await asyncio.to_thread(make_request)
        
        if response.status_code == 200:
            def write_file():
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return output_path
            
            result = await asyncio.to_thread(write_file)
            print(f"✅ Deepgram audio saved: {result}")
            return result
        else:
            error_msg = f"Deepgram API Error: {response.status_code} - {response.text}"
            print(error_msg)
            raise Exception(error_msg)
    except Exception as e:
        print(f"❌ Deepgram failed: {e}")
        raise e

async def generate_audio(text, output_path="audiobook.mp3", voice_id="21m00Tcm4TlvDq8ikWAM", stability=0.5, similarity_boost=0.75, style=0.0, use_speaker_boost=True, provider="elevenlabs", speaking_rate=1.0):
    """
    Generates audio using the specified provider with automatic fallback.
    Priority: Deepgram -> Edge TTS (inbuilt)
    """
    print(f"🎵 Generating audio with provider: {provider} (Rate: {speaking_rate})")
    
    # Deepgram with automatic fallback to edge-tts
    if provider == "deepgram":
        if not DEEPGRAM_API_KEY:
            print("⚠️  Deepgram key missing. Falling back to Inbuilt (Edge TTS).")
            return await generate_audio_edge(text, output_path, voice_id, rate=speaking_rate)
        
        try:
            return await generate_audio_deepgram(text, output_path, voice_id)
        except Exception as e:
            print(f"⚠️  Deepgram failed: {e}. Falling back to Inbuilt (Edge TTS).")
            return await generate_audio_edge(text, output_path, voice_id, rate=speaking_rate)
    
    # Edge TTS (inbuilt)
    elif provider == "inbuilt":
        return await generate_audio_edge(text, output_path, voice_id, rate=speaking_rate)
    
    # ElevenLabs with fallback
    elif provider == "elevenlabs":
        if not ELEVENLABS_API_KEY:
            print("⚠️  ElevenLabs key missing. Falling back to Inbuilt (Edge TTS).")
            return await generate_audio_edge(text, output_path, voice_id, rate=speaking_rate)
        return await generate_audio_elevenlabs(text, output_path, voice_id, stability, similarity_boost, style, use_speaker_boost)
    
    # Default fallback
    else:
        print(f"⚠️  Unknown provider '{provider}'. Using Edge TTS.")
        return await generate_audio_edge(text, output_path, voice_id, rate=speaking_rate)

async def generate_audio_elevenlabs(text, output_path, voice_id, stability, similarity_boost, style, use_speaker_boost):
    """
    Generates audio using ElevenLabs API.
    """
    print(f"Generating audio for {len(text)} characters using ElevenLabs ({voice_id})...")
    if not ELEVENLABS_API_KEY:
        print("ERROR: ELEVENLABS_API_KEY is missing!")
        raise Exception("ELEVENLABS_API_KEY is missing!")
    else:
        print(f"API Key present: {bool(ELEVENLABS_API_KEY)}")
    
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
            if response.status_code == 401:
                if "missing_permissions" in response.text:
                    print("WARNING: ElevenLabs Key lacks 'text_to_speech' permission. Falling back to Edge TTS.")
                    raise Exception("ElevenLabs Key lacks 'text_to_speech' permission.")
                else:
                    raise Exception("Invalid ElevenLabs API Key.")
            raise Exception(error_msg)
            
    except Exception as e:
        print(f"Exception in ElevenLabs TTS: {e}")
        print("Falling back to Edge TTS...")
        return await generate_audio_edge(text, output_path, voice_id)

async def generate_audio_edge(text, output_path, voice_id=None, rate=1.0):
    """
    Fallback using edge-tts (free).
    """
    try:
        import edge_tts
        
        # Calculate rate string (e.g., "+10%", "-10%")
        rate_str = "+0%"
        if rate != 1.0:
            percent = int((rate - 1.0) * 100)
            sign = "+" if percent >= 0 else ""
            rate_str = f"{sign}{percent}%"
            
        print(f"Generating audio using Edge TTS (Rate: {rate_str})...")
        
        # Map ElevenLabs IDs to Edge Voices if possible, or use a default mapping
        edge_voice = "en-US-ChristopherNeural" # Default
        
        # Simple mapping for Podcast fallback
        # Adam (Jax) -> Guy
        # Rachel (Emma) -> Aria
        if "pNInz6obpgDQGcFmaJgB" in str(voice_id): # Adam ID
             edge_voice = "en-US-GuyNeural"
        elif "21m00Tcm4TlvDq8ikWAM" in str(voice_id): # Rachel ID
             edge_voice = "en-US-AriaNeural"
             
        communicate = edge_tts.Communicate(text, edge_voice, rate=rate_str)
        await communicate.save(output_path)
        print(f"Audio saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"Edge TTS failed: {e}")
        raise e



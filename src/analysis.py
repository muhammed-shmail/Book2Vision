# import spacy # Moved inside function
from collections import Counter
import json
import os
import google.generativeai as genai
from src.config import GEMINI_API_KEY
from src.gemini_utils import get_gemini_model

nlp = None

def load_spacy():
    global nlp
    if nlp is None:
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            print(f"Warning: Spacy load failed: {e}")
            nlp = None
    return nlp

def semantic_analysis(text):
    """
    Performs semantic analysis to extract entities and key concepts.
    Uses Gemini Pro if available, else Spacy.
    """
    # Fetch dynamically
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key:
        return semantic_analysis_with_llm(text, api_key)
        
    nlp_model = load_spacy()
    if not nlp_model:
        return {"entities": [], "keywords": []}
    
    doc = nlp_model(text[:100000]) # Limit to 100k chars for prototype speed
    
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    
    # Extract keywords (nouns and proper nouns)
    keywords = [token.text for token in doc if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop]
    common_keywords = Counter(keywords).most_common(10)
    
    return {
        "entities": entities,
        "keywords": common_keywords
    }

def semantic_analysis_with_llm(text, api_key):
    print("Using Gemini for Semantic Analysis...")
    
    try:
        model = get_gemini_model(capability="text", api_key=api_key)
        
        prompt = f"""
        You are an expert literary analyst and visual storytelling assistant.

        Your task is to analyze the following book text and produce a CLEAN, VALID JSON OBJECT.
        Follow these rules very carefully:

        1. SUMMARY
           - Write a concise plot summary in natural language.
           - Maximum 3 sentences.
           - No bullet points.

        2. ENTITIES (CHARACTERS)
           - Identify the main characters only (3–10 characters).
           - For each character, provide:
               - Their name as it appears in the text.
               - A short role label (e.g., "protagonist", "antagonist", "friend", "mentor", "villain", "side character").
           - Represent each character as: ["Character Name", "Role"].

        3. THEMES (KEYWORDS)
           - Extract 5–10 main themes of the story.
           - Each theme should be a short phrase of 1–3 words (e.g., "friendship", "betrayal", "coming of age").
           - Do NOT use generic words like "story", "book", "plot".

        4. VISUAL SCENES
           - Propose EXACTLY 3 scenes that would work well for image generation.
           - Each scene must be:
               - A single sentence or two short sentences.
               - Very visual, describing:
                   - Setting (where),
                   - Characters (who),
                   - Main action (what is happening),
                   - Important visual details (mood, lighting, key objects).
           - Avoid camera jargon (no "close-up shot", "frame", etc.).

        OUTPUT FORMAT (IMPORTANT):
        - Respond with EXACTLY ONE JSON OBJECT.
        - NO markdown, NO code fences, NO explanation.
        - NO trailing commas.
        - NO "..." placeholders.

        The JSON MUST follow this schema:

        {{
            "summary": "brief plot summary here",
            "entities": [
                ["Character Name 1", "Role 1"],
                ["Character Name 2", "Role 2"]
            ],
            "keywords": [
                "theme1",
                "theme2",
                "theme3"
            ],
            "scenes": [
                "Scene description 1",
                "Scene description 2",
                "Scene description 3"
            ]
        }}

        Now analyze this text (may be truncated if long):

        {text[:5000]}
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        print(f"Gemini Analysis Response: {response_text[:200]}...")  # Log first 200 chars
        
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        return json.loads(response_text)
        
    except Exception as e:
        print(f"Gemini Analysis Failed: {e}")
        return {"summary": "Analysis failed.", "entities": [], "keywords": []}


def chapter_segmentation(text):
    """
    Segments text into chapters based on headings.
    Simple heuristic: Look for "Chapter" or all-caps lines.
    """
    chapters = []
    lines = text.split('\n')
    current_chapter = {"title": "Introduction", "content": ""}
    
    for line in lines:
        if line.strip().lower().startswith("chapter") or (line.isupper() and len(line.strip()) < 50):
            if current_chapter["content"].strip():
                chapters.append(current_chapter)
            current_chapter = {"title": line.strip(), "content": ""}
        else:
            current_chapter["content"] += line + "\n"
            
    if current_chapter["content"].strip():
        chapters.append(current_chapter)
        
    return chapters

def identify_visual_content(text):
    """
    Identifies segments that are good for visualization.
    """
    # Placeholder: look for descriptive words
    visual_keywords = ["see", "look", "diagram", "figure", "image", "picture", "scene"]
    # This is a very basic heuristic
    return []

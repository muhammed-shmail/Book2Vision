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
        Analyze the following text from a book.
        1. Summarize the plot briefly (max 3 sentences).
        2. Extract key characters (names only).
        3. Extract main themes (keywords).
        4. Identify 3 key visual scenes suitable for image generation.
        
        Return JSON:
        {{
            "summary": "...",
            "entities": [["Name", "Role"]],
            "keywords": ["theme1", "theme2"],
            "scenes": ["scene description 1", ...]
        }}
        
        Text: {text[:5000]}...
        """
        
        response = model.generate_content(prompt)
        # Clean up response text if it contains markdown code blocks
        response_text = response.text.strip()
        print(f"Gemini Analysis Response: {response_text[:200]}...") # Log first 200 chars
        
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

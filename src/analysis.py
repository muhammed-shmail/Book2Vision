
from collections import Counter
import json
import os
import re
import asyncio
from google import genai
from src.config import GEMINI_API_KEY
from src.gemini_utils import get_gemini_model

# Compile regex pattern once for performance
CAPITALIZED_PATTERN = re.compile(r'\b[A-Z][a-z]+\b')

async def semantic_analysis(text):
    """
    Performs semantic analysis to extract entities and key concepts (Async).
    Priority: Gemini -> Basic Regex
    """
    # 1. Try Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"=== SEMANTIC ANALYSIS DEBUG ===")
    print(f"API Key present: {bool(api_key)}")
    if api_key:
        result = await semantic_analysis_with_llm(text, api_key)
        # If successful and has entities, return it
        if result and result.get("entities"):
            # Enforce minimum scenes
            ensure_minimum_scenes(result)

            print(f"✅ Gemini analysis succeeded. Found {len(result.get('entities', []))} entities and {len(result.get('scenes', []))} scenes.")
            return result
        print(f"❌ Gemini analysis failed or returned no entities. Result: {result}")
        print("Falling back...")


    # 3. Basic Regex Fallback
    print("Falling back to Basic Regex Analysis...")
    
    # Limit scan to first 10K characters for performance
    scan_text = text[:10000]
    words = CAPITALIZED_PATTERN.findall(scan_text)
    
    common_stops = {
        "The", "A", "An", "It", "He", "She", "They", "But", "And", "When", "Then", "Suddenly",
        "Meanwhile", "However", "Although", "Okay", "So", "If", "This", "That", "There", "Here",
        "What", "Why", "How", "Who", "Where", "Beneath", "Above", "Behind", "Inside", "Outside",
        "Near", "Far", "Just", "Only", "Very", "Really", "Now", "Later", "Soon", "Yesterday",
        "Today", "Tomorrow", "Yes", "No", "Please", "Thank", "Thanks", "Hello", "Hi", "Goodbye",
        "Mr", "Mrs", "Ms", "Dr", "Prof", "Captain", "Sergeant", "General", "King", "Queen",
        "Prince", "Princess", "Lord", "Lady", "Sir", "Madam", "One", "Two", "Three", "First",
        "Second", "Third", "Next", "Last", "Finally", "Also", "Besides", "Moreover", "Furthermore",
        "In", "On", "At", "To", "For", "With", "By", "From", "Of", "About", "As", "Like"
    }
    
    candidates = [w for w in words if w not in common_stops and len(w) > 2]
    
    # Count frequency
    counts = Counter(candidates)
    
    # Entity format: [name, role, visual_description]
    # Empty description for fallback since regex can't infer appearance
    top_entities = [
        [name, "Character", ""]  # description blank - not available from regex
        for name, count in counts.most_common(5)
    ]
    
    return {
        "entities": top_entities,
        "keywords": [],
        "scenes": [
            {
                "description": "The story begins, introducing the main characters and setting.",
                "excerpt": "The beginning...",
                "narrator_intro": "Our story starts here.",
                "emotion": "anticipation",
                "mood": "introductory",
                "environment": "opening scene"
            },
            {
                "description": "A key event occurs that sets the plot in motion.",
                "excerpt": "Something happens...",
                "narrator_intro": "Then, everything changed.",
                "emotion": "surprise",
                "mood": "dynamic",
                "environment": "key location"
            },
            {
                "description": "The tension rises as the characters face a challenge.",
                "excerpt": "The conflict grows...",
                "narrator_intro": "The stakes were getting higher.",
                "emotion": "tension",
                "mood": "intense",
                "environment": "challenging setting"
            },
            {
                "description": "The story reaches its conclusion or a dramatic moment.",
                "excerpt": "The climax approaches...",
                "narrator_intro": "Finally, the moment of truth.",
                "emotion": "dramatic",
                "mood": "climactic",
                "environment": "final setting"
            }
        ]
    }

from src.prompts import SEMANTIC_ANALYSIS_PROMPT

async def semantic_analysis_with_llm(text, api_key):
    print("Using Gemini for Semantic Analysis...")
    
    try:
        client, model_name = get_gemini_model(capability="text", api_key=api_key)
        
        prompt = SEMANTIC_ANALYSIS_PROMPT.format(text=text[:100000])
        
        # Run blocking generation in thread
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=model_name,
            contents=prompt
        )
        response_text = response.text.strip()
        print(f"Gemini Analysis Response: {response_text[:200]}...")  # Log first 200 chars
        
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        return json.loads(response_text)
        
    except Exception as e:
        import traceback
        print(f"Gemini Analysis Failed: {e}")
        traceback.print_exc()
        return {"entities": [], "keywords": []}


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

def ensure_minimum_scenes(analysis_result, min_scenes=4):
    """
    Ensures the analysis result has at least min_scenes.
    Pads with generic scenes if necessary.
    Modifies the dictionary in-place.
    """
    scenes = analysis_result.get("scenes", [])
    if len(scenes) < min_scenes:
        print(f"⚠️ Only {len(scenes)} scenes found. Padding to {min_scenes} with generic scenes.")
        defaults = [
            "The journey continues as the plot unfolds.",
            "A moment of quiet reflection or building tension.",
            "The characters face a new challenge or revelation.",
            "The story reaches a pivotal turning point.",
            "New developments change the course of events.",
            "The atmosphere shifts as the story progresses."
        ]
        
        # Add defaults until we have min_scenes
        needed = min_scenes - len(scenes)
        for i in range(needed):
            scenes.append({
                "description": defaults[i % len(defaults)],
                "excerpt": "The story continues...",
                "narrator_intro": "Moving forward...",
                "emotion": "neutral",
                "mood": "atmospheric",
                "environment": "in the story setting"
            })
        analysis_result["scenes"] = scenes
    return analysis_result


# Centralized Prompts Configuration

# --- 1. Audio & TTS Prompts ---

SSML_PROMPT = """
You are an expert audiobook director and SSML specialist.
Your goal is to transform the text into a deeply engaging, human-like performance.

Your task:
Rewrite the input text into SSML that sounds like a professional voice actor reading a story, not a robot reading text.

Key Guidelines for "Human" Quality:
1.  **Pacing & Rhythm:**
    -   Vary the speed. Slow down for dramatic or emotional moments (`rate="-10%"`). Speed up slightly for action or excitement (`rate="+5%"`).
    -   Use pauses effectively. Don't just pause at commas. Pause for effect before a big reveal or after a heavy statement (`<break time="300ms"/>`).
2.  **Intonation & Pitch:**
    -   Use `<prosody pitch="...">` to reflect the mood. Lower pitch slightly for serious/dark moments. Raise it for questions or excitement.
3.  **Emphasis:**
    -   Use `<emphasis level="moderate">` to highlight key words, just as a human would stress them.
4.  **Character Voices (Subtle):**
    -   If there is dialogue, try to slightly shift the pitch or rate to distinguish the speaker, but keep it subtle.

Strict Output Rules:
-   Wrap everything in `<speak>...</speak>`.
-   Use `<p>` and `<s>` tags for structure.
-   **DO NOT** add any extra words, intro, or outro.
-   **DO NOT** use markdown code blocks. Just return the raw XML string.

Input Text:
\"\"\"{text}\"\"\"
"""

PODCAST_PROMPT = """
You are the producer for "Booked & Busy", a high-energy morning radio show where books meet pop culture.
Your hosts are **{host1_name}** and **{host2_name}**.

**Host Personalities:**
*   **{host1_name} ({host1_gender}):** {host1_personality}
*   **{host2_name} ({host2_gender}):** {host2_personality}

**Show Style & Vibe:**
*   **Hyper-Realistic & Conversational:** This must sound like two friends chatting, NOT a script reading.
*   **Dynamic Flow:** Fast-paced, overlapping energy.
*   **Chemistry:** They finish each other's sentences, laugh together, and genuinely react.

**The Task:**
Create a dynamic 2-3 minute podcast script discussing the book content below.

**CRITICAL: REALISM RULES (Must Follow):**
1.  **INTERRUPTIONS:** Hosts must interrupt each other. Start sentences with "Wait," "But," "No way," or "Hold on" to simulate jumping in.
2.  **REACTIONS:** One host should react *while* the other is explaining something. (e.g., "Mmhmm," "Right," "Oh wow," "Exactly").
3.  **NATURAL FILLERS:** Use "like," "you know," "I mean," "honestly" to sound authentic (but don't overdo it).
4.  **SHORT TURNS:** No long monologues! Switch speakers every 1-2 sentences. Keep the rhythm fast.
5.  **EMOTIONAL VARIATION:** Go from whispering a secret to laughing out loud. Use [laughs], [gasps], [sighs] in the text (TTS will try to interpret context).

**CRITICAL: FORMATTING FOR NATURAL SPEECH:**
1.  **Use commas for pauses:** Add commas before names in direct address ("Hello, Maria"), between list items, and for natural conversational pauses.
2.  **Short phrases:** Break long sentences into shorter standalone phrases with periods for better pacing.
3.  **Proper punctuation:** Always end sentences with periods, questions with ?, exclamations with !
4.  **Space before punctuation:** Ensure there's always a space before ? and ! marks.
5.  **Good examples:**
    - ✓ "One moment, {host2_name}. I'm searching for that information."
    - ✓ "Would you like fries, a drink, or an apple pie ?"
    - ✗ "One moment {host2_name} I'm searching for that information"

**Structure:**
1.  **The Hook:** Immediate energy. Jump right into the topic.
2.  **The Juice:** The wildest part of the book. Gossip about the characters.
3.  **The Real Talk:** How this book makes you *feel*. Relatable life connections.
4.  **The Sign-Off:** Quick, punchy goodbye.

**Input Book Content:**
{text}

**Output Format (STRICT JSON):**
[
  {{"speaker": "{host1_name}", "text": "Okay, stop everything. Did you read the part where..."}},
  {{"speaker": "{host2_name}", "text": "The cliffhanger?! I literally screamed!"}},
  {{"speaker": "{host1_name}", "text": "Right?! I was like, no way that just happened."}},
  {{"speaker": "{host2_name}", "text": "I mean, honestly, I'm still recovering."}}
]
"""

# --- 2. Visual Prompts (Image Generation) ---

# Global negative prompt to ensure quality
NEGATIVE_PROMPT = "blurry, low quality, distorted, watermark, logo overlay, UI elements, buttons, 3d book mockup, floating book, background scene, framed artwork, poster layout, multiple covers, template design, canva style, stock photo, generic typography, bold flat text, white block letters, bad anatomy, deformed hands, extra limbs, 3d render, plastic, doll, mannequin, cgi, fake, toy, clay, sculpture"

# Enhanced templates with "magic words" for quality
IMAGE_PROMPT_TEMPLATE = """
Cinematic shot of {scene_description}, 
{style} style, midjourney v6 style, masterpiece, trending on artstation, highly detailed, dramatic lighting, volumetric fog, 
visual storytelling, 8k resolution, 16:9 aspect ratio, depth of field, ray tracing, 
no text, no watermark.
"""

ENTITY_PROMPT_TEMPLATE = """
Character portrait of {name} as {role}, 
{style} style, expressive face, soulfulness, organic textures, intricate details, 
soft studio lighting, rim lighting, 8k resolution, masterpiece, best quality, 
looking at viewer, detailed eyes, no text.
"""

TITLE_PROMPT_TEMPLATE = """
Book cover art for "{title}", 
{style} style, elegant, captivating, atmospheric, 
room for title text (but no actual text), 
high quality illustration, 16:9 aspect ratio, 
intricate details, professional composition.
"""

COVER_PROMPT_TEMPLATE = """
Professional FRONT book cover artwork for a published book.
This is a single flat front cover image ONLY — not a mockup, not a 3D book,
not a background scene, not a poster, not multiple covers.

Book title: '{title}'
Author: {author}
{theme_context}
{char_context}

Cover Design Requirements:
- Include the book title '{title}' clearly and prominently as part of the cover design, integrated naturally into the artwork.
- Typography must match the book's theme and mood — cinematic, atmospheric, and professional.
- Include the author name '{author}' in smaller, secondary placement.
- IMPORTANT: Generate ONLY the front cover artwork. No floating book, no mockup background.
- The artwork must fill the entire canvas edge-to-edge.

Composition:
- Single strong focal subject or scene placed in the center or lower third.
- Clear foreground, midground, and background separation.
- Minimal clutter. Strong silhouette and title readability.

Style:
- {style} cinematic realism, painterly digital art.
- Emotionally evocative, atmospheric, symbolic representation of the book's theme.
- Masterpiece, trending on artstation, 8k resolution.

Lighting & Color:
- Controlled dramatic lighting with intentional color grading.
- High contrast between subject and background.

Layout & Size:
- Vertical 5:8 aspect ratio, professional publishing-standard book cover.
- Ultra high detail, sharp focus, no distortion, no watermark.
"""

SCENE_PROMPT_TEMPLATE = """
{style} comic art.
SCENE ACTION: {scene_description}
STORY CONTEXT: {story_summary}

CAMERA & COMPOSITION: {camera_angle}. Dynamic perspective, depth of field.
ENVIRONMENT: {environment_context}

CHARACTERS (Keep consistent): {character_context}
(Focus on: OUTFITS, SIGNATURE PROPS, and PHYSICAL TRAITS. Ensure they are performing the ACTION).

Comic aesthetics: Bold ink linework, vibrant colors, dramatic shadows, dynamic motion lines.
Panel hints: Multi-panel composition with black borders separating scenes.
Quality: Masterpiece, 8k resolution, professional illustration.

CRITICAL: NO speech bubbles, NO dialogue text, NO captions.
NEGATIVE PROMPT: posing, looking at camera, character sheet, static, boring, repetitive, portrait, headshot, blank background.
"""

# --- 3. Semantic Analysis Prompts ---

SEMANTIC_ANALYSIS_PROMPT = """
You are an expert literary analyst and visual storytelling assistant.

Your task is to analyze the following book text and produce a CLEAN, VALID JSON OBJECT.
Follow these rules very carefully:

1. SUMMARY
   - Write a concise plot summary in natural language.
   - Maximum 3 sentences.
   - No bullet points.

2. ENTITIES (CHARACTERS)
   - Identify the main characters only (3–10 characters).
   - **CRITICAL**: Include ONLY sentient beings (people, animals, robots).
   - **DO NOT** include locations, organizations, objects, or abstract concepts.
   - For each character, provide:
       - Their name as it appears in the text.
       - A short role label (e.g., "protagonist", "antagonist", "friend", "mentor").
       - A concise VISUAL DESCRIPTION (e.g., "tall, red curly hair, green eyes"). **Focus on physical traits.**
       - **OUTFIT/CLOTHING**: Specific clothing details (e.g., "worn leather jacket, blue jeans", "shining silver armor").
       - **SIGNATURE PROP**: A key object they often carry (e.g., "glowing sword", "ancient book", "none").
   - Represent each character as: ["Character Name", "Role", "Visual Description", "Outfit", "Signature Prop"].

3. THEMES (KEYWORDS)
   - Extract 5–10 main themes of the story.
   - Each theme should be a short phrase of 1–3 words.

4. KEY SCENES
   - Identify **5-8 key scenes** that visually represent the ALL major plot points (ensure comprehensive coverage).
   - For each scene, provide:
       - "description": A descriptive sentence suitable for image generation (e.g., "The hero stands on a cliff overlooking the burning city, holding a glowing sword."). **Make it visual.**
       - "excerpt": The actual text from the book corresponding to this scene (approx. 2-3 sentences).
       - "narrator_intro": A short 1-sentence setup line for the narrator to introduce the scene.
       - "emotion": The dominant emotion of this scene (e.g., "fear", "triumph", "despair", "hope", "tension").
       - "mood": The visual mood/atmosphere (e.g., "dark and ominous", "bright and hopeful", "tense and shadowy", "peaceful and serene").
       - "environment": Specific setting details (e.g., "cyberpunk city with neon rain", "medieval village with thatched roofs").

OUTPUT FORMAT (IMPORTANT):
- Respond with EXACTLY ONE JSON OBJECT.
- NO markdown, NO code fences, NO explanation.
- NO trailing commas.
- NO "..." placeholders.

The JSON MUST follow this schema:

{{
    "summary": "brief plot summary here",
    "entities": [
        ["Character Name 1", "Role 1", "Visual Description 1", "Outfit 1", "Signature Prop 1"],
        ["Character Name 2", "Role 2", "Visual Description 2", "Outfit 2", "Signature Prop 2"]
    ],
    "keywords": [
        "theme1",
        "theme2",
        "theme3"
    ],
    "scenes": [
        {{
            "description": "Visual description of scene 1...",
            "excerpt": "The actual text from the book corresponding to this scene...",
            "narrator_intro": "A short 1-sentence setup line for the narrator...",
            "emotion": "dominant emotion",
            "mood": "visual atmosphere description",
            "environment": "specific setting details"
        }},
        {{
            "description": "Visual description of scene 2...",
            "excerpt": "The actual text from the book corresponding to this scene...",
            "narrator_intro": "A short 1-sentence setup line for the narrator...",
            "emotion": "dominant emotion",
            "mood": "visual atmosphere description",
            "environment": "specific setting details"
        }}
    ]
}}

Now analyze this text (may be truncated if long):

{text}
"""

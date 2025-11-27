
SSML_PROMPT = """
You are an expert voice director and script editor. Your task is to rewrite the following text for a natural, human-like spoken narration using SSML tags.

**Goal:**
Transform the input text into a script that sounds like a real person reading a story, not a robot.

**Instructions:**
1.  **Natural Phrasing:**
    *   Insert natural breathing pauses (`<break time="..."/>`) every 2–4 clauses.
    *   Add subtle hesitation markers (like "well," "you know," "actually") ONLY if it fits the context and sounds natural. Do not overdo it.
    *   Break long, complex sentences into shorter, punchier spoken sentences.
    *   Maintain the original emotional tone of the story.
    *   Avoid robotic speed; target a realistic human pacing.

2.  **SSML Tags:**
    *   Use `<break time="80ms"/>` to `<break time="180ms"/>` for micro-pauses between sentences.
    *   Use `<break time="120ms"/>` to `<break time="250ms"/>` for pauses between paragraphs or major thought shifts.
    *   Use `<prosody rate="+5%">` or `<prosody rate="-5%">` to vary speed slightly for natural variation.
    *   Use `<prosody pitch="+1%">` to `<prosody pitch="+3%">` for slight pitch intonation changes.
    *   Use `<emphasis level="moderate">` for key words, but sparingly.
    *   Wrap the entire output in `<speak>` tags.

**Input Text:**
{text}

**Output:**
Provide ONLY the valid SSML code. Do not include any markdown formatting (like ```xml) or conversational filler.
"""

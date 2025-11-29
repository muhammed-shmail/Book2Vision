import os
# from moviepy.editor import ImageClip, AudioFileClip, ConcatenateVideoclips
# import moviepy.editor as mp

# from openai import OpenAI
# from src.config import OPENAI_API_KEY, IMAGE_MODEL, IMAGE_SIZE, IMAGE_QUALITY
import requests
import os
import urllib.parse

import re
import random

def generate_entity_image(entity_name, entity_role, output_dir, seed=None):
    """
    Generates a circular-ready avatar image for an entity.
    """
    if seed is None:
        seed = random.randint(0, 10000)
        
    prompt = (
        f"Close-up portrait of {entity_name} as {entity_role}, "
        f"centered character, facing the viewer, storybook illustration style, "
        f"cute, expressive, highly detailed, soft diffused lighting, "
        f"clean plain white background, no text, no logo, no watermark, "
        f"framed to work well as a circular avatar."
    )
    encoded_prompt = urllib.parse.quote(prompt)
    
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=flux&seed={seed}&width=512&height=512&nologo=true"
    
    safe_name = re.sub(r'[\\/*?:"<>|\n\r]', "_", entity_name)
    filename = f"entity_{safe_name}.jpg"
    img_path = os.path.join(output_dir, filename)
    
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(img_path, 'wb') as handler:
                handler.write(response.content)
            return img_path
    except Exception as e:
        print(f"Error generating entity image for {entity_name}: {e}")
        return None

def generate_images(semantic_map, output_dir, style="storybook", seed=None, title=None):
    """
    Generates images based on semantic analysis using Pollinations.ai (Free).
    All images are generated in 16:9 aspect ratio (1920x1080).
    """
    images = []
    
    if seed is None:
        seed = random.randint(0, 10000)
    
    print(f"Generating images with style: {style} (Seed: {seed})")

    # 1. Generate Title Page (if title is provided)
    if title:
        print(f"Generating Title Page for: {title}")
        try:
            if style == "storybook":
                prompt = (
                    f"Front book cover for a children's story titled '{title}', "
                    f"whimsical storybook illustration style, bright and colorful, "
                    f"magical and inviting atmosphere, soft lighting, decorative border, "
                    f"ample clean space for bold readable title text in the center, "
                    f"no logo, no watermark, 16:9 aspect ratio."
                )
            else:
                prompt = (
                    f"Cinematic book or movie poster for a story titled '{title}', "
                    f"dramatic composition, strong focal point, high contrast, "
                    f"atmospheric lighting, realistic or semi-realistic style, "
                    f"title area clearly visible and readable, ultra detailed, "
                    f"epic 8k look, no logo, no watermark, 16:9 aspect ratio."
                )
            
            encoded_prompt = urllib.parse.quote(prompt)
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=flux&seed={seed}&width=1920&height=1080&nologo=true"
            
            response = requests.get(image_url)
            if response.status_code == 200:
                safe_title = re.sub(r'[\\/*?:"<>|\n\r]', "_", title)[:50]
                filename = f"image_00_title_{safe_title}.jpg"
                img_path = os.path.join(output_dir, filename)
                
                with open(img_path, 'wb') as handler:
                    handler.write(response.content)
                
                images.append(img_path)
                print(f"Saved Title Page: {img_path}")
            else:
                print(f"Failed to download title page: {response.status_code}")
        except Exception as e:
            print(f"Error generating title page: {e}")

    # 2. Generate Entity Images
    entities = semantic_map.get("entities", [])[:5]
    scenes = semantic_map.get("scenes", [])
    
    for i, entity in enumerate(entities):
        if isinstance(entity, list) and len(entity) >= 2:
            name, role = entity[0], entity[1]
        elif isinstance(entity, tuple) and len(entity) >= 2:
            name, role = entity[0], entity[1]
        else:
            name = str(entity)
            role = "Character"
        
        prompt = (
            f"Full or mid-shot illustration of {name} as {role}, "
            f"{style} style, highly detailed, vibrant colors, "
            f"clear character design, expressive pose, visually appealing background, "
            f"cinematic 16:9 composition, no text, no logo, no watermark."
        )
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=flux&seed={seed+i+1}&width=1920&height=1080&nologo=true"
        
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                safe_name = re.sub(r'[\\/*?:"<>|\n\r]', "_", name)[:30]
                filename = f"image_{i+1:02d}_entity_{safe_name}.jpg"
                img_path = os.path.join(output_dir, filename)
                
                with open(img_path, 'wb') as handler:
                    handler.write(response.content)
                
                images.append(img_path)
                print(f"Saved entity image: {img_path}")
            else:
                print(f"Failed to download image for {name}: {response.status_code}")
        except Exception as e:
            print(f"Error generating image for {name}: {e}")
            
    return images

def generate_video(summary_text, audio_path, image_paths, output_path="video.mp4"):
    """
    Generates a video summary.
    """
    print("Generating video...")
    try:
        # Placeholder for moviepy logic
        # audio = AudioFileClip(audio_path)
        # clip = ImageClip(image_paths[0]).set_duration(audio.duration)
        # clip = clip.set_audio(audio)
        # clip.write_videofile(output_path, fps=24)
        print(f"Video generation logic would run here. Output: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error generating video: {e}")
        return None

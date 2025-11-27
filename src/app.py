import streamlit as st
import os
import sys
import base64
# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import shutil
from src.ingestion import ingest_book
from src.analysis import semantic_analysis
from src.audio import generate_audiobook
from src.visuals import generate_images, generate_entity_image
from src.knowledge import generate_quizzes
import json

# Page Config
st.set_page_config(
    page_title="Book2Vision",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load CSS
def load_css():
    with open("src/styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize Session State
if "ingestion_result" not in st.session_state:
    st.session_state.ingestion_result = None
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "audio_path" not in st.session_state:
    st.session_state.audio_path = None
if "images_list" not in st.session_state:
    st.session_state.images_list = []
if "entity_images" not in st.session_state:
    st.session_state.entity_images = {}
if "seed" not in st.session_state:
    st.session_state.seed = 42

# --- UI Layout ---

# 1. Navbar
st.markdown("""
<div class="navbar">
    <div class="navbar-title">📚 Book2Vision</div>
    <div>
        <!-- Buttons are handled by Streamlit below, this is just for layout visual -->
    </div>
</div>
""", unsafe_allow_html=True)

# Main Layout: Split Panels
col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📂 Upload & Entities")
    
    uploaded_file = st.file_uploader("Upload Book", type=["pdf", "txt", "epub"], label_visibility="collapsed")
    
    if uploaded_file:
        temp_dir = "temp_upload"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, uploaded_file.name)
        
        # Save only if not already processed or different file
        if not st.session_state.ingestion_result or st.session_state.ingestion_result.get("filename") != uploaded_file.name:
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            with st.spinner("Analyzing..."):
                ingestion_result = ingest_book(file_path)
                ingestion_result["filename"] = uploaded_file.name # Track filename
                st.session_state.ingestion_result = ingestion_result
                st.session_state.full_text = ingestion_result.get("full_text", "")
                
                analysis = semantic_analysis(st.session_state.full_text)
                st.session_state.analysis_result = analysis
                st.rerun()

    # Display Entities
    if st.session_state.analysis_result:
        st.markdown("### Characters")
        entities = st.session_state.analysis_result.get("entities", [])[:5]
        
        for ent in entities:
            name = ent[0]
            role = ent[1]
            
            # Generate Entity Image if missing
            if name not in st.session_state.entity_images:
                img_dir = os.path.join("temp_upload", "entities")
                os.makedirs(img_dir, exist_ok=True)
                img_path = generate_entity_image(name, role, img_dir, seed=st.session_state.seed)
                if img_path:
                    st.session_state.entity_images[name] = img_path
            
            img_src = st.session_state.entity_images.get(name, "")
            
            # Read image as base64 for embedding
            img_b64 = ""
            if img_src and os.path.exists(img_src):
                with open(img_src, "rb") as img_f:
                    img_b64 = base64.b64encode(img_f.read()).decode()
            
            st.markdown(f"""
            <div class="entity-container">
                <img src="data:image/jpg;base64,{img_b64}" class="entity-circle">
                <div>
                    <div class="entity-name">{name}</div>
                    <div class="entity-role">{role}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="glass-card storybook-container">', unsafe_allow_html=True)
    st.subheader("📖 Storybook Preview")
    
    if st.session_state.ingestion_result:
        # Control Buttons
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("✨ Generate Visuals", use_container_width=True):
                with st.spinner("Painting the story..."):
                    visuals_dir = os.path.join("temp_upload", "visuals")
                    os.makedirs(visuals_dir, exist_ok=True)
                    images = generate_images(st.session_state.analysis_result, visuals_dir, style="storybook", seed=st.session_state.seed)
                    st.session_state.images_list = images
                    st.rerun()
                    
        with btn_col2:
            if st.button("🔊 Generate Audio", use_container_width=True):
                with st.spinner("Narrating the story..."):
                    # Use the clean story body for TTS, fallback to full text if missing
                    tts_text = st.session_state.ingestion_result.get("body", st.session_state.full_text)
                    # Limit for demo speed if needed, but let's try full or larger chunk
                    preview_text = tts_text[:2000] 
                    output_path = os.path.join("temp_upload", "audiobook.mp3")
                    
                    audio_file = generate_audiobook(preview_text, output_path)
                    
                    if audio_file:
                        st.session_state.audio_path = audio_file
                        st.success("Audio Generated!")
                        st.rerun()

        # Audio Player
        if st.session_state.audio_path:
            st.audio(st.session_state.audio_path)

        # Display Story content interleaved with images
        story_text = st.session_state.ingestion_result.get("body", "")
        paragraphs = story_text.split("\n\n")
        
        # Simple interleaving logic: Show an image every few paragraphs
        img_idx = 0
        for i, para in enumerate(paragraphs):
            if not para.strip():
                continue
                
            st.markdown(f'<div class="story-text">{para}</div>', unsafe_allow_html=True)
            
            # Inject image if available
            if st.session_state.images_list and img_idx < len(st.session_state.images_list) and i % 3 == 0:
                st.image(st.session_state.images_list[img_idx], use_column_width=True)
                img_idx += 1
                
    else:
        st.info("Upload a book to see the story here.")
        
    st.markdown('</div>', unsafe_allow_html=True)

# Bottom Bar
st.markdown("""
<div class="bottom-bar">
    <div>
        <span style="font-weight:bold; margin-right:10px;">Voice:</span>
        <span>Aura Asteria</span>
    </div>
    <div>
        <span style="font-weight:bold; margin-right:10px;">Style:</span>
        <span>Storybook</span>
    </div>
    <div>
        <span style="font-weight:bold; margin-right:10px;">Seed:</span>
        <span>42</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Hidden Settings (controlled by bottom bar conceptually, but implemented here for now)
# In a real app, we'd make the bottom bar interactive with st.columns inside a container, 
# but for the pure CSS visual requested, this static bar works for the "look".
# We can add actual controls if needed.

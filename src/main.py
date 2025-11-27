import argparse
import os
import sys

# Add project root to sys.path to fix ModuleNotFoundError
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion import ingest_book, clean_format
from src.analysis import semantic_analysis, chapter_segmentation
from src.audio import generate_audiobook
from src.visuals import generate_images, generate_video
from src.knowledge import generate_flashcards, generate_quizzes, generate_mindmap

def main():
    parser = argparse.ArgumentParser(description="Book2Vision - Automated Book-to-Multimedia Conversion")
    parser.add_argument("input_file", help="Path to the input book file (PDF, EPUB, TXT)")
    parser.add_argument("--output_dir", default="Book2Vision_Output", help="Directory to save output")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: File {args.input_file} not found.")
        return

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Processing {args.input_file}...")
    
    # Step 1: Ingestion
    print("\n--- Step 1: Ingestion ---")
    ingestion_result = ingest_book(args.input_file)
    raw_text = ingestion_result.get("full_text", "")
    clean_text = clean_format(raw_text)
    print(f"Extracted {len(clean_text)} characters.")
    
    # Step 2: Analysis
    print("\n--- Step 2: Analysis ---")
    semantic_data = semantic_analysis(clean_text)
    chapters = chapter_segmentation(clean_text)
    print(f"Identified {len(chapters)} chapters and {len(semantic_data.get('entities', []))} entities.")
    
    # Step 3: Audiobook
    print("\n--- Step 3: Audiobook ---")
    audio_dir = os.path.join(args.output_dir, "Audiobook")
    os.makedirs(audio_dir, exist_ok=True)
    generate_audiobook(clean_text[:500], os.path.join(audio_dir, "preview.mp3")) # Preview only for speed
    
    # Step 4: Visuals
    print("\n--- Step 4: Visuals ---")
    visuals_dir = os.path.join(args.output_dir, "Visuals")
    os.makedirs(visuals_dir, exist_ok=True)
    # Use a fixed seed for consistency across runs, or random for variety
    images = generate_images(semantic_data, visuals_dir, seed=42)
    generate_video(clean_text[:500], "dummy_audio_path", images, os.path.join(visuals_dir, "summary.mp4"))
    
    # Step 5: Knowledge Tools
    print("\n--- Step 5: Knowledge Tools ---")
    knowledge_dir = os.path.join(args.output_dir, "Knowledge")
    os.makedirs(knowledge_dir, exist_ok=True)
    generate_flashcards(clean_text, os.path.join(knowledge_dir, "flashcards.json"))
    generate_quizzes(clean_text, os.path.join(knowledge_dir, "quiz.json"))
    
    print(f"\nDone! Output saved to {args.output_dir}")

if __name__ == "__main__":
    main()

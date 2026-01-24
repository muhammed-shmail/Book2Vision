import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.visuals import generate_entity_image

async def test_gen():
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating test image...")
    path = await generate_entity_image("Test Character", "Protagonist", output_dir)
    
    if path:
        print(f"Success! Image saved to: {path}")
    else:
        print("Failed to generate image.")

if __name__ == "__main__":
    asyncio.run(test_gen())

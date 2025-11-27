# Book2Vision

**Book2Vision** is an automated system designed to transform digital books (PDF, EPUB, TXT) into complete multimedia packages, including audiobooks, video summaries, image packs, and knowledge tools.

## Features

*   **Ingestion**: Supports PDF, EPUB, and TXT formats.
*   **Analysis**: Extracts text, identifies chapters, and performs semantic analysis.
*   **Audiobook**: Generates audiobooks using TTS.
3.  Install Tesseract OCR (required for scanned PDFs).
4.  Download Spacy model:
    ```bash
    python -m spacy download en_core_web_sm
    ```

## Usage

1.  Start the server:
    ```bash
    uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload
    ```
2.  Open your browser and navigate to `http://localhost:8000`.
3.  Upload a book to start the transformation.

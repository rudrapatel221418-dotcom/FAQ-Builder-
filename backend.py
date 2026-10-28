import os
import shutil
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from main import read_document, generate_summary_and_faq


# ==========================================
# 1. CREATE FASTAPI APP
# ==========================================

app = FastAPI(
    title="FAQ Builder & Document Summarizer API",
    description="API for generating document summaries and FAQs using Groq.",
    version="1.0.0"
)


# ==========================================
# 2. CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi.responses import FileResponse

# ==========================================
# 3. HOME ENDPOINT (Serves index.html or API info)
# ==========================================

@app.get("/")
def home():
    index_file = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "message": "FAQ Builder & Document Summarizer API is running",
        "docs": "/docs"
    }



# ==========================================
# 4. HEALTH CHECK
# ==========================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# ==========================================
# 5. GENERATE SUMMARY + FAQ
# ==========================================

@app.post("/generate")
async def generate(
    file: UploadFile = File(...)
):

    # --------------------------------------
    # Check file
    # --------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    # --------------------------------------
    # Check extension
    # --------------------------------------

    extension = os.path.splitext(file.filename)[1].lower()

    allowed_extensions = [
        ".txt",
        ".pdf",
        ".docx"
    ]

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file format. "
                "Only TXT, PDF and DOCX files are allowed."
            )
        )

    # --------------------------------------
    # Create temporary file
    # --------------------------------------

    temp_file = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp:

            temp_file = temp.name

            shutil.copyfileobj(
                file.file,
                temp
            )

        # ----------------------------------
        # Read document
        # ----------------------------------

        document = read_document(temp_file)

        if not document.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the document."
            )

        # ----------------------------------
        # Generate summary + FAQ
        # ----------------------------------

        result = generate_summary_and_faq(document)

        # ----------------------------------
        # Return response
        # ----------------------------------

        return {
            "success": True,
            "filename": file.filename,
            "result": result
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        # ----------------------------------
        # Delete temporary file
        # ----------------------------------

        if temp_file and os.path.exists(temp_file):

            os.remove(temp_file)


# ==========================================
# 6. RUN DIRECTLY
# ==========================================

if __name__ == "__main__":
    import uvicorn
    print("Starting FAQ Builder Server on http://127.0.0.1:8000 ...")
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)
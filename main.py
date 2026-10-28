import os
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader
from docx import Document


# ==========================================
# 1. LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found. "
        "Please add it to your .env file."
    )


# ==========================================
# 2. CREATE GROQ CLIENT
# ==========================================

client = Groq(api_key=api_key)


# ==========================================
# 3. GROQ MODEL
# ==========================================

MODEL = "openai/gpt-oss-20b"


# ==========================================
# 4. READ TXT FILE
# ==========================================

def read_txt(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# ==========================================
# 5. READ PDF FILE
# ==========================================

def read_pdf(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# ==========================================
# 6. READ DOCX FILE
# ==========================================

def read_docx(file_path):

    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:

        if paragraph.text.strip():
            text += paragraph.text + "\n"

    return text


# ==========================================
# 7. READ DOCUMENT
# ==========================================

def read_document(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".txt":

        return read_txt(file_path)

    elif extension == ".pdf":

        return read_pdf(file_path)

    elif extension == ".docx":

        return read_docx(file_path)

    else:

        raise ValueError(
            "Unsupported file format.\n"
            "Supported formats: TXT, PDF, DOCX"
        )


# ==========================================
# 8. GENERATE SUMMARY + FAQ
# ==========================================

def generate_summary_and_faq(document):

    # --------------------------------------
    # Count words
    # --------------------------------------

    word_count = len(document.split())

    # Target approximately 1/3
    target_words = max(100, word_count // 3)

    print(f"Original document words: {word_count}")
    print(
        f"Target summary words: approximately {target_words}"
    )


    # --------------------------------------
    # Prompt
    # --------------------------------------

    prompt = f"""
You are a document summarization and FAQ generation assistant.

You will receive a document.

Your job is to perform TWO tasks.

========================
TASK 1: SUMMARY
========================

Create a summary of approximately {target_words} words.

IMPORTANT:
The summary MUST be written as clear bullet points.
Do NOT write the summary as a paragraph.

Summary requirements:

- Use bullet points.
- Each bullet point should contain one important idea.
- Each bullet point should be clear and meaningful.
- Cover the major concepts and important information from the document.
- Preserve important facts, concepts, names and dates.
- Remove unnecessary repetition.
- Use simple and easy-to-understand language.
- Use only information from the document.
- Do NOT invent information.
- Do NOT add information that is not present in the document.
- Do NOT combine unrelated ideas into one bullet point.
- Prefer around 8-15 meaningful bullet points when appropriate.
- The number of bullet points can be different if the document is very short or very long.

========================
TASK 2: FAQ
========================

Create 10 Frequently Asked Questions based ONLY
on the document.

For each FAQ:

- Create a useful question.
- Give a clear answer.
- Keep the answer concise.
- Do not use information outside the document.
- Do not invent facts.

========================
OUTPUT FORMAT
========================

SUMMARY
=======

- Important point from the document.
- Another important point from the document.
- Another important concept or fact.
- Another important point.
- Another important point.


FAQ
===

1. Question: ...
   Answer: ...

2. Question: ...
   Answer: ...

3. Question: ...
   Answer: ...

4. Question: ...
   Answer: ...

5. Question: ...
   Answer: ...

6. Question: ...
   Answer: ...

7. Question: ...
   Answer: ...

8. Question: ...
   Answer: ...

9. Question: ...
   Answer: ...

10. Question: ...
    Answer: ...


========================
DOCUMENT
========================

{document}
"""


    # --------------------------------------
    # Send request to Groq
    # --------------------------------------

    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert document "
                    "summarization and FAQ assistant. "
                    "Always follow the requested output format."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2
    )


    # --------------------------------------
    # Get response
    # --------------------------------------

    result = response.choices[0].message.content

    return result


# ==========================================
# 9. MAIN PROGRAM
# ==========================================

if __name__ == "__main__":

    print("=" * 60)
    print("      FAQ BUILDER & DOCUMENT SUMMARIZER")
    print("=" * 60)

    print("\nSupported files:")
    print("1. TXT")
    print("2. PDF")
    print("3. DOCX")

    print()

    file_path = input(
        "Enter document path: "
    ).strip()

    try:

        # ----------------------------------
        # Read document
        # ----------------------------------

        print("\nReading document...")

        document = read_document(file_path)

        if not document.strip():

            raise ValueError(
                "No text could be extracted from the document."
            )

        print("Document successfully read.")


        # ----------------------------------
        # Generate result
        # ----------------------------------

        print("\nSending document to Groq...")
        print("Generating summary and FAQs...")
        print("Please wait...\n")

        result = generate_summary_and_faq(document)


        # ----------------------------------
        # Display result
        # ----------------------------------

        print("=" * 60)
        print("              RESULT")
        print("=" * 60)

        print(result)

        print("\n" + "=" * 60)
        print("              COMPLETED")
        print("=" * 60)


    except Exception as e:

        print("\n" + "=" * 60)
        print("ERROR")
        print("=" * 60)

        print(e)
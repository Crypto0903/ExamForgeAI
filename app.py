from flask import Flask, render_template, request, send_file
from groq import Groq
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import os
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from dotenv import load_dotenv

app = Flask(__name__)

# ==========================================
# CONFIG
# ==========================================

UPLOAD_FOLDER = "uploads"
GENERATED_FOLDER = "generated"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

# ==========================================
# LOAD ENV
# ==========================================

load_dotenv()

# ==========================================
# GROQ API
# ==========================================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ==========================================
# EXTRACT TEXT FROM DOCX
# ==========================================

def extract_text(path):

    text = ""

    with zipfile.ZipFile(path, "r") as z:

        xml_content = z.read("word/document.xml")

        tree = ET.fromstring(xml_content)

        for elem in tree.iter():

            if elem.text:
                text += elem.text + " "

    return text


# ==========================================
# CREATE VECTOR STORE (RAG)
# ==========================================

def create_vector_store(text):

    chunks = [
        text[i:i+700]
        for i in range(0, len(text), 700)
    ]

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform(chunks)

    return vectorizer, vectors, chunks


# ==========================================
# RETRIEVE CONTEXT
# ==========================================

def retrieve_context(query, vectorizer, vectors, chunks, k=8):

    query_vec = vectorizer.transform([query])

    scores = (vectors @ query_vec.T).toarray().flatten()

    top_indices = np.argsort(scores)[-k:][::-1]

    return " ".join([chunks[i] for i in top_indices])


# ==========================================
# AI SUBJECT DETECTION
# ==========================================

def detect_subject_ai(text):

    sample_text = text[:4000]

    prompt = f"""
You are an academic assistant.

Analyze the syllabus and identify:

1. Subject Name
2. Programme Name
3. Exam Title

Return ONLY in this format:

SUBJECT: ...
PROGRAMME: ...
EXAM: ...

Syllabus:
{sample_text}
"""

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    result = response.choices[0].message.content

    subject = "Question Paper"
    programme = "MCA"
    exam = "Semester Examination"

    for line in result.split("\n"):

        if "SUBJECT:" in line.upper():
            subject = line.split(":")[-1].strip()

        elif "PROGRAMME:" in line.upper():
            programme = line.split(":")[-1].strip()

        elif "EXAM:" in line.upper():
            exam = line.split(":")[-1].strip()

    return subject, programme, exam


# ==========================================
# EXTRACT QUESTIONS
# ==========================================

def extract_questions(text):

    pattern = r"(Q\d+\..*?)(?=Q\d+\.|$)"

    questions = re.findall(pattern, text, re.S)

    return questions


# ==========================================
# REMOVE DUPLICATES
# ==========================================

def remove_duplicates(questions):

    seen = set()

    unique = []

    for q in questions:

        cleaned = re.sub(r"\s+", " ", q.lower()).strip()

        if cleaned not in seen:

            seen.add(cleaned)

            unique.append(q)

    return unique


# ==========================================
# GENERATE QUESTIONS
# ==========================================

def generate_paper(context, qtype, difficulty):

    if qtype == "mcq":

        format_rules = """
Q1. Question
A)
B)
C)
D)
Answer:
"""

    elif qtype == "descriptive":

        format_rules = """
Q1. Explain...
"""

    else:

        format_rules = """
Q1. Define...
"""

    all_questions = []

    while len(all_questions) < 50:

        prompt = f"""
Generate EXACTLY 20 UNIQUE questions.

Type: {qtype}
Difficulty: {difficulty}

STRICT RULES:
- NO markdown
- NO bold text
- NO ** symbols
- Plain clean university format
- No repeated concepts
- No duplicate questions
- Proper numbering Q1, Q2...
- Questions must look like real university exam paper
- Questions should be syllabus specific
- Cover syllabus evenly
- No explanation outside questions

FORMAT:
{format_rules}

Context:
{context}
"""

        response = client.chat.completions.create(

            model="llama-3.1-8b-instant",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        generated_text = response.choices[0].message.content

        generated_text = re.sub(r"\*\*", "", generated_text)

        questions = extract_questions(generated_text)

        all_questions.extend(questions)

        all_questions = remove_duplicates(all_questions)

    final_questions = all_questions[:50]

    cleaned_questions = []

    for i, q in enumerate(final_questions, 1):

        q = re.sub(r"Q\d+\.", f"Q{i}.", q)

        cleaned_questions.append(q)

    return cleaned_questions


# ==========================================
# SAVE DOCX
# ==========================================

def save_docx(filename, questions, qtype, syllabus_text):

    doc = Document()

    # ==========================================
    # AI HEADER DETECTION
    # ==========================================

    subject, programme, exam = detect_subject_ai(syllabus_text)

    # ==========================================
    # PAGE SETTINGS
    # ==========================================

    section = doc.sections[0]

    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    # ==========================================
    # MAIN HEADING
    # ==========================================

    heading = doc.add_paragraph()

    heading.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    run = heading.add_run(subject.upper())

    run.bold = True
    run.font.size = Pt(20)

    # ==========================================
    # SUB HEADING
    # ==========================================

    sub_heading = doc.add_paragraph()

    sub_heading.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    run = sub_heading.add_run(exam.upper())

    run.bold = True
    run.font.size = Pt(13)

    # ==========================================
    # DETAILS TABLE
    # ==========================================

    table = doc.add_table(rows=4, cols=2)

    table.style = "Table Grid"

    table.cell(0,0).text = "Programme"
    table.cell(0,1).text = programme

    table.cell(1,0).text = "Subject"
    table.cell(1,1).text = subject

    table.cell(2,0).text = "Time"
    table.cell(2,1).text = "2 Hours"

    table.cell(3,0).text = "Maximum Marks"
    table.cell(3,1).text = "50"

    doc.add_paragraph("")

    # ==========================================
    # INSTRUCTIONS
    # ==========================================

    ins = doc.add_paragraph()

    run = ins.add_run("Instructions:\n")

    run.bold = True
    run.font.size = Pt(11)

    instructions = [
        "1. Answer all questions.",
        "2. Figures to the right indicate marks.",
        "3. Assume suitable data wherever necessary.",
        "4. Maintain neat and clear presentation."
    ]

    for i in instructions:
        ins.add_run(i + "\n")

    doc.add_paragraph("")

    # ==========================================
    # SECTION A
    # ==========================================

    sec_a = doc.add_paragraph()

    sec_a.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    run = sec_a.add_run("SECTION A")

    run.bold = True
    run.font.size = Pt(14)

    sub = doc.add_paragraph("(1 Mark Questions)")

    sub.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    for q in questions[:20]:

        p = doc.add_paragraph()

        run = p.add_run(q)

        run.font.size = Pt(11)

        p.paragraph_format.space_after = Pt(10)

    # ==========================================
    # SECTION B
    # ==========================================

    sec_b = doc.add_paragraph()

    sec_b.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    run = sec_b.add_run("SECTION B")

    run.bold = True
    run.font.size = Pt(14)

    sub = doc.add_paragraph("(2 Mark Questions)")

    sub.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    for q in questions[20:35]:

        p = doc.add_paragraph()

        run = p.add_run(q)

        run.font.size = Pt(11)

        p.paragraph_format.space_after = Pt(10)

    # ==========================================
    # SECTION C
    # ==========================================

    sec_c = doc.add_paragraph()

    sec_c.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    run = sec_c.add_run("SECTION C")

    run.bold = True
    run.font.size = Pt(14)

    sub = doc.add_paragraph("(5 Mark Questions)")

    sub.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    for q in questions[35:50]:

        p = doc.add_paragraph()

        run = p.add_run(q)

        run.font.size = Pt(11)

        p.paragraph_format.space_after = Pt(10)

    # ==========================================
    # FOOTER
    # ==========================================

    footer = section.footer

    para = footer.paragraphs[0]

    para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    run = para.add_run(
        "AI Generated Question Paper"
    )

    run.italic = True
    run.font.size = Pt(9)

    # ==========================================
    # SAVE FILE
    # ==========================================

    doc.save(filename)


# ==========================================
# ROUTES
# ==========================================

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        file = request.files["file"]

        qtype = request.form["type"]

        difficulty = request.form["difficulty"]

        path = os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )

        file.save(path)

        # ==========================================
        # EXTRACT TEXT
        # ==========================================

        text = extract_text(path)

        # ==========================================
        # RAG
        # ==========================================

        vectorizer, vectors, chunks = create_vector_store(text)

        context = retrieve_context(
            f"{qtype} {difficulty}",
            vectorizer,
            vectors,
            chunks
        )

        # ==========================================
        # GENERATE PAPER
        # ==========================================

        questions = generate_paper(
            context,
            qtype,
            difficulty
        )

        # ==========================================
        # SAVE DOCX
        # ==========================================

        output_file = os.path.join(
            GENERATED_FOLDER,
            "question_paper.docx"
        )

        save_docx(
            output_file,
            questions,
            qtype,
            text
        )

        return send_file(
            output_file,
            as_attachment=True
        )

    return render_template("index.html")


# ==========================================
# DOWNLOAD
# ==========================================

@app.route("/download")
def download():

    return send_file(
        os.path.join(
            GENERATED_FOLDER,
            "question_paper.docx"
        ),
        as_attachment=True
    )


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
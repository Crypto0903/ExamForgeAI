# ExamForge AI — Intelligent Question Paper Generator

ExamForge AI is an AI-powered Question Paper Generation System built using Flask, Groq LLM, and Retrieval-Augmented Generation (RAG).

The system automatically analyzes uploaded syllabus documents and generates university-style question papers with proper formatting, section distribution, difficulty control, and DOCX export support.

Designed as an academic automation solution, the project focuses on generating syllabus-specific, non-repetitive, and structured examination papers.

---

# Features

## AI-Based Question Generation
- Generates intelligent syllabus-based questions using Groq LLM
- Supports:
  - MCQ Papers
  - Descriptive Papers
  - One-Liner Questions

---

## Retrieval-Augmented Generation (RAG)
- Extracts syllabus content
- Splits syllabus into semantic chunks
- Retrieves relevant academic context using TF-IDF vectorization
- Generates context-aware questions

---

## Smart Exam Formatting
- University-style question paper layout
- Section-wise formatting:
  - SECTION A
  - SECTION B
  - SECTION C
- Automatic numbering
- Marks distribution
- Instructions section
- Clean document hierarchy

---

## Intelligent Header Detection
- AI automatically detects:
  - Subject Name
  - Programme
  - Exam Title

from uploaded syllabus documents.

---

## Duplicate Prevention System
- Removes repeated questions
- Prevents concept duplication
- Ensures syllabus coverage balance

---

## Modern UI/UX
- Responsive design
- Drag & drop syllabus upload
- Mobile-friendly interface
- Difficulty selection
- Question type selection

---

# Tech Stack

## Backend
- Python
- Flask
- Groq API
- Scikit-learn
- NumPy
- python-docx

---

## Frontend
- HTML5
- CSS3
- JavaScript

---

## AI / NLP
- Retrieval-Augmented Generation (RAG)
- TF-IDF Vectorization
- Large Language Models (LLMs)

---

# System Workflow

```text
Upload Syllabus
       ↓
Extract DOCX Text
       ↓
Chunk Syllabus Content
       ↓
Generate TF-IDF Vector Store
       ↓
Retrieve Relevant Context
       ↓
Generate AI Questions
       ↓
Remove Duplicates
       ↓
Generate University-Style DOCX
```

---

# Project Structure

```text
ExamForge-AI/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env
│
├── templates/
│   └── index.html
│
├── uploads/
│
├── generated/
│
└── static/
    └── screenshots/
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/ExamForge-AI.git
```

---

## Navigate to Project

```bash
cd ExamForge-AI
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_api_key_here
```

---

## Run Application

```bash
python app.py
```

---

# Usage

1. Upload syllabus document (`.docx`)
2. Select question type:
   - MCQ
   - Descriptive
   - One-Liner
3. Select difficulty:
   - Beginner
   - Intermediate
   - Advanced
4. Generate question paper
5. Download formatted DOCX output

---

# Output Capabilities

The system generates:
- Structured examination papers
- Syllabus-specific questions
- Non-repetitive content
- University-style formatting
- Section-based paper layout

---

# Key Functionalities

| Functionality | Description |
|---|---|
| RAG Pipeline | Retrieves syllabus-relevant content |
| AI Generation | Creates syllabus-specific questions |
| Deduplication | Prevents repeated questions |
| DOCX Export | Generates formatted exam papers |
| Dynamic Header Detection | AI-generated paper heading |
| Responsive UI | Works across devices |

---

# Screenshots

Add screenshots inside:

```text
static/screenshots/
```

Recommended screenshots:
- Home Interface
- Upload Section
- Generated Question Paper
- DOCX Output
- Mobile UI

---

# Future Enhancements

- PDF Export
- Database Integration
- User Authentication
- Admin Dashboard
- Chapter-wise Weightage
- Bloom’s Taxonomy Integration
- Cloud Deployment
- Multi-University Templates
- AI Difficulty Calibration

---

# Academic Relevance

This project demonstrates:
- Applied Artificial Intelligence
- Natural Language Processing
- Retrieval-Augmented Generation
- Backend Development
- Document Automation
- Prompt Engineering
- Full Stack Development

---

# Author

Vignesh Valvaikar

---

# License

This project is developed for academic and educational purposes.
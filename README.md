# Smart Document Processing Bot

An end-to-end automation solution that combines UiPath with AI to extract, summarize, and process scanned documents. Designed for business workflows that require intelligent document understanding and structured output.

---

## Features

- Reads scanned PDFs from a designated folder
- Extracts text using OCR (Tesseract or UiPath Document OCR)
- Sends extracted text to a Python-based AI API
- Performs summarization and key field extraction (e.g., name, date, amount)
- Saves structured data to Excel
- Sends a summary report via email

---

## Architecture

![Architecture Diagram](architecture-diagram.png)

This project integrates UiPath with a custom FastAPI backend to process documents intelligently. UiPath handles orchestration, file handling, and notifications. FastAPI handles NLP and data extraction.

---

## Tech Stack

- **UiPath Studio** (with REFramework)
- **Python 3.10+** (FastAPI)
- **OCR:** Tesseract / UiPath Document OCR
- **Excel Automation**
- **SMTP Email**
- **GitHub for version control**

---

## Setup & Run Instructions

### 1. Start the AI API

```bash
cd ai_api
pip install -r requirements.txt
uvicorn main:app --reload

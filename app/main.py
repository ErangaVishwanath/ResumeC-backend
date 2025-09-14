from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import JSONResponse
import pdfplumber
import re
import requests
import tempfile
import pandas as pd
from pydantic import BaseModel
import random
from difflib import SequenceMatcher
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
from app.skills import skills_list
import spacy

app = FastAPI(title="Resume Verifier API", version="1.0.0")

# Load the custom NER model
ner_model = spacy.load("./skill_ner_model")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Replace with your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using pdfplumber."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    return text.lower()

def extract_from_dict(skills_dict: list, text: str):
    """Find skills in resume text based on dictionary matching."""
    found = set()
    for skill in skills_dict:
        if re.search(rf"\b{re.escape(skill)}\b", text):
            found.add(skill)
    return found

QUESTION_BANK_PATH = "app/QuestionBank.csv"
question_bank = pd.read_csv(QUESTION_BANK_PATH)

class CandidateTech(BaseModel):
    technologies: list[str]
    difficulty: str = "medium"  # easy | medium | hard

class CandidateAnswer(BaseModel):
    question_text: str
    answer: str

@app.post("/verify_resume/")
async def verify_resume(
    file: UploadFile = File(...),
    github_username: str = Form(...)
):
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Extract text and skills from resume
        text = extract_text_from_pdf(tmp_path)

        if not text.strip():
            # If pdfplumber fails, use spaCy NER model to extract text and skills
            with pdfplumber.open(tmp_path) as pdf:
                all_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        all_text += page_text + " "
            doc = ner_model(all_text)
            resume_skills = set(ent.text for ent in doc.ents if ent.label_ == "SKILL")
        else:
            resume_skills = extract_from_dict(skills_list, text)

        # Fetch GitHub repositories
        api_url = f"https://api.github.com/users/{github_username}/repos"
        response = requests.get(api_url)

        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="GitHub user not found")

        repositories = response.json()

        # Check languages for each repo
        repository_languages = {}
        for repo in repositories:
            languages_url = repo['languages_url']
            languages_response = requests.get(languages_url)
            if languages_response.status_code == 200:
                languages_data = languages_response.json()
                repository_languages[repo['name']] = list(languages_data.keys())

        # Match resume skills with GitHub languages
        matching_skills = set()
        for skill in resume_skills:
            for repo_languages in repository_languages.values():
                if skill.lower() in [lang.lower() for lang in repo_languages]:
                    matching_skills.add(skill)
                    break
        
        score = (len(matching_skills) / len(resume_skills) * 100) if resume_skills else 0

        return JSONResponse(content={
            "filename": file.filename,
            "resume_skills": list(resume_skills),
            "github_username": github_username,
            "matching_skills": list(matching_skills),
            "repositories_checked": len(repositories),
            "score": round(score, 2)
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-questions")
def get_questions(candidate: CandidateTech):
    # Filter by technology
    filtered = question_bank[question_bank["technology"].isin(candidate.technologies)]

    if candidate.difficulty == "easy":
        filtered = filtered[filtered["complexity_score"] <= 3]
    elif candidate.difficulty == "hard":
        filtered = filtered[filtered["complexity_score"] >= 7]
    else:
        filtered = filtered[(filtered["complexity_score"] > 3) & (filtered["complexity_score"] < 7)]

    if filtered.empty:
        raise HTTPException(status_code=404, detail="No questions found for given tech stack")

    # Pick 2 random questions
    selected = filtered.sample(n=min(2, len(filtered))).to_dict(orient="records")
    return {"questions": selected}

# --- API Endpoint: Check Answer ---
@app.post("/check-answer")
def check_answer(candidate_answer: CandidateAnswer):
    # Lookup expected answer
    row = question_bank[question_bank["question_text"] == candidate_answer.question_text]

    if row.empty:
        raise HTTPException(status_code=404, detail="Question not found in bank")

    expected_answer = row.iloc[0]["expected_answer"]

    # Compare using similarity ratio
    similarity = SequenceMatcher(None, candidate_answer.answer.lower(), expected_answer.lower()).ratio()

    return {
        "expected_answer": expected_answer,
        "candidate_answer": candidate_answer.answer,
        "similarity_score": round(similarity, 2),
        "result": "pass" if similarity > 0.7 else "fail"
    }
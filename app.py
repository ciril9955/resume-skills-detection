import os
import re
import spacy
from PyPDF2 import PdfReader
from docx import Document
import logging
import streamlit as st

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to extract skills from text using regular expressions
def extract_skills(text, predefined_skills):
    extracted_skills = []
    skill_pattern = r'\b(?:' + '|'.join(re.escape(skill) for skill in predefined_skills) + r')\b'
    matches = re.findall(skill_pattern, text, flags=re.IGNORECASE)
    for match in matches:
        extracted_skills.append(match.title())
    return list(set(extracted_skills))

# Function to parse PDF file
def parse_pdf(pdf_path, predefined_skills):
    skills = []
    try:
        pdf_reader = PdfReader(pdf_path)
        for page in pdf_reader.pages:
            text = page.extract_text()
            skills += extract_skills(text, predefined_skills)
    except Exception as e:
        logger.error(f"Error parsing PDF '{pdf_path}': {str(e)}")
    return skills

# Function to parse Word document
def parse_word_doc(docx_path, predefined_skills):
    skills = []
    try:
        doc = Document(docx_path)
        for paragraph in doc.paragraphs:
            text = paragraph.text
            skills += extract_skills(text, predefined_skills)
    except Exception as e:
        logger.error(f"Error parsing Word document '{docx_path}': {str(e)}")
    return skills

# Function to parse a single resume
def parse_resume(resume_path, predefined_skills):
    _, file_extension = os.path.splitext(resume_path)
    if file_extension.lower() == ".pdf":
        skills = parse_pdf(resume_path, predefined_skills)
    elif file_extension.lower() == ".docx":
        skills = parse_word_doc(resume_path, predefined_skills)
    else:
        logger.error(f"Unsupported file format for '{resume_path}'")
        raise ValueError("Unsupported file format")
    return skills

# Function to process all resumes in a folder
def process_resumes_in_folder(folder_path, predefined_skills):
    matching_skills_all_resumes = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith((".pdf", ".docx")):
                resume_path = os.path.join(root, file)
                matching_skills = parse_resume(resume_path, predefined_skills)
                matching_skills_all_resumes[resume_path] = matching_skills
    return matching_skills_all_resumes

# Streamlit UI
st.title("Resume Skill Matcher")

# User input for predefined skills
user_input_skills = st.text_input("Enter predefined skills (comma-separated):")
predefined_skills = [skill.strip() for skill in user_input_skills.split(',')]

# Upload resumes
uploaded_files = st.file_uploader("Upload resumes (PDF or DOCX files)", accept_multiple_files=True)

# Check button
if st.button("Check Skills"):
    if not predefined_skills:
        st.warning("Please enter predefined skills.")
    elif not uploaded_files:
        st.warning("Please upload resumes.")
    else:
        # Create a temporary directory to store uploaded files
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)

        # Save uploaded files to the temporary directory
        resume_paths = []
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            resume_paths.append(file_path)

        # Process uploaded resumes
        matching_skills_all_resumes = process_resumes_in_folder(temp_dir, predefined_skills)

        # Display matching skills and percentage for each resume
        for resume_path, matching_skills in matching_skills_all_resumes.items():
            num_predefined_skills = len(predefined_skills)
            num_matching_skills = len(matching_skills)
            percentage = (num_matching_skills / num_predefined_skills) * 100 if num_predefined_skills > 0 else 0
            
            st.info(f"Number of Predefined Skills: {num_predefined_skills}")
            st.info(f"Number of Matching Skills: {num_matching_skills}")
            st.info(f"Matching Skills: {matching_skills}")
            st.info(f"Percentage of Matching Skills: {percentage:.2f}%")

        # Clean up temporary files
        for resume_path in resume_paths:
            os.remove(resume_path)
        os.rmdir(temp_dir)

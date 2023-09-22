import os
import re
import spacy
from PyPDF2 import PdfReader
from docx import Document
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Define predefined skills
predefined_skills = ["Python", "Java", "Machine Learning", "Data Analysis", "Power BI", "Sales", "Marketing"]

# Function to extract skills from text using regular expressions
def extract_skills(text):
    extracted_skills = []
    skill_pattern = r'\b(?:' + '|'.join(re.escape(skill) for skill in predefined_skills) + r')\b'
    matches = re.findall(skill_pattern, text, flags=re.IGNORECASE)
    for match in matches:
        extracted_skills.append(match.title())
    return list(set(extracted_skills))

# Function to parse PDF file
def parse_pdf(pdf_path):
    skills = []
    try:
        pdf_reader = PdfReader(pdf_path)
        for page in pdf_reader.pages:
            text = page.extract_text()
            skills += extract_skills(text)
    except Exception as e:
        logger.error(f"Error parsing PDF '{pdf_path}': {str(e)}")
    return skills

# Function to parse Word document
def parse_word_doc(docx_path):
    skills = []
    try:
        doc = Document(docx_path)
        for paragraph in doc.paragraphs:
            text = paragraph.text
            skills += extract_skills(text)
    except Exception as e:
        logger.error(f"Error parsing Word document '{docx_path}': {str(e)}")
    return skills

# Function to parse a single resume
def parse_resume(resume_path):
    _, file_extension = os.path.splitext(resume_path)
    if file_extension.lower() == ".pdf":
        skills = parse_pdf(resume_path)
    elif file_extension.lower() == ".docx":
        skills = parse_word_doc(resume_path)
    else:
        logger.error(f"Unsupported file format for '{resume_path}'")
        raise ValueError("Unsupported file format")
    return skills

# Function to process all resumes in a folder
def process_resumes_in_folder(folder_path):
    matching_skills_all_resumes = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith((".pdf", ".docx")):
                resume_path = os.path.join(root, file)
                matching_skills = parse_resume(resume_path)
                matching_skills_all_resumes[resume_path] = matching_skills
    return matching_skills_all_resumes

# Resume folder path
folder_path = "C:/Users/ciril/OneDrive/Desktop/resume detection/resumes"
matching_skills_all_resumes = process_resumes_in_folder(folder_path)

# Print matching skills for each resume along with the number of predefined and matching skills
for resume_path, matching_skills in matching_skills_all_resumes.items():
    num_predefined_skills = len(predefined_skills)
    num_matching_skills = len(matching_skills)
    logger.info(f"Resume: {resume_path}")
    logger.info(f"Number of Predefined Skills: {num_predefined_skills}")
    logger.info(f"Number of Matching Skills: {num_matching_skills}")
    logger.info(f"Matching Skills: {matching_skills}")

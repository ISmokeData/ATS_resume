import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

load_dotenv()  # Load all our environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_prompt)
    return response.text

def input_pdf_text(uploaded_file):
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page in range(len(reader.pages)):
            page = reader.pages[page]
            text += str(page.extract_text())
        return text
    except Exception as e:
        return None, str(e)

# Prompt Template
input_prompt_template = """
Hey Act Like a skilled or very experienced ATS(Application Tracking System)
with a deep understanding of tech field, software engineering, data science, data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving the resumes. Assign the percentage matching based 
on JD and the missing keywords with high accuracy.

resume: {text}
description: {jd}

I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
"""

# Streamlit app
st.title("Smart ATS")
st.text("Improve Your Resume for ATS")

jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload a PDF file")

if st.button("Submit"):
    if uploaded_file is not None and jd:
        with st.spinner("Processing..."):
            text, error = input_pdf_text(uploaded_file)
            if text:
                input_prompt = input_prompt_template.format(text=text, jd=jd)
                response = get_gemini_response(input_prompt)
                try:
                    response_json = json.loads(response)
                    st.subheader("Job Description Match Percentage")
                    st.text(response_json.get("JD Match", "N/A"))
                    st.subheader("Missing Keywords")
                    st.text(", ".join(response_json.get("MissingKeywords", [])))
                    st.subheader("Profile Summary")
                    st.text(response_json.get("Profile Summary", "N/A"))
                except json.JSONDecodeError:
                    st.error("Failed to decode response from the AI model.")
            else:
                st.error(f"Error reading PDF file: {error}")
    else:
        st.error("Please upload a PDF file and provide a job description.")



'''Features Added:
Error Handling: Added error handling for PDF reading.
Response Parsing: Improved parsing and display of JSON response.
User Feedback: Added spinners and error messages for better user experience.
Validation: Added validation to ensure both JD and PDF are provided.'''

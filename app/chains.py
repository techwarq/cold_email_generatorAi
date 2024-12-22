import os
import streamlit as st

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv
import json

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=st.secrets["GROQ_API_KEY"], model_name="llama-3.1-70b-versatile")
    
    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job posting and return it in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            If the job title is not explicitly mentioned in the skills or description, include it in the `role` field.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]
    
    def write_mail(self, job, portfolio_items):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DETAILS:
            {job_details}
            
            ### YOUR SKILLS AND PROJECTS:
            {portfolio_items}
            
            ### INSTRUCTION:
            You are Sonali, an aspiring software engineer writing a cold email to apply for the job role mentioned above. Your task is to write a compelling 200-word cold email that showcases your skills and experiences, focusing on the following:

            1. Create a concise subject line for the email using the job role.
            2. Introduce yourself briefly as an aspiring software engineer. Keep the email tone like a student wrote it; don't make it too perfect.
            3. Express your enthusiasm for the specific role, mentioning the role title explicitly.
            4. List your own skills from the portfolio/resume that align with the role in bulleted points.
            5. State that while you may not have all the skills listed in the job description, you are eager and committed to learning them if required.
            6. Provide a very brief summary of 1-2 of your most relevant projects, emphasizing how they align with your existing skills.
            7. Conclude with a statement about your eagerness to contribute to the company and grow in your field.
            8. Close with a call to action, such as requesting an interview or further discussion.

            Ensure that you do not include skills from the job description that are not listed in the portfolio. Instead, mention your willingness to learn.

            ### EMAIL (INCLUDING SUBJECT LINE):
            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_details": json.dumps(job), "portfolio_items": json.dumps(portfolio_items)})
        return res.content

    def write_linkedin_message(self, job, portfolio_items):
        prompt_linkedin = PromptTemplate.from_template(
            """
            ### JOB DETAILS:
            {job_details}
            
            ### YOUR SKILLS AND PROJECTS:
            {portfolio_items}
            
            ### INSTRUCTION:
            Write a brief LinkedIn message to apply for the job role.
            - Use an approachable and professional tone.
            - Keep the message under 100 words.
            - Mention the role and highlight 2 key skills or experiences.
            - End with a call to action for a follow-up or further discussion.
            ### MESSAGE:
            """
        )
        chain_linkedin = prompt_linkedin | self.llm
        res = chain_linkedin.invoke({"job_details": json.dumps(job), "portfolio_items": json.dumps(portfolio_items)})
        return res.content
    
    def extract_skills_and_projects(self, pdf_text):
        prompt = PromptTemplate.from_template(
            """
            ### PDF TEXT:
            {pdf_text}
            ### INSTRUCTION:
            Carefully analyze the provided PDF text, which is extracted from a resume. Your task is to extract all skills and projects mentioned in the text.

            For skills:
            - Include both technical skills (programming languages, frameworks, tools) and soft skills.
            - List each skill separately.

            For projects:
            - Extract any mentioned projects or significant work experiences.
            - Include a brief description for each project if available.

            Return the extracted information in JSON format with the keys: `skills` (an array of strings) and `projects` (an array of strings, each containing a project name and brief description).

            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt | self.llm
        res = chain_extract.invoke(input={"pdf_text": pdf_text})
        
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse skills and projects.")
        
        return res

if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))

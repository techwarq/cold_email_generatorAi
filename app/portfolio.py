import chromadb
import uuid
from PyPDF2 import PdfReader
from io import BytesIO
from chains import Chain

class Portfolio:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path='./chromadb')
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")
        self.chains = Chain()

    def load_portfolio_from_pdf(self, pdf_file):
        extracted_text = self.extract_text_from_pdf(pdf_file)
        extracted_data = self.chains.extract_skills_and_projects(extracted_text)
        print("Extracted Data:", extracted_data)  

        skills = extracted_data.get("skills", [])
        projects = extracted_data.get("projects", [])

        
        self.collection.delete(where={'type': 'skill'})
        self.collection.delete(where={'type': 'project'})

       
        for skill in skills:
            if isinstance(skill, str):
                self.collection.add(
                    documents=[skill],
                    metadatas=[{"type": "skill"}],
                    ids=[f"skill_{str(uuid.uuid4())}"]
                )

        
        for project in projects:
            if isinstance(project, dict) and "name" in project and "description" in project:
                project_data = f"Project Name: {project['name']}\nDescription: {project['description']}"
                self.collection.add(
                     documents=[project_data],
                     metadatas=[{"type": "project"}],
                     ids=[f"project_{str(uuid.uuid4())}"]
        )

       
        self.print_portfolio_items()

        

    def extract_text_from_pdf(self, pdf_file):
        
        pdf_bytes = BytesIO(pdf_file.read())
        
        reader = PdfReader(pdf_bytes)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    def get_portfolio_items(self):
        
        skills = []
        projects = []

        
        skill_results = self.collection.query(query_texts=[""], n_results=5, where={"type": "skill"})
        for document in skill_results['documents'][0]:
            skills.append(document)

        
        project_results = self.collection.query(query_texts=[""], n_results=10, where={"type": "project"})
        for document in project_results['documents'][0]:
            projects.append(document)

        return {"skills": skills, "projects": projects}

    def print_portfolio_items(self):
        """Prints the contents of the portfolio to the console for debugging."""
        items = self.get_portfolio_items()
        print("Current Skills in DB:")
        for skill in items['skills']:
            print(f"• {skill}")
        
        print("\nCurrent Projects in DB:")
        for project in items['projects']:
            print(f"• {project}")

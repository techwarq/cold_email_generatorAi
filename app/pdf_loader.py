# pdf_loader.py

from langchain.document_loaders import PyMuPDFLoader
from io import BytesIO

class PDFLoader:
    def __init__(self, pdf_file):
        self.pdf_file = pdf_file

    def load_data(self):
        # Use PyMuPDFLoader to read the PDF from BytesIO
        loader = PyMuPDFLoader(BytesIO(self.pdf_file.read()))  # Use BytesIO to read the uploaded file
        documents = loader.load()
        return [doc.page_content for doc in documents]  # Return extracted text

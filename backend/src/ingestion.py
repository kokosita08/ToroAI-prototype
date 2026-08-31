# This file processes PDF documents for ToroAI's RAG knowledge base.
# Workflow of the file is as follows : PDF -> extract text -> clean -> chunk -> embed -> prepare for Pinecone

from pathlib import Path 
from pypdf import PdfReader
from langchain_core.documents import Document 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# to get chunk size and overlap from config.py 
from backend.config import Config 
# custom logger
from backend.src.logger import get_logger 

# log for this file 
logger = get_logger(__name__)


# official CSUDH source pages for the downloaded PDFs
PDF_SOURCE_URLS = {

    "cpt_information_2022.pdf":
        "https://www.csudh.edu/international/intl-student-info/current-students/employment/",

    "cpt_application.pdf":
        "https://www.csudh.edu/international/intl-student-info/current-students/employment/",

    "opt_request_form.pdf":
        "https://www.csudh.edu/international/intl-student-info/current-students/employment/",

    "opt_employment_update.pdf":
        "https://www.csudh.edu/international/intl-student-info/current-students/employment/",

    "ssn_information_2025.pdf":
        "https://www.csudh.edu/international/intl-student-info/current-students/employment/",

    "reduced_course_load.pdf":
        "https://www.csudh.edu/international/intl-student-info/current-students/immigration/",

    "concurrent_enrollment.pdf":
        "https://www.csudh.edu/international/intl-student-info/current-students/immigration/",

    "f1_student_regulations.pdf":
        "https://www.csudh.edu/international/intl-student-info/current-students/immigration/",

    "i20_program_extension.pdf":
        "https://www.csudh.edu/international/intl-student-info/current-students/forms-documents/",

    "sevis_transfer_request.pdf":
        "https://www.csudh.edu/international/intl-student-info/current-students/forms-documents/",

    "i20_change_major.pdf":
        "https://www.csudh.edu/international/intl-student-info/current-students/forms-documents/",

    "departure_form.pdf":
        "https://www.csudh.edu/international/intl-student-info/current-students/forms-documents/"
}


# LOAD 
def load_pdf(pdf_path):
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found : {pdf_path}")
    
    logger.info(f"Loading pdf: {path.name}")

    reader = PdfReader(str(path))
    documents = []
    total_pages = len(reader.pages)
    page_number = 1 

    source_url = PDF_SOURCE_URLS.get(path.name)


    for page in reader.pages:
        text = page.extract_text()
        if text is None:
            text= ""
        text = text.strip()

        if len(text)>=50:
            metadata = {"source": path.name,"page": page_number, "total_pages": total_pages}

            # add the official webpage link if we have one
            if source_url is not None:
                metadata["source_url"] = source_url


            document = Document(page_content = text, metadata = metadata)
            documents.append(document)
        page_number = page_number+1     

    logger.info(f"Loaded {len(documents)} pages from {path.name}")
    return documents

# CLEAN 

def clean_documents(documents):

    cleaned_documents= []
    
    for document in documents:
        text = document.page_content
        words = text.split()
        cleaned_text = " ".join(words)

        if len(cleaned_text)>=50:
            cleaned_document = Document(page_content=cleaned_text,metadata= document.metadata)
            cleaned_documents.append(cleaned_document)
    
    logger.info(f"Cleaned {len(cleaned_documents)} documents")
    return cleaned_documents 

# CHUNK 

def chunk_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = Config.CHUNK_SIZE,chunk_overlap = Config.CHUNK_OVERLAP, separators = ["\n\n","\n",". "," ",""],length_function = len)

    chunks = text_splitter.split_documents(documents)
    chunk_number = 1

    for chunk in chunks :
        chunk.metadata["chunk_id"] = chunk_number
        chunk.metadata["char_count"] = len(chunk.page_content)

        chunk_number = chunk_number +1 
    
    logger.info(f"Created {len(chunks)} chunks ")

    return chunks

# EMBED 

def embed_chunks(chunks):
    logger.info(f"Creating embeddings for {len(chunks)} chunks")

    embedding_model = OpenAIEmbeddings(model = Config.OPENAI_EMBEDDING_MODEL,api_key = Config.OPENAI_API_KEY)
    texts = []

    for chunk in chunks:
        texts.append(chunk.page_content)

    vectors = embedding_model.embed_documents(texts)
    logger.info(f"Created {len(vectors)} embeddings")

    return vectors




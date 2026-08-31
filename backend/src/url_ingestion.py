# This file loads official webpages and extracts useful text for ToroAI's RAG knowledge base.
# Workflow of this file is as follows : URL -> fetch webpage -> extract main text -> create Document

import requests 
from trafilatura import extract

from langchain_core.documents import Document 
from backend.src.logger import get_logger

logger = get_logger(__name__)

# Load webpage 

def load_webpage(url):
    response = requests.get(url)
    if response.status_code != 200 :
        raise Exception(f"Could not load webpage :{url}")

    # extract the main useful text from the webpage
    text = extract(response.text,include_comments=False)
    
    if text is None:
        raise Exception(f"Could not extract webpage text: {url}")


    document = Document(page_content= text, metadata = {"source" : url , "source_type": "webpage"})

    logger.info(f"Loaded webpage: {url}")

    return document 



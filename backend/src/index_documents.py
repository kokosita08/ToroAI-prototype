# This file indexes all downloaded CSUDH PDF documents into Pinecone.
# Workflow of this file is as follows : PDFs -> load -> clean -> chunk -> embed -> store vectors in Pinecone

from pathlib import Path 
from backend.src.ingestion import load_pdf
from backend.src.ingestion import clean_documents
from backend.src.ingestion import chunk_documents
from backend.src.ingestion import embed_chunks

from backend.src.vector_store import get_pinecone_index
from backend.src.vector_store import store_vectors

# Folders where all csudh pdfs are stored 
pdf_folder = Path ("backend/data/csudh")

# connect to Pinecone
index = get_pinecone_index()


# count no.of pdfs  processed 
pdf_count = 0

# count no.of vectors stored
vector_count = 0 

# Go through every file in the folder 

for file in pdf_folder.iterdir():

    # only process pdf files
    if file.suffix.lower() ==".pdf":

        print(f"\nProcessing: {file.name}")

        documents = load_pdf(file)                                  # LOAD 
        cleaned_documents = clean_documents(documents)              # CLEAN 
        chunks = chunk_documents(cleaned_documents)                 # CHUNK
        vectors = embed_chunks(chunks)                              # EMBED 

        store_vectors(index,chunks,vectors)                         # store in pinecone 

        # update counters 

        pdf_count += 1
        vector_count += len(vectors)

print("\nDONE")
print("PDF processed:  ", pdf_count) 
print("Vector stored : ", vector_count)


# This file takes a user question and retrieves the most relevant chunks from Pinecone.
# Workflow of the file : user question -> embed question -> search Pinecone -> return best matching chunks

from langchain_openai import OpenAIEmbeddings
from backend.config import Config 
from backend.src.vector_store import get_pinecone_index
from backend.src.vector_store import search_pinecone 

# retrieve 
def retrieve_chunks(question):
    # connect to the same embedding model used for our stored chunks
    embedding_model = OpenAIEmbeddings(model = Config.OPENAI_EMBEDDING_MODEL, api_key = Config.OPENAI_API_KEY)
    # user's question into vector 
    question_vector = embedding_model.embed_query(question)

    #Connect to Pinecone 
    index = get_pinecone_index()

    # searching most relevant chunks 
    results= search_pinecone(index, question_vector)

    # minimum score for a relevant chunk
    SIMILARITY_THRESHOLD = 0.50

    filtered_matches = []

    for match in results["matches"]:
        if match["score"] >= SIMILARITY_THRESHOLD:
            filtered_matches.append(match)

    results["matches"] = filtered_matches

    return results
    

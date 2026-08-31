# This file manages ToroAI's Pinecone vector database.
# Workflow of this file is as follows : connect to Pinecone -> store chunk vectors + metadata -> search relevant vectors

from pinecone import Pinecone, ServerlessSpec
from backend.config import Config
from backend.src.logger import get_logger


logger = get_logger(__name__)

# PINECONE

def get_pinecone_index():
    # connect to pinecone 
    pinecone = Pinecone(api_key= Config.PINECONE_API_KEY)
    # if index exists?
    index_names = pinecone.list_indexes().names()

    if Config.PINECONE_INDEX_NAME not in index_names:
        logger.info("Creating pinecone index")
        pinecone.create_index(name =Config.PINECONE_INDEX_NAME ,dimension= Config.EMBEDDING_DIMENSION,metric="cosine",spec = ServerlessSpec(cloud ="aws",region = "us-east-1"))
    
    # connect to our index 

    index = pinecone.Index(Config.PINECONE_INDEX_NAME)
    logger.info("connected to Pinecone")
    return index
 
# STORE VECTORS

def store_vectors(index, chunks, vectors):
    records = []
    
    for i in range(len(chunks)):
        chunk = chunks[i]
        vector = vectors[i]
        record_id = f"{chunk.metadata['source']}-{chunk.metadata['chunk_id']}"

        # basic metadata used for every source
        metadata = { "source": chunk.metadata["source"], "chunk_id": chunk.metadata["chunk_id"],"char_count": chunk.metadata["char_count"],"text": chunk.page_content }

        # add PDF metadata if it exists
        if "page" in chunk.metadata:
            metadata["page"] = chunk.metadata["page"]

        if "total_pages" in chunk.metadata:
            metadata["total_pages"] = chunk.metadata["total_pages"]

        # add webpage metadata if it exists
        if "source_type" in chunk.metadata:
            metadata["source_type"] = chunk.metadata["source_type"]
        
        # add clickable source link if it exists
        if "source_url" in chunk.metadata:
            metadata["source_url"] = chunk.metadata["source_url"]

        # create one Pinecone record
        record = {"id": record_id, "values": vector,"metadata": metadata}
        records.append(record)

    index.upsert(vectors=records)                       # store all records in Pinecone
    logger.info(f"Stored {len(records)} vectors in Pinecone")


# SEARCH
def search_pinecone(index, question_vector):

    results = index.query(
        vector=question_vector,
        top_k=5,
        include_metadata=True
    )

    return results



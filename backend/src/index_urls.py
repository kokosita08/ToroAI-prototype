# This file processes all selected official urls and stores their information in Pinecone
# Workflow of the file is as follows : URL -> load webpage -> clean -> chunk -> embed -> store in Pinecone

from backend.src.url_ingestion import load_webpage

from backend.src.ingestion import clean_documents
from backend.src.ingestion import chunk_documents
from backend.src.ingestion import embed_chunks

from backend.src.vector_store import get_pinecone_index
from backend.src.vector_store import store_vectors

# official webpages toroai will use  

urls = ["https://www.csudh.edu/international/intl-student-info/current-students/immigration/",
    "https://www.csudh.edu/international/intl-student-info/current-students/employment/",
    "https://www.csudh.edu/international/intl-student-info/current-students/travel/",
    "https://www.uscis.gov/working-in-the-united-states/students-and-exchange-visitors/students-and-employment",
    "https://www.uscis.gov/working-in-the-united-states/students-and-exchange-visitors/optional-practical-training-opt-for-f-1-students",
    "https://www.uscis.gov/working-in-the-united-states/students-and-exchange-visitors/optional-practical-training-extension-for-stem-students-stem-opt",
    "https://www.uscis.gov/policy-manual/volume-2-part-f-chapter-5",
    "https://www.uscis.gov/policy-manual/volume-2-part-f-chapter-6"
    ]

# Connect to the Pinecone index 

index = get_pinecone_index()

# to count the no.of urls processed

url_count = 0

# to count no.of vectors stored 

vector_count = 0 

# go through every url 

for url in urls:
    print(f"\nProcessing: {url}")

    #load 
    document = load_webpage(url)     # load the webpage and turn it into a document 
    documents = [document]            # clean_documents expects a list of documents 

    #clean
    cleaned_documents = clean_documents(documents)    # clean the webpage text 

    #chunk
    chunks = chunk_documents(cleaned_documents)    # cleaned web text into smaller chunks 

    #embed 
    vectors = embed_chunks(chunks)                 # turn every chunk into a vector 

    #store 
    store_vectors(index,chunks,vectors)           # store vectors and their metadata into PINECONE 

    # update counters
    url_count += 1
    vector_count += len(vectors)


print("\nDONE")
print("URLs processed:", url_count)
print("Vectors stored:", vector_count)





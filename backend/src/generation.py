# This file takes the user's question + the retrieved Pinecone chunks and asks the LLM to create the final ToroAI answer.
# Workflow of the file : question -> retrieve chunks -> build context -> send to LLM -> return final answer

from langchain_openai import ChatOpenAI 
from backend.config import Config
from backend.src.retrieval import retrieve_chunks

# Generate answer

def generate_answer(question):

    # retrieves the most relevant chunk from pinecone 
    results= retrieve_chunks(question)
    # if Pinecone did not find any strong matching chunks, do not ask the LLM to answer from its own knowledge
    if len(results["matches"]) == 0:
        return {
             "answer": "This question is outside ToroAI's current knowledge scope, or there is not enough information in the indexed sources to answer it reliably.",
             "sources": []
        }

    # useful retrieved text 
    context = ""

    # store the source used for this answer 
    sources = []

    # go through every retrieved match 
    for match in results["matches"]:

        source = match["metadata"]["source"]
        text = match["metadata"]["text"]

        # use clickable URL if available
        if "source_url" in match["metadata"]:
            source_link = match["metadata"]["source_url"]
        else:
            source_link = source

        # add the source only once
        if source_link not in sources:
            sources.append(source_link)

        # adding source and text to its context 
        context += f"\nSOURCE: {source}\n"
        context += f"TEXT: {text}\n"

    # Instruction for the llm

    prompt = f""" You are ToroAI, a student-built assistant for CSUDH F-1 students.
    Answer the user's question using only the retrieved sources provided below.
    GROUNDING RULES:
    - Do not use outside knowledge or general model knowledge.
    - Do not make up or infer missing facts.
    - Clearly distinguish federal immigration rules from CSUDH procedures when possible.
    - If the retrieved sources are unclear, incomplete, conflicting, or insufficient, explicitly say so.
    - Do not answer out-of-scope questions using general knowledge.
    - Do not write a Sources section inside the answer because the application displays source links separately.
    
    INDIVIDUAL CASE AND UNCERTAINTY RULES:
    - Never state a possible explanation as the confirmed reason for a student's individual immigration decision.
    - If the sources do not state why a CPT request was denied, cancelled, paused, or changed, say that the reason cannot be determined from the available sources.
    - You may explain possible relevant rules, but clearly label them as possibilities.
    - Never determine that a specific student is currently "in status" or "out of status" unless the retrieved sources directly establish that individual status.
    - Explain whether an action may violate an F-1 rule, but distinguish that from determining the student's current SEVIS or immigration status.
    - For unpaid internships, volunteering, remote work, offsite work, client-site work, or other fact-specific employment arrangements, do not give a broad yes/no unless the retrieved sources clearly support it.
    - For uncertain immigration situations, recommend confirming with CSUDH International Student Services before taking action.
    
    CLARITY AND SCOPE RULES:
    - If the user's question contains an unclear reference such as "this", "that", or "it" and the intended action cannot be determined, ask the user to clarify instead of assuming.
    - Avoid repeating the same rule in different words.
    - Keep the full answer concise.
    
    FORMATTING RULES:
    - Use Markdown formatting.
    - Start with one short, direct answer in one sentence.
    - Then give the rest mainly as a flat bullet list.
    - Use only simple "- " bullet points.
    - Do not use nested bullet points unless absolutely necessary.
    - Use no more than 5 bullet points unless the question truly requires more detail.
    - Keep each bullet to 1-2 short sentences.
    - Do not insert blank lines between bullet points.
    - Keep each bullet concise and easy to scan.
    - Bold only important rules, deadlines, statuses, warnings, and key terms using **bold text**.
    - Do not overuse bold formatting.
    
    USER QUESTION:
    {question}
    RETRIEVED SOURCES:
    {context}
    
    """


    # connect to the openai llm

    llm = ChatOpenAI(model = Config.OPENAI_LLM_MODEL, api_key = Config.OPENAI_API_KEY, max_tokens=500)

    #send the prompt to llm

    response = llm.invoke(prompt)

    # return the final written answer and source links 
    return { "answer": response.content, "sources": sources}


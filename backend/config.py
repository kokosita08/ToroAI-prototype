# This file loads ToroAI's environment variables and shared configuration settings.
# Workflow of this file is as follows : .env -> load settings -> make configuration available to backend files

import os
from dotenv import load_dotenv
from pathlib import Path

# find the backend folder 

backend_folder = Path(__file__).resolve().parent

# find .env file inside the backend folder 
env_file = backend_folder / ".env"

# load the variables from the .env files
load_dotenv(env_file )

class Config:
    # API keys and pinecone settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

    # openAI models
    OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")

    # RAG settings
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

    # flask settings
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "8080"))

    # logging setting
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # supabase settings
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

    # authentication settings
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_EXPIRY_HOURS = os.getenv("JWT_EXPIRY_HOURS")

# settings used by logger.py   
LOG_LEVEL = Config.LOG_LEVEL
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)



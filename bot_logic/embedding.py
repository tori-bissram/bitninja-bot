import os
import openai
from dotenv import load_dotenv

load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_embedding(text):
    """Generate embeddings using OpenAI"""
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

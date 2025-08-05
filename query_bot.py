import os
import json
import faiss
import numpy as np
import openai
from embedding import get_embedding
from dotenv import load_dotenv

load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load index + metadata
# Load or build index + metadata
if not os.path.exists("bitninja_index.faiss"):
    print("bitninja_index.faiss not found. Rebuilding index...")
    from build_index import main as build_index_main
    build_index_main()

try:
    index = faiss.read_index("bitninja_index.faiss")
    with open("bitninja_metadata.json", "r") as f:
        metadata = json.load(f)
    print("Vector store loaded successfully!")
except Exception as e:
    print(f"Error loading FAISS index or metadata: {str(e)}")
    index = None
    metadata = []


def search_docs(query, k=3):
    """Search for relevant documents using OpenAI embeddings"""
    if index is None:
        return []
    
    query_embedding = get_embedding(query)
    query_vec = np.array([query_embedding]).astype('float32')
    D, I = index.search(query_vec, k)
    return [metadata[i] for i in I[0] if i != -1 and i < len(metadata)]

def generate_response(context, question):
    """Generate clean, formatted response using OpenAI GPT"""
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": f"""You are BITNinja, a helpful IT support bot. Use the context below to answer the user's question.

Context:
{context}

IMPORTANT FORMATTING RULES:
- Keep responses concise and under 200 words
- Use bullet points for step-by-step instructions
- Use clear headings when needed
- Avoid repeating information
- Be direct and helpful
- If multiple solutions exist, present the main one first
- End with "Need more help? Just ask!" if appropriate"""
                },
                {"role": "user", "content": question}
            ],
            max_tokens=300,
            temperature=0.3
        )
        
        # Clean up the response
        clean_response = response.choices[0].message.content.strip()
        
        # Remove any duplicate sentences or phrases
        lines = clean_response.split('\n')
        unique_lines = []
        seen = set()
        
        for line in lines:
            line_clean = line.strip()
            if line_clean and line_clean not in seen:
                unique_lines.append(line)
                seen.add(line_clean)
        
        return '\n'.join(unique_lines)
        
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def answer_query(query):
    """Main function to answer user queries"""
    print(f"Processing query: {query}")
    
    # Search for relevant documents
    top_docs = search_docs(query)
    
    if not top_docs:
        return "I couldn't find relevant information in my knowledge base."
    
    # Combine context from top documents
    context = "\n\n".join([doc.get("text", "")[:1000] for doc in top_docs])
    
    # Generate response using OpenAI
    response = generate_response(context, query)
    print(f"Generated response: {response}")
    
    return response

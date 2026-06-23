import os
import json
import sys
import time
from dotenv import load_dotenv
import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure stdout to support UTF-8 characters on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key or api_key == "YOUR_GEMINI_API_KEY":
    api_key = None

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.1-flash-lite')
else:
    model = None

def generate_content_with_retry(prompt, generation_config=None, request_options=None):
    if not model:
        raise Exception("Model is not initialized.")
    max_retries = 5
    for attempt in range(max_retries):
        try:
            kwargs = {}
            if generation_config:
                kwargs["generation_config"] = generation_config
            if request_options:
                kwargs["request_options"] = request_options
            else:
                kwargs["request_options"] = {"timeout": 60.0}
            return model.generate_content(prompt, **kwargs)
        except Exception as e:
            if "429" in str(e) or "Quota" in str(e) or "ResourceExhausted" in str(e) or "rate limit" in str(e).lower():
                sleep_time = (attempt + 1) * 12
                print(f"\n[Gemini API] Rate limit hit. Sleeping for {sleep_time}s and retrying (attempt {attempt+1}/{max_retries})...")
                time.sleep(sleep_time)
            else:
                raise e
    raise Exception("Max retries exceeded for generate_content due to rate limits.")

dataset_dir = "./dataset"

def load_documents_and_chunk():
    chunks = []
    chunk_sources = []
    
    docs = [f for f in os.listdir(dataset_dir) if f.endswith(".txt")]
    docs.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))
    
    for doc in docs:
        path = os.path.join(dataset_dir, doc)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Extract title and snippet if available
        lines = content.split("\n")
        title = lines[1].replace("Title:", "").strip() if len(lines) > 1 else doc
        
        # Simple paragraph chunking
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        for p in paragraphs:
            # Skip very short paragraphs
            if len(p) < 40:
                continue
            # If paragraph is very long, split into smaller pieces
            if len(p) > 2000:
                sub_chunks = [p[i:i+1500] for i in range(0, len(p), 1200)]
                for sc in sub_chunks:
                    chunks.append(sc)
                    chunk_sources.append(f"{doc} ({title})")
            else:
                chunks.append(p)
                chunk_sources.append(f"{doc} ({title})")
                
    return chunks, chunk_sources

class FlatRAGEngine:
    def __init__(self):
        print("Loading corpus and building TF-IDF index for Flat RAG...")
        self.chunks, self.sources = load_documents_and_chunk()
        
        # Build TF-IDF
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(self.chunks)
        print(f"Flat RAG index ready with {len(self.chunks)} text chunks.")
        
    def retrieve(self, query, top_k=3):
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top K indices
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            score = similarities[idx]
            if score > 0.0:  # Only include if there is some overlap
                results.append({
                    "chunk": self.chunks[idx],
                    "source": self.sources[idx],
                    "score": score
                })
        return results

    def query(self, query):
        print(f"\n[FlatRAG] Query: '{query}'")
        retrieved = self.retrieve(query)
        
        # Textualize retrieved context
        context_parts = []
        for idx, item in enumerate(retrieved):
            context_parts.append(f"Source [{idx+1}]: {item['source']}\nContent: {item['chunk']}\n")
            
        context = "\n".join(context_parts)
        
        if not model:
            if not context:
                return "[Offline Mode] No relevant documents found."
            return f"[Offline Mode] Retrieved Context:\n{context}\n(Please configure GEMINI_API_KEY in .env to get LLM response)"
            
        prompt = f"""
You are an expert analyst. Answer the user's question using the provided document context.
Prioritize the facts retrieved from the context. If the context does not have enough information, you may use your general knowledge, but clearly distinguish between what came from the context and what is general knowledge.

Document Context:
{context if context else "No relevant document context found."}

Question:
{query}

Answer:
"""
        try:
            response = generate_content_with_retry(prompt, request_options={"timeout": 60.0})
            return response.text.strip()
        except Exception as e:
            return f"Error generating answer: {e}\n\nRetrieved Context:\n{context}"

def main():
    engine = FlatRAGEngine()
    test_query = "What is the financial performance of VinFast in Q3 2024?"
    answer = engine.query(test_query)
    print("\n[FlatRAG Answer]:\n", answer)

if __name__ == "__main__":
    main()

import os
import json
import sys
import time
import networkx as nx
from networkx.readwrite import json_graph
from dotenv import load_dotenv
import google.generativeai as genai

# Configure stdout to support UTF-8 characters on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key or api_key == "YOUR_GEMINI_API_KEY":
    print("[ERROR] Please set your actual GEMINI_API_KEY in the .env file before running this script.")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3.1-flash-lite')

dataset_dir = "./dataset"
output_graph_path = "./tech_company_graph.json"

def clean_text(text):
    # Truncate text if it's exceptionally long to save tokens and prevent rate limit issues
    if len(text) > 6000:
        return text[:6000] + "\n... [TRUNCATED] ..."
    return text

def extract_triples_batch(batch_dict):
    """
    Extracts triples for a batch of documents. 
    batch_dict: dict mapping doc_name -> content
    """
    documents_str = ""
    for doc_name, content in batch_dict.items():
        documents_str += f"=== DOCUMENT: {doc_name} ===\n{content}\n\n"
        
    prompt = f"""
You are an expert information extraction system.
Analyze the following documents and extract key entities and their relationships.
Focus on technology companies (e.g., Tesla, OpenAI, Microsoft, Google, VinFast, Polestar, Zeekr, Nvidia, Cadillac, Mercedes), people (e.g., Elon Musk, Sam Altman), products/technologies (e.g., ChatGPT, electric vehicles, batteries, Autopilot), metrics/statistics (e.g., sales growth, market share, transaction price), and locations/regions (e.g., US, China, California).

For each document, extract the key relationships.
Format your output STRICTLY as a JSON object where the keys are the exact document names (e.g. "doc_1.txt") and the values are JSON arrays of objects containing:
- "subject": The name of the subject entity (e.g., "OpenAI"). Capitalized and normalized.
- "relation": A short, uppercase relation name (e.g., "FOUNDED_BY", "COMPETES_WITH", "ACQUIRED", "PARTNERED_WITH", "DEVELOPED", "HAS_MARKET_SHARE", "LOCATED_IN", "EXPERIENCED_GROWTH").
- "object": The name of the object entity (e.g., "Sam Altman"). Capitalized and normalized.

Example output format:
{{
  "doc_1.txt": [
    {{"subject": "OpenAI", "relation": "FOUNDED_BY", "object": "Sam Altman"}},
    {{"subject": "Tesla", "relation": "MANUFACTURES", "object": "Electric Vehicles"}}
  ],
  "doc_2.txt": [
    {{"subject": "Tesla", "relation": "COMPETES_WITH", "object": "BYD"}}
  ]
}}

Do not include any explanation or markdown formatting. Return ONLY the raw JSON object mapping.

Documents to analyze:
{documents_str}
"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"},
                request_options={"timeout": 60.0}
            )
            data = json.loads(response.text.strip())
            return data
        except Exception as e:
            if "429" in str(e) or "Quota exceeded" in str(e) or "ResourceExhausted" in str(e):
                sleep_time = (2 ** attempt) * 15
                print(f"\n[Batch] Rate limit hit. Sleeping for {sleep_time}s...")
                time.sleep(sleep_time)
            else:
                print(f"\n[Batch] Error extracting: {e}")
                break
    return {}

def extract_triples_single(doc_name, content):
    """
    Fallback method to process a single document if the batch fails or has issues.
    """
    prompt = f"""
You are an expert information extraction system.
Analyze the following document and extract key entities and their relationships.
Focus on technology companies, people, products, metrics, and locations.

Format your output STRICTLY as a JSON array of objects, where each object has:
- "subject": The name of the subject entity. Capitalized and normalized.
- "relation": A short, uppercase relation name.
- "object": The name of the object entity. Capitalized and normalized.

Example output:
[
  {{"subject": "OpenAI", "relation": "FOUNDED_BY", "object": "Sam Altman"}}
]

Return ONLY the raw JSON array.

Document: {doc_name}
Content:
---
{content}
---
"""
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"},
            request_options={"timeout": 60.0}
        )
        return json.loads(response.text.strip())
    except Exception as e:
        print(f"\n[{doc_name}] Fallback failed: {e}")
        return []

def main():
    print("Starting optimized entity and relation extraction (Indexing)...")
    
    docs = [f for f in os.listdir(dataset_dir) if f.endswith(".txt")]
    docs.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))
    
    G = nx.MultiDiGraph()
    total_docs = len(docs)
    batch_size = 5
    
    start_time = time.time()
    
    # Process in batches of 5
    for i in range(0, total_docs, batch_size):
        batch_files = docs[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(total_docs + batch_size - 1)//batch_size} (files: {batch_files}) ... ", end="", flush=True)
        
        batch_dict = {}
        for doc in batch_files:
            path = os.path.join(dataset_dir, doc)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                batch_dict[doc] = clean_text(content)
                
        batch_results = extract_triples_batch(batch_dict)
        
        # Process results
        for doc in batch_files:
            triples = batch_results.get(doc)
            
            # If batch did not return results for this doc, try single document fallback
            if not triples:
                print(f"\n  [Fallback] No triples in batch for {doc}. Running fallback...", end="", flush=True)
                triples = extract_triples_single(doc, batch_dict[doc])
                
            added_count = 0
            for triple in triples:
                sub = triple.get("subject")
                rel = triple.get("relation")
                obj = triple.get("object")
                if sub and rel and obj:
                    sub = sub.strip()
                    rel = rel.strip().upper()
                    obj = obj.strip()
                    if not G.has_node(sub):
                        G.add_node(sub, label=sub)
                    if not G.has_node(obj):
                        G.add_node(obj, label=obj)
                    G.add_edge(sub, obj, relation=rel, source_doc=doc)
                    added_count += 1
            print(f"{doc}({added_count}) ", end="", flush=True)
            
        print("done.")
        
        # Save intermediate graph
        data = json_graph.node_link_data(G)
        with open(output_graph_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        # Respect rate limits
        if i + batch_size < total_docs:
            time.sleep(4.0)
            
    print(f"\nIndexing completed in {time.time() - start_time:.2f} seconds!")
    print(f"Final Graph size: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")

if __name__ == "__main__":
    main()

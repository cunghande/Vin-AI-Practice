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
    # Fallback to offline/mock message if API key is not configured yet
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

def load_graph(graph_path="./tech_company_graph.json"):
    if not os.path.exists(graph_path):
        print(f"[ERROR] Graph file {graph_path} not found. Please run indexing.py first.")
        return None
    with open(graph_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return json_graph.node_link_graph(data)

def extract_entities_from_query(query):
    if not model:
        # Simple heuristic fallback if offline
        words = query.split()
        capitalized = [w.strip("?,.!") for w in words if w[0].isupper() if w]
        return capitalized if capitalized else ["Tesla"]

    prompt = f"""
Identify the primary entities (companies, people, organizations, technologies) in the following user question.
Return your answer STRICTLY as a JSON array of strings.

Question:
"{query}"

Example output:
["Tesla", "Nvidia"]
"""
    try:
        response = generate_content_with_retry(
            prompt,
            generation_config={"response_mime_type": "application/json"},
            request_options={"timeout": 60.0}
        )
        return json.loads(response.text.strip())
    except Exception as e:
        print(f"Error extracting entities: {e}")
        # Return fallback entity based on keywords
        q_lower = query.lower()
        for brand in ["tesla", "openai", "microsoft", "google", "vinfast", "polestar", "zeekr", "nvidia", "apple"]:
            if brand in q_lower:
                return [brand.capitalize()]
        return []

def search_nodes(G, entity_name):
    # Case-insensitive substring match to find node names
    matched = []
    entity_name_lower = entity_name.lower()
    for node in G.nodes():
        if entity_name_lower in str(node).lower() or str(node).lower() in entity_name_lower:
            matched.append(node)
    return matched

def traverse_2_hop(G, start_nodes):
    visited_nodes = set(start_nodes)
    visited_edges = []
    
    # Hop 1
    hop_1_nodes = set()
    for node in start_nodes:
        if not G.has_node(node):
            continue
        # Outgoing edges
        for u, v, key, data in G.out_edges(node, keys=True, data=True):
            visited_edges.append((u, data.get("relation", "LINKED_TO"), v))
            hop_1_nodes.add(v)
        # Incoming edges
        for u, v, key, data in G.in_edges(node, keys=True, data=True):
            visited_edges.append((u, data.get("relation", "LINKED_TO"), v))
            hop_1_nodes.add(u)
            
    visited_nodes.update(hop_1_nodes)
    
    # Hop 2
    for node in hop_1_nodes:
        if node in start_nodes: # skip start nodes
            continue
        # Outgoing edges
        for u, v, key, data in G.out_edges(node, keys=True, data=True):
            # Only traverse to nodes we want to include
            if v not in start_nodes:
                visited_edges.append((u, data.get("relation", "LINKED_TO"), v))
                visited_nodes.add(v)
        # Incoming edges
        for u, v, key, data in G.in_edges(node, keys=True, data=True):
            if u not in start_nodes:
                visited_edges.append((u, data.get("relation", "LINKED_TO"), v))
                visited_nodes.add(u)
                
    # Remove duplicates from visited_edges
    unique_edges = []
    seen = set()
    for edge in visited_edges:
        edge_key = (edge[0], edge[1], edge[2])
        if edge_key not in seen:
            seen.add(edge_key)
            unique_edges.append(edge)
            
    return unique_edges

def textualize_edges(edges):
    sentences = []
    for u, rel, v in edges:
        # Convert UPPERCASE relations to readable format
        rel_str = rel.replace("_", " ").lower()
        sentences.append(f"- {u} {rel_str} {v}")
    return "\n".join(sentences)

def query_graph_rag(query, G):
    if G is None:
        return "Graph database is not initialized."
        
    print(f"\n[GraphRAG] Query: '{query}'")
    
    # Step 1: Extract entity
    entities = extract_entities_from_query(query)
    print(f"[GraphRAG] Extracted entities: {entities}")
    
    # Step 2: Find nodes in Graph
    start_nodes = []
    for ent in entities:
        matched = search_nodes(G, ent)
        start_nodes.extend(matched)
    
    # Deduplicate start nodes
    start_nodes = list(set(start_nodes))
    print(f"[GraphRAG] Matched nodes in graph: {start_nodes}")
    
    # Step 3: Traverse 2-hop
    edges = traverse_2_hop(G, start_nodes)
    print(f"[GraphRAG] Found {len(edges)} relations in 2-hop neighborhood.")
    
    # Step 4: Textualization
    context = textualize_edges(edges)
    
    # Step 5: Answer generation using LLM
    if not model:
        # Offline mock answer using graph context
        if not context:
            return f"[Offline Mode] No graph relationships found for {entities}."
        return f"[Offline Mode] Graph context retrieved:\n{context}\n(Please configure GEMINI_API_KEY in .env to get LLM response)"
        
    prompt = f"""
You are an expert analyst. Answer the user's question using the provided graph database relations (subject-relation-object triples).
Prioritize the facts retrieved from the graph database. If the graph does not have enough information, you may use your general knowledge, but clearly distinguish between what came from the graph and what is general knowledge.

Graph Context (triples extracted around the query entities):
{context if context else "No matching relations found in the graph database."}

Question:
{query}

Answer:
"""
    try:
        response = generate_content_with_retry(prompt, request_options={"timeout": 60.0})
        return response.text.strip()
    except Exception as e:
        return f"Error generating answer: {e}\n\nGraph Context retrieved:\n{context}"

def main():
    G = load_graph()
    if G:
        print("Graph loaded successfully.")
        # Test query
        test_query = "What is the financial performance of VinFast in Q3 2024?"
        answer = query_graph_rag(test_query, G)
        print("\n[GraphRAG Answer]:\n", answer)

if __name__ == "__main__":
    main()

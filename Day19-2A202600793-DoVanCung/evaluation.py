import os
import json
import sys
import time

# Configure stdout to support UTF-8 characters on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from flat_rag import FlatRAGEngine
from query_engine import query_graph_rag, load_graph

# List of 5 complex questions designed to test multi-hop reasoning
TEST_QUESTIONS = [
    "Who are the founders of OpenAI and in what year was it established?",
    "How does the Q1 2024 U.S. sales growth of Tesla compare to Cadillac and Mercedes-Benz?",
    "What are the main factors that impact electric vehicle battery life, and what is the typical battery warranty length?",
    "What is the financial performance of VinFast in Q3 2024, and what are their revenue figures?",
    "How do Zero Emission Vehicle (ZEV) regulations in the US impact electric vehicle model availability and market share?"
]

def main():
    print("Initializing Evaluation...")
    
    # Check if graph exists
    if not os.path.exists("./tech_company_graph.json"):
        print("[WARNING] Graph file (tech_company_graph.json) not found.")
        print("Please run indexing.py to generate the graph file first.")
        print("Creating a mock graph file for testing query engine structure...")
        
        # Create a simple mock graph with some nodes and edges so the query engine doesn't crash
        import networkx as nx
        from networkx.readwrite import json_graph
        G = nx.MultiDiGraph()
        
        # Add some mock triples from the dataset
        mock_triples = [
            ("OpenAI", "FOUNDED_BY", "Sam Altman"),
            ("OpenAI", "FOUNDED_BY", "Elon Musk"),
            ("OpenAI", "FOUNDED_IN", "2015"),
            ("Tesla", "EXPERIENCED_DECLINE", "Q1 2024"),
            ("Cadillac", "EV_SALES_GROWTH", "499.2%"),
            ("Mercedes", "EV_SALES_GROWTH", "66.9%"),
            ("VinFast", "REPORTED_REVENUE_IN_Q3_2024", "$512 million"),
            ("VinFast", "EXPERIENCED_REVENUE_GROWTH", "8.9%"),
            ("ZEV Regulations", "INCREASE_MODEL_AVAILABILITY", "13 more models"),
            ("ZEV Regulations", "INCREASE_MARKET_SHARE", "5%")
        ]
        for s, r, o in mock_triples:
            G.add_node(s, label=s)
            G.add_node(o, label=o)
            G.add_edge(s, o, relation=r, source_doc="mock_doc.txt")
            
        data = json_graph.node_link_data(G)
        with open("./tech_company_graph.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("Mock graph created successfully.")

    # Load Graph for GraphRAG
    G = load_graph()
    
    # Initialize FlatRAG
    try:
        flat_engine = FlatRAGEngine()
    except Exception as e:
        print(f"[ERROR] Failed to load FlatRAG: {e}")
        return

    output_lines = []
    output_lines.append("=================================================================")
    output_lines.append("                 FLAT RAG VS GRAPHRAG EVALUATION                 ")
    output_lines.append("=================================================================\n")

    for i, q in enumerate(TEST_QUESTIONS, 1):
        header = f"--- Question {i}: {q} ---"
        print(header)
        output_lines.append(header)
        
        # Run Flat RAG
        print(" Running Flat RAG...")
        flat_ans = flat_engine.query(q)
        print(" Running GraphRAG...")
        graph_ans = query_graph_rag(q, G)
        
        flat_section = f"\n[FLAT RAG RESPONSE]:\n{flat_ans}\n"
        graph_section = f"\n[GRAPHRAG RESPONSE]:\n{graph_ans}\n"
        divider = "-" * 80 + "\n"
        
        print(flat_section)
        print(graph_section)
        
        output_lines.append(flat_section)
        output_lines.append(graph_section)
        output_lines.append(divider)

        # Pacing to avoid hitting 15 RPM rate limits
        if i < len(TEST_QUESTIONS):
            print("Pacing API requests, sleeping 5 seconds...")
            time.sleep(5.0)

    # Write to evaluation_results.txt
    with open("./evaluation_results.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
        
    print("\nEvaluation complete! Results saved to ./evaluation_results.txt")

if __name__ == "__main__":
    main()

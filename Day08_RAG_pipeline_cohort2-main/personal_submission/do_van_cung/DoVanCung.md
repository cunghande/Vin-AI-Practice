# Day08 Personal Submission - Do Van Cung

## Scope

Implemented a local RAG baseline for the individual Day08 tasks:

- Task 1: legal landing files in `data/landing/legal/`
- Task 2: news landing files in `data/landing/news/`
- Task 3: standardized markdown corpus in `data/standardized/`
- Task 4: document loading, chunking, local indexing stub
- Task 5: semantic search with token cosine similarity
- Task 6: lexical BM25 search
- Task 7: reranking and RRF fusion
- Task 8: PageIndex-compatible local fallback
- Task 9: hybrid retrieval pipeline with fallback
- Task 10: generation wrapper with citation-ready context formatting

## Notes

This branch uses a lightweight local implementation so the automated tests can run without external API keys or a hosted vector database. The group can later replace the local retrieval and generation pieces with shared production components for the chatbot demo and evaluation pipeline.

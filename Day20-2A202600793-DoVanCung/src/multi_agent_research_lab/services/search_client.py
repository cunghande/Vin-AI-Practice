"""Search client abstraction for ResearcherAgent."""

from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import SourceDocument


import logging
import requests

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import SourceDocument

logger = logging.getLogger(__name__)


class SearchClient:
    """Provider-agnostic search client skeleton."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.api_key = self.settings.tavily_api_key

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query.

        If api_key is available, calls Tavily API, else returns mock results.
        """
        if self.api_key:
            return self._search_tavily(query, max_results)
        else:
            return self._search_mock(query, max_results)

    def _search_tavily(self, query: str, max_results: int) -> list[SourceDocument]:
        logger.info(f"Performing real Tavily search for query: {query}")
        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": self.api_key,
                "query": query,
                "max_results": max_results,
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("results", []):
                results.append(
                    SourceDocument(
                        title=item.get("title", "Untitled Source"),
                        url=item.get("url"),
                        snippet=item.get("content", ""),
                        metadata={"score": item.get("score", 0.0)}
                    )
                )
            return results
        except Exception as e:
            logger.error(f"Tavily search failed: {e}. Falling back to mock search.")
            return self._search_mock(query, max_results)

    def _search_mock(self, query: str, max_results: int) -> list[SourceDocument]:
        logger.warning("No TAVILY_API_KEY set. Returning mock search results.")
        # Generate rich mock documents based on the query keywords
        q_lower = query.lower()
        if "graphrag" in q_lower or "graph" in q_lower:
            return [
                SourceDocument(
                    title="Introduction to GraphRAG & Entity Extraction",
                    url="https://arxiv.org/abs/2404.16130",
                    snippet="GraphRAG combines knowledge graph generation with LLM retrieval to enable global reasoning over entire text corpora, resolving limitations in standard vector RAG.",
                    metadata={"source": "arxiv"}
                ),
                SourceDocument(
                    title="Microsoft Research: From Local to Global Querying",
                    url="https://github.com/microsoft/graphrag",
                    snippet="By structuring raw text data into an entity-relation graph, GraphRAG supports hierarchically summarizing information across communities of nodes.",
                    metadata={"source": "github"}
                ),
                SourceDocument(
                    title="Comparing Vector RAG vs GraphRAG",
                    url="https://medium.com/ai-insights/rag-vs-graphrag",
                    snippet="Standard RAG is optimized for local queries ('Find specific info on X'), whereas GraphRAG excel at global aggregation questions ('What are the major themes?').",
                    metadata={"source": "medium"}
                )
            ][:max_results]
        else:
            return [
                SourceDocument(
                    title=f"Comprehensive Overview of {query}",
                    url="https://wikipedia.org/wiki/Special_Search",
                    snippet=f"This document provides historical context, definitions, and applications of {query} in modern information technology frameworks.",
                    metadata={"source": "wikipedia"}
                ),
                SourceDocument(
                    title=f"State-of-the-Art Research in {query}",
                    url="https://scholar.google.com/search",
                    snippet=f"A collection of academic papers exploring advanced systems, algorithms, and architectures relating to {query}.",
                    metadata={"source": "scholar"}
                )
            ][:max_results]


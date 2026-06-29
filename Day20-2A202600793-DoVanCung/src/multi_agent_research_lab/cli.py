"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass
    settings = get_settings()
    configure_logging(settings.log_level)


from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.services.storage import LocalArtifactStore

@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a real single-agent RAG baseline."""
    _init()
    console.print(f"[bold green]Running Single-Agent Baseline for query:[/bold green] {query}")
    
    # 1. Search
    search_client = SearchClient()
    sources = search_client.search(query)
    
    # 2. Format
    formatted_sources = []
    for idx, doc in enumerate(sources, 1):
        formatted_sources.append(
            f"[Source {idx}]\n"
            f"Title: {doc.title}\n"
            f"Snippet: {doc.snippet}\n"
        )
    sources_text = "\n".join(formatted_sources)
    
    # 3. LLM call
    llm = LLMClient()
    system_prompt = (
        "You are a Single-Agent Research Assistant.\n"
        "Your task is to write a comprehensive report answering the user's query using the provided source documents.\n"
        "Make sure to cite your sources using [Source X] references."
    )
    user_prompt = f"Query: {query}\n\nSearch Results:\n{sources_text}"
    
    llm_res = llm.complete(system_prompt, user_prompt)
    
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    state.sources = sources
    state.final_answer = llm_res.content
    state.agent_results.append(
        AgentResult(
            agent=AgentName.WRITER,
            content=llm_res.content,
            metadata={
                "input_tokens": llm_res.input_tokens,
                "output_tokens": llm_res.output_tokens,
                "cost_usd": llm_res.cost_usd
            }
        )
    )
    
    console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline Result"))


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""
    _init()
    console.print(f"[bold blue]Running Multi-Agent Workflow for query:[/bold blue] {query}")
    
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
        
    console.print(Panel.fit(result.final_answer or "No final answer produced.", title="Multi-Agent Result"))
    console.print("[bold green]Agent Route History:[/bold green]")
    console.print(" -> ".join(result.route_history))


@app.command()
def benchmark(
    query: Annotated[
        str,
        typer.Option("--query", "-q", help="Research query to run benchmark on")
    ] = "Research GraphRAG state-of-the-art and write a 500-word summary",
) -> None:
    """Run benchmark comparing single-agent vs multi-agent and output a report."""
    _init()
    console.print(Panel.fit(f"Query: {query}", title="Starting System Benchmark"))

    # Baseline Runner
    def runner_baseline(q: str) -> ResearchState:
        search_client = SearchClient()
        sources = search_client.search(q)
        formatted_sources = []
        for idx, doc in enumerate(sources, 1):
            formatted_sources.append(f"[Source {idx}] {doc.title}: {doc.snippet}")
        sources_text = "\n".join(formatted_sources)
        
        llm = LLMClient()
        system_prompt = (
            "You are a Single-Agent Research Assistant.\n"
            "Synthesize a report on the user query based on the search results.\n"
            "Cite sources using [Source X] references."
        )
        user_prompt = f"Query: {q}\n\nSearch Results:\n{sources_text}"
        llm_res = llm.complete(system_prompt, user_prompt)
        
        state = ResearchState(request=ResearchQuery(query=q))
        state.sources = sources
        state.final_answer = llm_res.content
        state.agent_results.append(
            AgentResult(
                agent=AgentName.WRITER,
                content=llm_res.content,
                metadata={
                    "input_tokens": llm_res.input_tokens,
                    "output_tokens": llm_res.output_tokens,
                    "cost_usd": llm_res.cost_usd
                }
            )
        )
        return state

    # Multi-Agent Runner
    def runner_multi_agent(q: str) -> ResearchState:
        state = ResearchState(request=ResearchQuery(query=q))
        workflow = MultiAgentWorkflow()
        return workflow.run(state)

    # Execute benchmarks
    _, baseline_metrics = run_benchmark("Single-Agent Baseline", query, runner_baseline)
    _, multi_agent_metrics = run_benchmark("Multi-Agent System", query, runner_multi_agent)

    # Render and store report
    metrics_list = [baseline_metrics, multi_agent_metrics]
    report_md = render_markdown_report(metrics_list)
    
    store = LocalArtifactStore()
    report_path = store.write_text("benchmark_report.md", report_md)
    
    console.print(f"[bold green]Benchmark completed successfully![/bold green]")
    console.print(f"Report written to: [italic]{report_path.absolute()}[/italic]")
    console.print(report_md)



if __name__ == "__main__":
    app()

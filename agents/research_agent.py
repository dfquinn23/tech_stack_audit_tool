# agents/research_agent.py
# CrewAI agent that locates and compiles recent changelogs / release notes for a given tool.

from crewai import Agent, Task
from textwrap import dedent


def get_research_agent(llm, tools: list | None = None):
    """
    tools: optional list of LangChain/Crew tools (web search, HTTP, scraper) to empower the agent later.
           For now you can pass None; agent will rely on upstream fetcher output.
    """
    return Agent(
        role="Changelog Researcher",
        goal="Identify and compile recent, relevant changelogs or release notes for a given software tool.",
        backstory=dedent("""\
            You are a meticulous research specialist. You find authoritative sources for software release notes, 
            and collect concise entries with dates, titles, and descriptions suitable for downstream summarization.
        """),
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=tools or []
    )


def get_research_task(agent, tool_name: str, seed_entries: list[dict] | None = None, lookback_days: int = 365):
    """
    seed_entries: optional list of dicts like {"date": "...", "title": "...", "description": "..."} (e.g., from core.changelog_fetcher)
    lookback_days: guidance to the agent for recency
    """
    seeds_str = ""
    if seed_entries:
        for e in seed_entries:
            d = e.get("date", "Unknown date")
            t = e.get("title", "")
            desc = e.get("description", "")
            seeds_str += f"- [{d}] {t}: {desc}\n"

    return Task(
        description=dedent(f"""\
            Tool: {tool_name}
            Objective: Compile a concise list of recent changelog entries (roughly last {lookback_days} days) for this tool.
            
            If you have seed entries (below), verify and refine them; if not, or if incomplete, identify likely sources 
            (official changelog pages, release notes, support docs) and reconstruct a short list with:
              - date (YYYY-MM-DD if possible)
              - title
              - one-sentence description

            Seed entries (may be partial or empty):
            {seeds_str or "(none provided)"}

            Output format:
            - [YYYY-MM-DD] Title: one-sentence description
            - [YYYY-MM-DD] Title: one-sentence description
        """),
        agent=agent,
        expected_output="A bullet list of dated changelog lines as specified above."
    )

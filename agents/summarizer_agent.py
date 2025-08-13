# ROLE - accepts a tool name and the raw changelog entries from changelog_fetcher.py,
# summarizes each update for a business audience, and returns the summaries for the audit report

from crewai import Agent, Task
from textwrap import dedent


def get_summarizer_agent(llm):
    return Agent(
        role="Changelog Summarizer",
        goal="Convert raw software changelog entries into short, business-friendly summaries for client audit reports.",
        backstory=dedent("""\
            You are a tech-savvy business analyst at an AI consulting firm.
            Your job is to summarize software update logs into clear, concise language that non-technical operations and compliance staff can understand.
        """),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )


def get_summarizer_task(agent, tool_name, changelog_entries):
    updates = ""
    for entry in changelog_entries:
        date = entry.get("date", "Unknown date")
        title = entry.get("title", "")
        description = entry.get("description", "")
        updates += f"\n- [{date}] {title}: {description}"

    return Task(
        description=dedent(f"""\
           You are given raw change log entries for the software tool: {tool_name}.
           Your task is to produce short summaries for each update using clear, non-technical language.

           The summaries will be included in a client audit report.
           Summarize each update in one sentence, and ensure the tone is neutral and business-friendly.

           Changelog Entries:
           {updates}
        """),
        agent=agent,
        expected_output="A bullet-point list os one-sentence summaries of each changelog entry."
    )

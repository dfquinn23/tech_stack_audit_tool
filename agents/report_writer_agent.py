# agents/report_writer_agent.py
# CrewAI agent that composes polished Markdown report sections (or full report) from pipeline outputs.

from crewai import Agent, Task
from textwrap import dedent


def get_report_writer_agent(llm):
    return Agent(
        role="Report Writer",
        goal="Compose a clear, client-ready Markdown report from audit pipeline outputs.",
        backstory=dedent("""\
            You are a concise technical writer who prepares executive-friendly summaries for RIAs and asset managers. 
            You format content cleanly in Markdown with headings, bullets, and short paragraphs.
        """),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )


def get_report_section_task(agent, tool_name: str, category: str, used_by: str, criticality: str,
                            summaries: list[str], audit_text: str, integrations_text: str):
    """
    Returns a Task that asks for a single tool section in Markdown.
    """
    summaries_md = "\n".join(
        [f"- {s}" for s in summaries]) if summaries else "- (no summaries)"
    return Task(
        description=dedent(f"""\
            Create a polished Markdown section for the tool below. Keep it concise and business-friendly.

            Tool: {tool_name}
            Category: {category}
            Users: {used_by}
            Criticality: {criticality}

            Summaries:
            {summaries_md}

            Audit Insights:
            {audit_text.strip()}

            Integration Opportunities:
            {integrations_text.strip()}

            Requirements:
            - Start with '### {tool_name}'
            - Next line: _Category: <category> • Users: <users> • Criticality: <criticality>_
            - Then '**Summaries**' as a subheader with bullets
            - Then '**Audit Insights**' as a short, readable block (bullets or brief paragraphs)
            - Then '**Integration Opportunities**' as bullets
            - Be succinct. No fluff. No repeated headings. No extra introductions.
        """),
        agent=agent,
        expected_output="A single Markdown section for this tool as specified."
    )


def get_full_report_task(agent, generated_sections_md: list[str]):
    """
    If you already have per-tool sections, this composes the final report header + sections.
    """
    sections_joined = "\n\n".join(
        ms.strip() for ms in generated_sections_md if ms and ms.strip())
    return Task(
        description=dedent(f"""\
            Assemble the following Markdown sections into a single cohesive report. Add a title and timestamp header,
            and ensure section spacing is consistent. Do not alter the content of each section beyond light spacing fixes.

            Sections:
            {sections_joined}

            Header format:
            # Tech Stack Audit Report
            _Generated: <YYYY-MM-DD HH:MM>_

            Insert a horizontal rule '---' after the header, then the sections.
        """),
        agent=agent,
        expected_output="A complete Markdown report with the header and the provided sections."
    )

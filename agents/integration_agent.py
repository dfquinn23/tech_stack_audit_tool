# CrewAI agent that analyzes a tool's updates and audit insights to propose
# specific, high-value n8n automation workflows connecting it with other tools in the firm's stack.


# agents/integration_agent.py

from crewai import Agent, Task
from textwrap import dedent


def get_integration_agent(llm):
    return Agent(
        role="Integration & Automation Architect",
        goal=(
            "Recommend concrete, high-ROI automations between the firm's tools using n8n. "
            "Each suggestion should include a trigger, the key nodes/steps, and the business value."
        ),
        backstory=dedent("""\
            You design pragmatic automations for wealth/asset management workflows.
            You know common vendor ecosystems (Microsoft 365, Zoom, custodians, CRMs like Wealthbox),
            and how to connect them via n8n (HTTP nodes, Webhooks, IMAP/Email, Microsoft Graph, S3/SharePoint, etc.).
            You avoid speculative tools not present in the firm's stack.
        """),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )


def get_integration_task(agent, firm_tools, focal_tool, summaries, audit_text):
    """
    firm_tools: list[str] of all tools in the stack (for cross-tool ideas)
    focal_tool: current tool being analyzed
    summaries: list[str] of summarized updates for the focal tool
    audit_text: str full audit analysis for the focal tool
    """
    tools_csv = ", ".join(sorted(set([t.strip() for t in firm_tools if t])))
    summaries_bullets = "\n".join(
        [f"- {s}" for s in summaries]) if summaries else "- (no summaries)"
    audit_excerpt = audit_text.strip()[:2200]  # keep prompt compact

    return Task(
        description=dedent(f"""\
            The firm's tool stack includes: {tools_csv}.
            You're focusing on: {focal_tool}.

            Summarized Updates for {focal_tool}:
            {summaries_bullets}

            Audit Insights (context):
            {audit_excerpt}

            Produce 3-6 **specific** n8n automation opportunities that connect {focal_tool} with other tools in the firm's stack.
            Prioritize measurable business value for an RIA/wealth manager (client comms, compliance logging, research ops).
            Each suggestion MUST follow this compact schema:

            - **Flow Name**: <short name>
              **Trigger**: <event in focal tool or another tool>
              **Key Nodes**: <n8n nodes or APIs to use, e.g., Webhook, HTTP Request, Microsoft Graph, IMAP Email, SharePoint, S3, CSV, Code>
              **Steps**: <2-5 short steps describing the flow>
              **Value**: <why it matters / KPI impact>

            Rules:
            - ONLY reference tools that appear in the firm's stack list.
            - Prefer Microsoft 365 integrations where relevant (since 365 is in the stack).
            - If the update mentions AI summarization/transcripts (e.g., Zoom), suggest auto-filing + notifying relevant teams.
            - If custodial data (e.g., Schwab) is involved, include compliance logging or CRM enrichment (Wealth Box).
            - Keep each suggestion to ~4–6 lines. No fluff.
        """),
        agent=agent,
        expected_output=(
            "A concise list of 3-6 automation opportunities in the schema above, "
            "each connecting the focal tool with other tools from the firm's stack."
        )
    )

# Takes the summaries from the summarizer Agent andanswewrs the question:
# Why does this update matter to the client?

from crewai import Agent, Task
from textwrap import dedent


def get_audit_agent(llm):
    return Agent(
        role="Audit Analyst",
        goal="Assess the business impact of recent software developments in an asset management firm's tech stack",
        backstory=dedent("""\
            You are a technology audit consultant specializing in financial services.
            Your job is to analyze software updates and explain their relevance, risks, and 
            potential benefits to our asset managememnt client.
                           """),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )


def get_audit_task(agent, tool_name, category, used_by, summaries):
    summaries_text = "\n".join([f"- {s}" for s in summaries])

    return Task(
        description=dedent(f"""\
            You are reviewing updates for the tool: {tool_name}.
            Category: {category}
            Primary Users: {used_by}

            Summarized Updates:
            {summaries_text}

            For each update, explain:
            1. Why it matters for the firm's operations or clients
            2. Any possible risks or challenges
            3. Whether it requires immediate adoption or can be monitored for later

            Output your analysis as bullet points under each update.
        """),
        agent=agent,
        expected_output="Bullet-point business impact anbalysis for each update."
    )

# run_pipeline.py
# Tech Stack Audit Tool pipeline:
# 1) Load tool list
# 2) Fetch changelogs (mock for now)
# 3) (optional) Research agent to refine/expand entries
# 4) Summarize updates (CrewAI agent)
# 5) Analyze business impact (CrewAI agent)
# 6) Recommend n8n integrations (CrewAI agent)
# 7) Write a Markdown report (optionally via Report Writer agent)

import os
import sys
from datetime import datetime
from pathlib import Path
from textwrap import dedent

from agents.research_agent import get_research_agent, get_research_task
from agents.report_writer_agent import (
    get_report_writer_agent,
    get_report_section_task,
    get_full_report_task,
)

# --- Env & LLM setup ---
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)  # ensure .env overrides shell vars
except Exception:
    pass  # optional

from langchain_openai import ChatOpenAI
from crewai import Crew

# --- Local modules ---
from core.input_handler import load_input
from core.changelog_fetcher import fetch_mock_changelog
from agents.summarizer_agent import get_summarizer_agent, get_summarizer_task
from agents.audit_agent import get_audit_agent, get_audit_task
from agents.integration_agent import get_integration_agent, get_integration_task


# --- Crew helpers (version-agnostic + output normalizer) ---
def run_crew(crew):
    """Run a Crew across versions (kickoff vs run)."""
    if hasattr(crew, "kickoff"):
        return crew.kickoff()
    if hasattr(crew, "run"):
        return crew.run()
    raise AttributeError(
        "Crew has neither kickoff() nor run(). Update CrewAI.")


def crew_to_text(result) -> str:
    """Normalize CrewAI CrewOutput/TaskOutput to plain text."""
    if isinstance(result, str):
        return result
    for attr in ("final_output", "output", "raw", "result", "content"):
        if hasattr(result, attr):
            val = getattr(result, attr)
            if isinstance(val, (str, bytes)):
                return val.decode() if isinstance(val, bytes) else val
            if isinstance(val, dict):
                for k in ("final_output", "output", "result", "content"):
                    if k in val and isinstance(val[k], str):
                        return val[k]
                return str(val)
    return str(result)


def research_lines_to_entries(text: str):
    """
    Parse lines like '- [YYYY-MM-DD] Title: description' back into dict entries.
    Returns list[{"date": str, "title": str, "description": str}]
    """
    entries = []
    for raw in (text or "").splitlines():
        line = raw.strip().lstrip("- ").strip()
        if not line or not line.startswith("["):
            continue
        try:
            # [DATE] Title: desc
            rdate, rest = line.split("]", 1)
            date = rdate[1:].strip()
            title, desc = rest.split(":", 1)
            entries.append(
                {"date": date.strip(), "title": title.strip(),
                 "description": desc.strip()}
            )
        except ValueError:
            continue
    return entries


# --- Misc helpers ---
def get_llm():
    """Create a single LLM instance for all agents."""
    model = os.getenv("OPENAI_MODEL", "gpt-5")
    temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
    # Fail fast if missing key
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "Missing OPENAI_API_KEY. Check your .env or environment.")
    return ChatOpenAI(model=model, temperature=temperature)


def ensure_output_dir(path_like) -> Path:
    p = Path(path_like)
    p.mkdir(parents=True, exist_ok=True)
    return p


def parse_bullet_list(text: str):
    """
    Convert agent output into a list of bullet items.
    Handles '-', '*', or '•' bullets; falls back to line split; de-dups.
    """
    s = (text or "").strip()
    if not s:
        return []
    lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
    bullets = []
    for ln in lines:
        if ln.startswith(("- ", "* ", "• ")):
            bullets.append(ln[2:].strip())
        else:
            bullets.append(ln)
    # de-dup
    seen, uniq = set(), []
    for b in bullets:
        if b not in seen:
            seen.add(b)
            uniq.append(b)
    return uniq


def main():
    project_root = Path(__file__).resolve().parent
    output_dir = ensure_output_dir(project_root / "output")

    # Shared LLM
    llm = get_llm()

    # Feature toggles
    use_research = os.getenv("USE_RESEARCH_AGENT", "0") == "1"
    use_report_writer = os.getenv("USE_REPORT_WRITER_AGENT", "1") == "1"

    # Load the input CSV (expects headers: Tool Name, Category, Used By, Criticality)
    csv_path = project_root / "data" / "tech_stack_list.csv"
    df = load_input(str(csv_path))

    # Gather tool list for integration context
    firm_tools = df["Tool Name"].astype(str).str.strip().tolist()

    report_sections = []
    print("\n🚀 Starting Tech Stack Audit pipeline...\n")

    for _, row in df.iterrows():
        tool_name = str(row["Tool Name"]).strip()
        category = str(row["Category"]).strip()
        used_by = str(row["Used By"]).strip()
        criticality = str(row["Criticality"]).strip()

        print(
            f"\n====== {tool_name} ({category}, {used_by}, Criticality: {criticality}) ======")

        # 1) Fetch changelogs (mock for now)
        changelog_entries = fetch_mock_changelog(tool_name)

        # Optional: let research agent refine/expand the entries (kept OFF by default)
        if use_research:
            research_agent = get_research_agent(llm, tools=None)
            research_task = get_research_task(
                research_agent, tool_name, seed_entries=changelog_entries, lookback_days=365
            )
            research_crew = Crew(agents=[research_agent], tasks=[
                                 research_task], verbose=True)
            try:
                research_result = run_crew(research_crew)
                research_text = crew_to_text(research_result)
                refined_entries = research_lines_to_entries(research_text)
                if refined_entries:
                    changelog_entries = refined_entries
            except Exception as e:
                print(
                    f"⚠️ Research agent failed for {tool_name}: {e} (continuing with seed entries)")

        # If still no entries, skip
        if not changelog_entries:
            print(f"⚠️  No changelogs found for {tool_name}. Skipping.")
            report_sections.append(
                f"### {tool_name}\n"
                f"_Category: {category} • Users: {used_by} • Criticality: {criticality}_\n\n"
                f"> No changelogs found for this tool (mock source).\n"
            )
            continue

        # 2) Summarize updates (CrewAI agent)
        summarizer_agent = get_summarizer_agent(llm)
        summarizer_task = get_summarizer_task(
            summarizer_agent, tool_name, changelog_entries)
        summarize_crew = Crew(agents=[summarizer_agent], tasks=[
                              summarizer_task], verbose=True)

        try:
            summary_result = run_crew(summarize_crew)
            summary_text = crew_to_text(summary_result)
        except Exception as e:
            print(f"❌ Summarizer failed for {tool_name}: {e}")
            report_sections.append(
                f"### {tool_name}\n"
                f"_Category: {category} • Users: {used_by} • Criticality: {criticality}_\n\n"
                f"> Error summarizing updates: {e}\n"
            )
            continue

        summaries = parse_bullet_list(summary_text)
        print("\n🧠 Summaries:")
        for s in summaries:
            print(f"  • {s}")

        # 3) Audit analysis (CrewAI agent)
        audit_agent = get_audit_agent(llm)
        audit_task = get_audit_task(
            audit_agent, tool_name, category, used_by, summaries)
        audit_crew = Crew(agents=[audit_agent], tasks=[
                          audit_task], verbose=True)

        try:
            audit_result = run_crew(audit_crew)
            audit_text = crew_to_text(audit_result)
        except Exception as e:
            print(f"❌ Audit analysis failed for {tool_name}: {e}")
            report_sections.append(
                f"### {tool_name}\n"
                f"_Category: {category} • Users: {used_by} • Criticality: {criticality}_\n\n"
                f"**Summaries**\n" +
                "\n".join([f"- {s}" for s in summaries]) + "\n\n"
                f"**Audit Insights**\n> Error generating audit insights: {e}\n"
            )
            continue

        print("\n📊 Audit Insights:")
        print(audit_text)

        # 4) Integration opportunities (CrewAI agent)
        integration_agent = get_integration_agent(llm)
        integration_task = get_integration_task(
            integration_agent,
            firm_tools=firm_tools,
            focal_tool=tool_name,
            summaries=summaries,
            audit_text=audit_text,
        )
        integration_crew = Crew(agents=[integration_agent], tasks=[
                                integration_task], verbose=True)

        try:
            integration_result = run_crew(integration_crew)
            integration_text = crew_to_text(integration_result)
        except Exception as e:
            print(f"❌ Integration generation failed for {tool_name}: {e}")
            integration_text = f"> Error generating integration opportunities: {e}"

        print("\n🔗 Integration Opportunities:")
        print(integration_text)

        # 5) Compose Markdown section (either via Report Writer agent or manual)
        if use_report_writer:
            report_writer = get_report_writer_agent(llm)
            section_task = get_report_section_task(
                report_writer,
                tool_name=tool_name,
                category=category,
                used_by=used_by,
                criticality=criticality,
                summaries=summaries,
                audit_text=audit_text,
                integrations_text=integration_text,
            )
            section_crew = Crew(agents=[report_writer], tasks=[
                                section_task], verbose=False)
            try:
                section_result = run_crew(section_crew)
                section_md_text = crew_to_text(section_result)
                report_sections.append(section_md_text.strip() + "\n")
            except Exception as e:
                print(
                    f"⚠️ Report writer failed for {tool_name}: {e} (falling back to manual section)")
                section_md = []
                section_md.append(f"### {tool_name}")
                section_md.append(
                    f"_Category: {category} • Users: {used_by} • Criticality: {criticality}_\n"
                )
                section_md.append("**Summaries**")
                section_md.extend([f"- {s}" for s in summaries])
                section_md.append("\n**Audit Insights**")
                section_md.append(audit_text.strip())
                section_md.append("\n**Integration Opportunities**")
                section_md.append(integration_text.strip())
                report_sections.append("\n".join(section_md) + "\n")
        else:
            section_md = []
            section_md.append(f"### {tool_name}")
            section_md.append(
                f"_Category: {category} • Users: {used_by} • Criticality: {criticality}_\n"
            )
            section_md.append("**Summaries**")
            section_md.extend([f"- {s}" for s in summaries])
            section_md.append("\n**Audit Insights**")
            section_md.append(audit_text.strip())
            section_md.append("\n**Integration Opportunities**")
            section_md.append(integration_text.strip())
            report_sections.append("\n".join(section_md) + "\n")

    # 6) Write Markdown report
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = dedent(
        f"""\
    # Tech Stack Audit Report
    _Generated: {ts}_

    ---
    """
    )
    report_md = header + "\n".join(report_sections)
    out_path = output_dir / "audit_report.md"
    out_path.write_text(report_md, encoding="utf-8")

    print(f"\n✅ Done. Report saved to: {out_path.resolve()}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(1)

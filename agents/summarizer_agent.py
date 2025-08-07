# ROLE - accepts a tool name and the raw changelog entries from changelog_fetcher.py,
# summarizes each update for a business audience, and returns the summaries for the audit report

from crewai import Agent, Task

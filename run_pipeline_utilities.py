# run_pipeline.py
"""
Utility functions for running CrewAI crews and processing results
"""

import os
from langchain_openai import ChatOpenAI
from crewai import Crew

def get_llm():
    """Get configured LLM instance"""
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        temperature=0
    )

def run_crew(crew: Crew):
    """Run a CrewAI crew and return results"""
    try:
        result = crew.kickoff()
        return result
    except Exception as e:
        print(f"⚠️ Crew execution failed: {e}")
        return f"Crew execution failed: {str(e)}"

def crew_to_text(crew_result) -> str:
    """Convert crew result to text string"""
    if isinstance(crew_result, str):
        return crew_result
    elif hasattr(crew_result, 'raw'):
        return crew_result.raw
    elif hasattr(crew_result, 'result'):
        return crew_result.result
    else:
        return str(crew_result)

def parse_bullet_list(text: str) -> list:
    """Parse text into bullet point list"""
    lines = text.strip().split('\n')
    bullets = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('- ') or line.startswith('• '):
            bullets.append(line[2:].strip())
        elif line.startswith('* '):
            bullets.append(line[2:].strip())
        elif line and not any(char in line for char in ['#', '=', '-'*3]):
            # Non-header, non-separator lines
            bullets.append(line)
    
    return [b for b in bullets if b]  # Remove empty bullets
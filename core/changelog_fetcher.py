# Accepts a list of tool names, returns mocked changelog entries (simulations),
# and sets the stage for integrating real changelogs later

def fetch_mock_changelog(tool_name):
    """
    Return mocked changelog entries for a given tool
    Later, replace with real API/web-scraped data

    """

    mock_changelog = {
        "Zoom": [
            {"date": "2024-12-25", "title": "AI Companion Enhancements",
                "description": "Added post-meeting summaries and smart meeting highlights."},
            {"date": "2025-3-1", "title": "Outlook Calendar Sync",
                "description": "Improved integration with Outlook for cross-platform invites."},
        ],

        "365": [
            {"date": "2025-1-22", "title": "Copilot Integration",
                "description": "Copilt is now fully embedded in Word and Excel for summarization and automation."}
        ],

        "Bloomberg": [
            {"date": "2024-11-5", "title": "Terminal Chat Upgrade",
                "description": "Improved NLP-based query suggestions and portfolio tagging."}
        ],

        "FactSet": [
            {"date": "2025-2-12", "title": "New ESG Scoring Model",
                "description": "Added detailed ESG metrics sourced from new global dataset."}
        ],
    }
    return mock_changelog.get(tool_name, [])

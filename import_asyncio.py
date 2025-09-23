import asyncio
from core.discovery_engine import analyze_tool_stack_versions


async def test_complete_version_analysis():
    # Test with a simple tool inventory
    test_tools = {
        "Zoom": {"category": "Video", "users": ["All"], "criticality": "Medium"},
        "Slack": {"category": "Communication", "users": ["All"], "criticality": "High"}
    }

    # Run complete version analysis
    results = await analyze_tool_stack_versions(test_tools)

    # Print results
    for tool_name, tool_data in results.items():
        version_info = tool_data['version_analysis']
        print(f"\n{tool_name}:")
        print(f"  Current: {version_info['current_version']}")
        print(f"  Latest: {version_info['latest_version']}")
        print(f"  Status: {version_info['comparison']['status']}")

# Run the test
asyncio.run(test_complete_version_analysis())

"""
Test script for feature detection - run this from the main project folder
"""
from core.discovery_engine import DiscoveryEngine
import asyncio
import sys
from pathlib import Path

# Add the project root to Python's path so it can find the core module
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_feature_detection():
    """Test the new feature detection capability"""
    print("🧪 Testing Feature Detection\n")

    engine = DiscoveryEngine()

    # Test with a few different tools
    test_tools = ["FactSet", "Microsoft 365", "Zoom", "Bloomberg"]

    for tool in test_tools:
        print(f"\n{'='*60}")
        result = await engine.detect_recent_automation_features(tool)

        print(f"\n📊 Results for {tool}:")
        print(f"   Features Found: {result['features_found']}")

        if result['features_found'] > 0:
            print(f"\n   Recent Automation Features:")
            for i, feature in enumerate(result['recent_features'], 1):
                print(f"\n   {i}. {feature['name']}")
                print(f"      Added: {feature['added']}")
                print(f"      Value: {feature['automation_value']}")
                print(f"      Impact: {feature['business_impact']}")
        else:
            print(f"   {result['summary']}")

if __name__ == "__main__":
    asyncio.run(test_feature_detection())

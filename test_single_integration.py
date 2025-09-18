# test_single_integration.py
"""Test a single integration assessment to debug the issue"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from core.integration_health_checker import IntegrationHealthChecker

async def test_single_assessment():
    """Test a single integration assessment"""
    print("🧪 Testing single integration assessment...")
    
    try:
        checker = IntegrationHealthChecker()
        print("✅ IntegrationHealthChecker created")
        
        # Test a simple assessment
        result = await checker.assess_integration_health("Advent Axys", "365")
        print(f"✅ Assessment completed: {result.status}")
        print(f"   Health Score: {result.health_score}")
        print(f"   Issues: {len(result.issues_found)}")
        
    except Exception as e:
        print(f"❌ Test failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_single_assessment())

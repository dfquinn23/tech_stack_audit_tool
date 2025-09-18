# debug_integration_exceptions.py
"""
Debug what's actually causing the integration assessment exceptions
Modify the exception handler to show the actual error details
"""

from pathlib import Path

def add_detailed_exception_logging():
    """Add detailed exception logging to see what's actually failing"""
    
    print("🔍 ADDING DETAILED EXCEPTION LOGGING")
    print("=" * 50)
    
    integration_file = Path("core/integration_health_checker.py")
    if not integration_file.exists():
        print("❌ integration_health_checker.py not found")
        return False
    
    with open(integration_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the current exception handler and make it more verbose
    old_exception_handler = '''        except Exception as e:
            print(f"   ❌ Integration assessment failed for {source_tool} → {target_tool}: {str(e)}")
            # Return a basic failed assessment instead of raising exception
            return IntegrationAssessment('''
    
    new_exception_handler = '''        except Exception as e:
            print(f"   ❌ Integration assessment failed for {source_tool} → {target_tool}")
            print(f"   🐛 Exception type: {type(e).__name__}")
            print(f"   🐛 Exception details: {str(e)}")
            import traceback
            print(f"   🐛 Stack trace: {traceback.format_exc()}")
            # Return a basic failed assessment instead of raising exception
            return IntegrationAssessment('''
    
    if old_exception_handler in content:
        content = content.replace(old_exception_handler, new_exception_handler)
        print("   ✅ Added detailed exception logging")
        
        with open(integration_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    else:
        print("   ❌ Could not find exception handler to modify")
        return False

def test_single_integration_assessment():
    """Test a single integration assessment to see what fails"""
    
    print("🧪 TESTING SINGLE INTEGRATION ASSESSMENT")
    print("=" * 50)
    
    # Create a simple test script
    test_script = '''# test_single_integration.py
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
'''
    
    test_file = Path("test_single_integration.py")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ Created test_single_integration.py")
    print("   Run: python test_single_integration.py")
    return True

def simplify_integration_assessment():
    """Simplify the integration assessment to avoid complex operations that might fail"""
    
    print("🔧 SIMPLIFYING INTEGRATION ASSESSMENT")
    print("=" * 50)
    
    integration_file = Path("core/integration_health_checker.py")
    if not integration_file.exists():
        return False
    
    with open(integration_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the assess_integration_health method and create a simplified version
    # that skips complex operations that might be failing
    
    # Comment out API health checks temporarily
    old_api_check = '''        # Perform API health checks where possible
        await self._perform_api_health_checks(assessment)'''
    
    new_api_check = '''        # Perform API health checks where possible (TEMPORARILY DISABLED FOR DEBUGGING)
        # await self._perform_api_health_checks(assessment)
        print(f"   🔧 Skipping API health checks for debugging")'''
    
    if old_api_check in content:
        content = content.replace(old_api_check, new_api_check)
        print("   ✅ Temporarily disabled API health checks")
    
    # Comment out caching temporarily
    old_cache_save = '''        # Cache the result
        self._save_cache(cache_key, assessment.__dict__)'''
    
    new_cache_save = '''        # Cache the result (TEMPORARILY DISABLED FOR DEBUGGING)
        # self._save_cache(cache_key, assessment.__dict__)
        print(f"   🔧 Skipping cache save for debugging")'''
    
    if old_cache_save in content:
        content = content.replace(old_cache_save, new_cache_save)
        print("   ✅ Temporarily disabled cache saving")
    
    with open(integration_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    """Add debugging and simplify to isolate the issue"""
    
    print("🚀 DEBUGGING INTEGRATION ASSESSMENT FAILURES")
    print("=" * 60)
    
    # Step 1: Add detailed exception logging
    if add_detailed_exception_logging():
        print("✅ Added detailed exception logging")
    
    # Step 2: Simplify the assessment to avoid complex operations
    if simplify_integration_assessment():
        print("✅ Simplified integration assessment for debugging")
    
    # Step 3: Create a single integration test
    if test_single_integration_assessment():
        print("✅ Created single integration test")
    
    print(f"\n{'='*60}")
    print("🎉 DEBUGGING SETUP COMPLETED!")
    print("\n🧪 Next steps:")
    print("   1. Run your audit again to see detailed error messages")
    print("   2. OR run: python test_single_integration.py")
    print("   3. Share the detailed error output so we can identify the root cause")
    
    print("\n🔍 What to look for:")
    print("   • Exception type and details will now be shown")
    print("   • Stack trace will show exactly where it's failing")
    print("   • Complex operations temporarily disabled")

if __name__ == "__main__":
    main()

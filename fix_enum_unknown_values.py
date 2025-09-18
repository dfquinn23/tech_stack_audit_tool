# fix_enum_unknown_values.py
"""
Fix the AttributeError: UNKNOWN issue
The problem is that IntegrationType and IntegrationStatus enums don't have UNKNOWN values
"""

from pathlib import Path

def fix_enum_definitions():
    """Add UNKNOWN values to the enums that are missing them"""
    
    print("🔧 FIXING ENUM UNKNOWN VALUES")
    print("=" * 40)
    
    integration_file = Path("core/integration_health_checker.py")
    if not integration_file.exists():
        print("❌ integration_health_checker.py not found")
        return False
    
    with open(integration_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix IntegrationStatus enum - add UNKNOWN if missing
    old_integration_status = '''class IntegrationStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    BROKEN = "broken"
    MISSING = "missing"
    UNKNOWN = "unknown"'''
    
    # Check if UNKNOWN is missing from IntegrationStatus
    if "UNKNOWN = \"unknown\"" not in content:
        print("   🔧 IntegrationStatus is missing UNKNOWN value")
        
        # Find IntegrationStatus enum and add UNKNOWN
        integration_status_pattern = '''class IntegrationStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    BROKEN = "broken"
    MISSING = "missing"'''
        
        new_integration_status = '''class IntegrationStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    BROKEN = "broken"
    MISSING = "missing"
    UNKNOWN = "unknown"'''
        
        if integration_status_pattern in content:
            content = content.replace(integration_status_pattern, new_integration_status)
            print("   ✅ Added UNKNOWN to IntegrationStatus enum")
    else:
        print("   ✅ IntegrationStatus already has UNKNOWN value")
    
    # Fix IntegrationType enum - add UNKNOWN if missing
    # Check if UNKNOWN is missing from IntegrationType
    if 'IntegrationType' in content and 'UNKNOWN = "unknown"' not in content.split('class IntegrationType')[1].split('class ')[0]:
        print("   🔧 IntegrationType is missing UNKNOWN value")
        
        # Find IntegrationType enum and add UNKNOWN
        integration_type_pattern = '''class IntegrationType(Enum):
    API = "api"
    WEBHOOK = "webhook"
    DATABASE = "database"
    FILE_SYNC = "file_sync"
    EMAIL_SYNC = "email_sync"
    CALENDAR_SYNC = "calendar_sync"
    SSO = "sso"
    MANUAL = "manual"
    NONE = "none"'''
        
        new_integration_type = '''class IntegrationType(Enum):
    API = "api"
    WEBHOOK = "webhook"
    DATABASE = "database"
    FILE_SYNC = "file_sync"
    EMAIL_SYNC = "email_sync"
    CALENDAR_SYNC = "calendar_sync"
    SSO = "sso"
    MANUAL = "manual"
    NONE = "none"
    UNKNOWN = "unknown"'''
        
        if integration_type_pattern in content:
            content = content.replace(integration_type_pattern, new_integration_type)
            print("   ✅ Added UNKNOWN to IntegrationType enum")
        else:
            # Alternative pattern - try to find and fix
            if "NONE = \"none\"" in content and "UNKNOWN = \"unknown\"" not in content:
                content = content.replace("NONE = \"none\"", "NONE = \"none\"\n    UNKNOWN = \"unknown\"")
                print("   ✅ Added UNKNOWN to IntegrationType enum (alternative method)")
    else:
        print("   ✅ IntegrationType already has UNKNOWN value or not found")
    
    # Write the fixed content back
    with open(integration_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def test_enum_fix():
    """Test that the enum fix works"""
    
    print("🧪 TESTING ENUM FIX")
    print("=" * 30)
    
    test_script = '''# test_enum_fix.py
"""Test that the enum fix works"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.append(str(project_root))

try:
    from core.integration_health_checker import IntegrationStatus, IntegrationType
    
    print("🧪 Testing enum values...")
    
    # Test IntegrationStatus.UNKNOWN
    try:
        status = IntegrationStatus.UNKNOWN
        print(f"✅ IntegrationStatus.UNKNOWN = {status.value}")
    except AttributeError:
        print("❌ IntegrationStatus.UNKNOWN not found")
    
    # Test IntegrationType.UNKNOWN
    try:
        int_type = IntegrationType.UNKNOWN
        print(f"✅ IntegrationType.UNKNOWN = {int_type.value}")
    except AttributeError:
        print("❌ IntegrationType.UNKNOWN not found")
    
    print("✅ Enum test completed")
    
except Exception as e:
    print(f"❌ Enum test failed: {e}")
'''
    
    test_file = Path("test_enum_fix.py")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ Created test_enum_fix.py")
    print("   Run: python test_enum_fix.py")
    return True

def main():
    """Fix the enum UNKNOWN values issue"""
    
    print("🚀 FIXING ENUM UNKNOWN VALUES ISSUE")
    print("=" * 50)
    
    # Fix 1: Add UNKNOWN values to enums
    if fix_enum_definitions():
        print("✅ Enum definitions fixed")
    
    # Fix 2: Create test to verify the fix
    if test_enum_fix():
        print("✅ Test script created")
    
    print(f"\n{'='*50}")
    print("🎉 ENUM FIX COMPLETED!")
    print("\n🧪 Next steps:")
    print("   1. Run: python test_enum_fix.py (to verify enums work)")
    print("   2. Run: python test_single_integration.py (to test integration)")
    print("   3. Run your full audit (should now work!)")
    
    print("\n🔍 What this fixed:")
    print("   • Added UNKNOWN values to IntegrationStatus and IntegrationType enums")
    print("   • This should resolve the AttributeError: UNKNOWN issue")

if __name__ == "__main__":
    main()

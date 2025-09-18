# test_enum_fix.py
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

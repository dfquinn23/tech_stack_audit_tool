#!/usr/bin/env python3
"""
Complete import fix and validation for Tech Stack Audit Tool
Fixes missing AuditStage import and validates the fix
"""

import sys
from pathlib import Path

def fix_missing_auditstage_import():
    """Fix the missing AuditStage import in enhanced_run_pipeline_day2.py"""
    
    pipeline_file = Path("enhanced_run_pipeline_day2.py")
    if not pipeline_file.exists():
        print("❌ enhanced_run_pipeline_day2.py not found")
        return False
    
    print("🔧 Fixing missing AuditStage import...")
    
    # Read the current file
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if AuditStage is already imported correctly
    if "from core.stage_gate_manager import" in content and "AuditStage" in content:
        print("   ✅ AuditStage already imported correctly")
        return True
    
    # Look for existing imports to modify
    import_patterns = [
        "from core.stage_gate_manager import StageGateManager, create_audit_session, load_audit_session",
        "from core.stage_gate_manager import StageGateManager, create_audit_session",
        "from core.stage_gate_manager import StageGateManager"
    ]
    
    fixed = False
    for pattern in import_patterns:
        if pattern in content:
            # Add AuditStage to the existing import
            new_import = pattern + ", AuditStage"
            content = content.replace(pattern, new_import)
            print(f"   ✅ Added AuditStage to existing import: {pattern[:40]}...")
            fixed = True
            break
    
    if not fixed:
        # Add new import line after existing imports
        import_lines = [
            "import asyncio",
            "import pandas as pd",
            "from datetime import datetime"
        ]
        
        for import_line in import_lines:
            if import_line in content:
                # Find the position after this import
                pos = content.find(import_line)
                if pos != -1:
                    # Find the end of this line
                    end_pos = content.find('\n', pos)
                    if end_pos != -1:
                        # Insert the new import after this line
                        new_import = "\nfrom core.stage_gate_manager import AuditStage"
                        content = content[:end_pos] + new_import + content[end_pos:]
                        print("   ✅ Added new AuditStage import line")
                        fixed = True
                        break
    
    if not fixed:
        print("   ⚠️ Could not automatically fix import - manual intervention needed")
        return False
    
    # Write the fixed content back
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def test_imports_after_fix():
    """Test that imports work after the fix"""
    print("\n🧪 Testing imports after fix...")
    
    try:
        # Test core imports
        from core.stage_gate_manager import StageGateManager, AuditStage, create_audit_session
        print("   ✅ Core imports: StageGateManager, AuditStage")
        
        # Test pipeline import
        from enhanced_run_pipeline_day2 import EnhancedAuditPipelineDay2
        print("   ✅ Enhanced pipeline imports successfully")
        
        # Test basic functionality
        test_manager = create_audit_session("Test Client")
        stage = AuditStage.DISCOVERY
        print(f"   ✅ AuditStage enum works: {stage.name}")
        
        # Clean up
        if test_manager.state_file.exists():
            test_manager.state_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import test failed: {e}")
        return False

def main():
    """Fix imports and validate"""
    print("🚀 COMPLETE IMPORT FIX AND VALIDATION")
    print("=" * 50)
    
    # Step 1: Fix the import
    print("\n📝 Step 1: Fix Missing Import")
    if not fix_missing_auditstage_import():
        print("❌ Import fix failed")
        return False
    
    # Step 2: Test the fix
    print("\n🧪 Step 2: Validate Fix")
    if not test_imports_after_fix():
        print("❌ Import validation failed")
        return False
    
    # Step 3: Success message
    print("\n" + "=" * 50)
    print("🎉 IMPORT FIX COMPLETED SUCCESSFULLY!")
    print("✅ AuditStage import fixed")
    print("✅ All imports validated")
    print("✅ Basic functionality tested")
    
    print("\n🚀 Next Steps:")
    print("   python final_validation_test.py    # Run full system validation")
    print("   python test_complete_system.py     # Alternative comprehensive test")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Fix the validation test AuditStage import issue
"""

from pathlib import Path

def fix_validation_test_import():
    """Fix the AuditStage import in final_validation_test.py"""
    
    validation_file = Path("final_validation_test.py")
    if not validation_file.exists():
        print("❌ final_validation_test.py not found")
        return False
    
    print("🔧 Fixing validation test imports...")
    
    with open(validation_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for existing stage_gate_manager imports
    if "from core.stage_gate_manager import" in content:
        # Find the import line and add AuditStage if missing
        import_line_start = content.find("from core.stage_gate_manager import")
        import_line_end = content.find("\n", import_line_start)
        
        if import_line_end != -1:
            current_import = content[import_line_start:import_line_end]
            print(f"Current import: {current_import}")
            
            if "AuditStage" not in current_import:
                new_import = current_import + ", AuditStage"
                content = content.replace(current_import, new_import)
                print("✅ Added AuditStage to validation test imports")
            else:
                print("✅ AuditStage already in validation test imports")
    else:
        # Add the import line after other imports
        # Look for a good place to insert it
        if "import asyncio" in content:
            insert_pos = content.find("import asyncio")
            insert_pos = content.find("\n", insert_pos) + 1
            new_import = "from core.stage_gate_manager import AuditStage\n"
            content = content[:insert_pos] + new_import + content[insert_pos:]
            print("✅ Added new AuditStage import to validation test")
    
    # Write the fixed content back
    with open(validation_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def check_where_auditstage_used_in_validation():
    """Find where AuditStage is used in the validation test"""
    
    validation_file = Path("final_validation_test.py")
    if not validation_file.exists():
        return
    
    print("\n🔍 Checking AuditStage usage in validation test...")
    
    with open(validation_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        if 'AuditStage' in line:
            print(f"   Line {i}: {line.strip()}")

def test_validation_fix():
    """Test that the validation fix works"""
    
    print("\n🧪 Testing validation fix...")
    
    try:
        # Try to run the key parts that might use AuditStage
        from core.stage_gate_manager import create_audit_session, AuditStage
        
        # Create a test manager
        manager = create_audit_session("Validation Fix Test")
        
        # Test stage comparisons that might be in the validation
        stage_checks = [
            manager.state.current_stage == AuditStage.DISCOVERY,
            manager.state.current_stage != AuditStage.ASSESSMENT,
            AuditStage.OPPORTUNITIES,
            AuditStage.DELIVERY
        ]
        
        print("✅ All AuditStage operations work")
        
        # Clean up
        if manager.state_file.exists():
            manager.state_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Validation fix test failed: {e}")
        return False

def main():
    """Fix validation test and verify"""
    
    print("🎯 FIXING VALIDATION TEST")
    print("=" * 40)
    
    # Check current usage
    check_where_auditstage_used_in_validation()
    
    # Apply fix
    if fix_validation_test_import():
        # Test the fix
        if test_validation_fix():
            print("\n🎉 VALIDATION TEST FIXED!")
            print("Now run: python final_validation_test.py")
        else:
            print("\n⚠️ Fix applied but test failed")
    else:
        print("\n❌ Could not apply fix")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Immediate fix for AuditStage import issue
Simple, direct fix that will work immediately
"""

from pathlib import Path

def fix_now():
    """Apply immediate fix to the import issue"""
    
    pipeline_file = Path("enhanced_run_pipeline_day2.py")
    
    if not pipeline_file.exists():
        print("❌ enhanced_run_pipeline_day2.py not found")
        return False
    
    print("🔧 Applying immediate fix...")
    
    # Read the file
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple string replacement to add AuditStage import
    # Look for the stage_gate_manager import line and add AuditStage
    
    old_imports = [
        "from core.stage_gate_manager import StageGateManager, create_audit_session, load_audit_session",
        "from core.stage_gate_manager import StageGateManager, create_audit_session",
        "from core.stage_gate_manager import StageGateManager"
    ]
    
    fixed = False
    for old_import in old_imports:
        if old_import in content and ", AuditStage" not in old_import:
            new_import = old_import + ", AuditStage"
            content = content.replace(old_import, new_import)
            print(f"✅ Fixed import: Added AuditStage")
            fixed = True
            break
    
    if not fixed:
        # If no existing import found, add it after the first import
        first_import_pos = content.find("from core.stage_gate_manager import")
        if first_import_pos != -1:
            # Find the end of this line
            line_end = content.find("\n", first_import_pos)
            if line_end != -1:
                # Add AuditStage import on next line
                new_import_line = "from core.stage_gate_manager import AuditStage\n"
                content = content[:line_end+1] + new_import_line + content[line_end+1:]
                print("✅ Added new AuditStage import line")
                fixed = True
    
    if not fixed:
        print("❌ Could not find import to fix")
        return False
    
    # Write back the fixed content
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ File updated successfully")
    return True

def verify_fix():
    """Verify the fix worked"""
    print("\n🧪 Verifying fix...")
    
    try:
        # Test the import
        exec("from enhanced_run_pipeline_day2 import EnhancedAuditPipelineDay2")
        print("✅ Enhanced pipeline imports successfully")
        return True
    except Exception as e:
        print(f"❌ Import still failing: {e}")
        return False

if __name__ == "__main__":
    print("⚡ IMMEDIATE AUDITSTAGE IMPORT FIX")
    print("=" * 40)
    
    if fix_now():
        if verify_fix():
            print("\n🎉 FIX SUCCESSFUL!")
            print("Now run: python final_validation_test.py")
        else:
            print("\n⚠️ Fix applied but still having issues")
    else:
        print("\n❌ Fix failed")

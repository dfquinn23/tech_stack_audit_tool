# patch_enhanced_pipeline.py
"""
Quick patch to fix the EnhancedAuditStateTool in the pipeline
Run this to apply the fix
"""

import sys
from pathlib import Path

def patch_pipeline_file():
    """Fix the EnhancedAuditStateTool class definition"""
    
    pipeline_file = Path("enhanced_run_pipeline_day2.py")
    if not pipeline_file.exists():
        # Check if the old name exists
        old_pipeline_file = Path("enhanced_pipeline_with_stage_gates.py")
        if old_pipeline_file.exists():
            print("🔧 Renaming enhanced_pipeline_with_stage_gates.py to enhanced_run_pipeline_day2.py")
            old_pipeline_file.rename(pipeline_file)
        else:
            print("❌ No pipeline file found")
            return False
    
    print("🔧 Patching EnhancedAuditStateTool...")
    
    # Read the current file
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the problematic tool class constructor
    old_constructor = '''def __init__(self, stage_manager: StageGateManager, 
                 health_checker: IntegrationHealthChecker = None,
                 gap_analyzer: IntegrationGapAnalyzer = None):
        super().__init__()
        self.stage_manager = stage_manager
        self.health_checker = health_checker or IntegrationHealthChecker()
        self.gap_analyzer = gap_analyzer or IntegrationGapAnalyzer()'''
    
    new_constructor = '''def __init__(self, stage_manager: StageGateManager, 
                 health_checker: IntegrationHealthChecker = None,
                 gap_analyzer: IntegrationGapAnalyzer = None):
        super().__init__()
        # Store as instance variables instead of trying to use field declarations
        self._stage_manager = stage_manager
        self._health_checker = health_checker or IntegrationHealthChecker()
        self._gap_analyzer = gap_analyzer or IntegrationGapAnalyzer()'''
    
    # Replace the constructor
    if old_constructor in content:
        content = content.replace(old_constructor, new_constructor)
        print("   ✅ Fixed constructor")
    
    # Fix all method references
    replacements = [
        ("self.stage_manager.state.tool_inventory", "self._stage_manager.state.tool_inventory"),
        ("self.stage_manager.state.integrations", "self._stage_manager.state.integrations"), 
        ("self.stage_manager.add_integration", "self._stage_manager.add_integration"),
        ("self.stage_manager.state", "self._stage_manager.state"),
        ("self.stage_manager.audit_id", "self._stage_manager.audit_id"),
        ("self.health_checker", "self._health_checker"),
        ("self.gap_analyzer", "self._gap_analyzer"),
    ]
    
    changes_made = 0
    for old_ref, new_ref in replacements:
        if old_ref in content:
            content = content.replace(old_ref, new_ref)
            changes_made += 1
    
    print(f"   ✅ Fixed {changes_made} method references")
    
    # Write the fixed content back
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Enhanced pipeline patched successfully")
    return True

if __name__ == "__main__":
    if patch_pipeline_file():
        print("✅ Patch completed successfully")
        print("Now run: python test_simple_system.py")
    else:
        print("❌ Patch failed")
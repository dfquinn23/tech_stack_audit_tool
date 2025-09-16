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
        print("❌ enhanced_run_pipeline_day2.py not found")
        return False
    
    print("🔧 Patching EnhancedAuditStateTool...")
    
    # Read the current file
    with open(pipeline_file, 'r') as f:
        content = f.read()
    
    # Replace the problematic tool class
    old_tool_class = '''class EnhancedAuditStateTool(BaseTool):
    """Enhanced CrewAI tool with Day 2 integration assessment capabilities"""
    name: str = "Enhanced Audit State Manager"
    description: str = "Access audit state, integration assessments, and gap analysis across pipeline stages"
    
    def __init__(self, stage_manager: StageGateManager, 
                 health_checker: IntegrationHealthChecker = None,
                 gap_analyzer: IntegrationGapAnalyzer = None):
        super().__init__()
        self.stage_manager = stage_manager
        self.health_checker = health_checker or IntegrationHealthChecker()
        self.gap_analyzer = gap_analyzer or IntegrationGapAnalyzer()'''
    
    new_tool_class = '''class EnhancedAuditStateTool(BaseTool):
    """Enhanced CrewAI tool with Day 2 integration assessment capabilities"""
    name: str = "Enhanced Audit State Manager"
    description: str = "Access audit state, integration assessments, and gap analysis across pipeline stages"
    
    def __init__(self, stage_manager: StageGateManager, 
                 health_checker: IntegrationHealthChecker = None,
                 gap_analyzer: IntegrationGapAnalyzer = None):
        super().__init__()
        # Store as instance variables instead of trying to use field declarations
        self._stage_manager = stage_manager
        self._health_checker = health_checker or IntegrationHealthChecker()
        self._gap_analyzer = gap_analyzer or IntegrationGapAnalyzer()'''
    
    # Also fix the method references
    old_method_refs = [
        "self.stage_manager.state.tool_inventory",
        "self.stage_manager.state.integrations", 
        "self.stage_manager.add_integration",
        "self.stage_manager.state",
    ]
    
    new_method_refs = [
        "self._stage_manager.state.tool_inventory",
        "self._stage_manager.state.integrations",
        "self._stage_manager.add_integration", 
        "self._stage_manager.state",
    ]
    
    # Apply the fixes
    if old_tool_class in content:
        content = content.replace(old_tool_class, new_tool_class)
        
        # Fix method references
        for old_ref, new_ref in zip(old_method_refs, new_method_refs):
            content = content.replace(old_ref, new_ref)
        
        # Write the fixed content back
        with open(pipeline_file, 'w') as f:
            f.write(content)
        
        print("✅ Enhanced pipeline patched successfully")
        return True
    else:
        print("⚠️ Patch not needed or content not found")
        return True

if __name__ == "__main__":
    if patch_pipeline_file():
        print("✅ Patch completed successfully")
        print("Now run: python test_simple_system.py")
    else:
        print("❌ Patch failed")

# fix_stage_manager_references.py
"""
Fix all _stage_manager references in the enhanced pipeline
The issue is mixing self.stage_manager and self._stage_manager
"""

import re
from pathlib import Path

def fix_pipeline_references():
    """Fix all _stage_manager references in the pipeline"""
    
    pipeline_file = Path("enhanced_run_pipeline_day2.py")
    if not pipeline_file.exists():
        print("❌ enhanced_run_pipeline_day2.py not found")
        return False
    
    print("🔧 Fixing stage_manager references...")
    
    # Read the current file
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The issue is that in EnhancedAuditPipelineDay2 class, 
    # the attribute is created as self.stage_manager but referenced as self._stage_manager
    
    # In the __init__ method of EnhancedAuditPipelineDay2, it creates self.stage_manager
    # But later it tries to access self._stage_manager
    
    # Fix all references in the EnhancedAuditPipelineDay2 class
    # We need to be careful to only fix the ones in this class, not in EnhancedAuditStateTool
    
    # Find and replace the incorrect references
    # Look for the print statements and method calls that use self._stage_manager
    # in the EnhancedAuditPipelineDay2 class context
    
    fixes = [
        # These are in EnhancedAuditPipelineDay2.__init__
        ('print(f"   Audit ID: {self._stage_manager.audit_id}")', 
         'print(f"   Audit ID: {self.stage_manager.audit_id}")'),
        ('print(f"   Client: {self._stage_manager.state.client_name}")', 
         'print(f"   Client: {self.stage_manager.state.client_name}")'),
        ('print(f"   Current Stage: {self._stage_manager.state.current_stage.name}")', 
         'print(f"   Current Stage: {self.stage_manager.state.current_stage.name}")'),
        
        # These are in various methods of EnhancedAuditPipelineDay2
        ('if self._stage_manager.state.current_stage != AuditStage.DISCOVERY:', 
         'if self.stage_manager.state.current_stage != AuditStage.DISCOVERY:'),
        ('if self._stage_manager.state.current_stage != AuditStage.ASSESSMENT:', 
         'if self.stage_manager.state.current_stage != AuditStage.ASSESSMENT:'),
        ('if self._stage_manager.state.current_stage != AuditStage.OPPORTUNITIES:', 
         'if self.stage_manager.state.current_stage != AuditStage.OPPORTUNITIES:'),
        ('if self._stage_manager.state.current_stage != AuditStage.DELIVERY:', 
         'if self.stage_manager.state.current_stage != AuditStage.DELIVERY:'),
        
        # Other references that might exist
        ('self._stage_manager.state.client_domain', 'self.stage_manager.state.client_domain'),
        ('self._stage_manager.state.tool_inventory', 'self.stage_manager.state.tool_inventory'),
        ('self._stage_manager.state.integrations', 'self.stage_manager.state.integrations'),
        ('self._stage_manager.add_integration', 'self.stage_manager.add_integration'),
        ('self._stage_manager.audit_id', 'self.stage_manager.audit_id'),
        
        # Stage gate checks
        ('self._stage_manager.state.__dict__', 'self.stage_manager.state.__dict__'),
        ('len(self._stage_manager.state.tool_inventory)', 'len(self.stage_manager.state.tool_inventory)'),
        ('len(self._stage_manager.state.integrations)', 'len(self.stage_manager.state.integrations)'),
        ('len(self._stage_manager.state.automation_opportunities)', 'len(self.stage_manager.state.automation_opportunities)'),
        
        # Any other _stage_manager references that should be stage_manager in EnhancedAuditPipelineDay2
    ]
    
    changes_made = 0
    original_content = content
    
    for old_text, new_text in fixes:
        if old_text in content:
            content = content.replace(old_text, new_text)
            changes_made += 1
            print(f"   ✅ Fixed: {old_text[:50]}...")
    
    # Additional pattern-based fixes for any remaining _stage_manager in the class
    # But be careful not to change the ones in EnhancedAuditStateTool class
    # We'll use a more targeted approach
    
    # Look for lines that have self._stage_manager but are NOT in the EnhancedAuditStateTool class
    lines = content.split('\n')
    in_enhanced_audit_state_tool = False
    in_enhanced_audit_pipeline = False
    
    for i, line in enumerate(lines):
        # Track which class we're in
        if 'class EnhancedAuditStateTool' in line:
            in_enhanced_audit_state_tool = True
            in_enhanced_audit_pipeline = False
        elif 'class EnhancedAuditPipelineDay2' in line:
            in_enhanced_audit_state_tool = False
            in_enhanced_audit_pipeline = True
        elif line.startswith('class ') and 'EnhancedAudit' not in line:
            in_enhanced_audit_state_tool = False
            in_enhanced_audit_pipeline = False
        
        # If we're in EnhancedAuditPipelineDay2 class and find self._stage_manager, fix it
        if in_enhanced_audit_pipeline and 'self._stage_manager' in line and not in_enhanced_audit_state_tool:
            old_line = line
            new_line = line.replace('self._stage_manager', 'self.stage_manager')
            if old_line != new_line:
                lines[i] = new_line
                changes_made += 1
                print(f"   ✅ Fixed line: self._stage_manager → self.stage_manager")
    
    content = '\n'.join(lines)
    
    # Only write if we made changes
    if content != original_content:
        with open(pipeline_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✅ Applied {changes_made} fixes")
        return True
    else:
        print("   ⚠️ No changes needed")
        return True

if __name__ == "__main__":
    if fix_pipeline_references():
        print("✅ Stage manager references fixed!")
        print("Now run: python test_complete_system.py")
    else:
        print("❌ Fix failed")
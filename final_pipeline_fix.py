# final_pipeline_fix.py
"""
Final fix for EnhancedAuditPipelineDay2 _stage_manager references
"""

import sys
from pathlib import Path

def fix_pipeline_references():
    """Fix all remaining _stage_manager references in the pipeline"""
    
    pipeline_file = Path("enhanced_run_pipeline_day2.py")
    if not pipeline_file.exists():
        print("❌ enhanced_run_pipeline_day2.py not found")
        return False
    
    print("🔧 Fixing all _stage_manager references...")
    
    # Read the current file
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix ALL references to _stage_manager that should be stage_manager
    replacements = [
        ("self._stage_manager", "self.stage_manager"),
        ("self._health_checker", "self.health_checker"), 
        ("self._gap_analyzer", "self.gap_analyzer"),
    ]
    
    changes_made = 0
    for old_ref, new_ref in replacements:
        if old_ref in content:
            content = content.replace(old_ref, new_ref)
            changes_made += 1
    
    print(f"   ✅ Fixed {changes_made} references")
    
    # Also fix the constructor to use regular attributes instead of underscore ones
    old_constructor = '''# Store as instance variables instead of trying to use field declarations
        self._stage_manager = stage_manager
        self._health_checker = health_checker or IntegrationHealthChecker()
        self._gap_analyzer = gap_analyzer or IntegrationGapAnalyzer()'''
    
    new_constructor = '''# Store as instance variables 
        self.stage_manager = stage_manager
        self.health_checker = health_checker or IntegrationHealthChecker()
        self.gap_analyzer = gap_analyzer or IntegrationGapAnalyzer()'''
    
    if old_constructor in content:
        content = content.replace(old_constructor, new_constructor)
        print("   ✅ Fixed constructor to use regular attributes")
    
    # Write the fixed content back
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ All pipeline references fixed")
    return True

if __name__ == "__main__":
    if fix_pipeline_references():
        print("✅ Fix completed successfully")
        print("Now run: python test_complete_system.py")
    else:
        print("❌ Fix failed")
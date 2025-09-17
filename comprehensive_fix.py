#!/usr/bin/env python3
"""
Comprehensive fix for AuditStage issues
Finds all occurrences and ensures proper imports everywhere
"""

import re
from pathlib import Path

def analyze_auditstage_usage():
    """Analyze where AuditStage is used in the pipeline"""
    
    pipeline_file = Path("enhanced_run_pipeline_day2.py")
    if not pipeline_file.exists():
        print("❌ enhanced_run_pipeline_day2.py not found")
        return False
    
    print("🔍 Analyzing AuditStage usage...")
    
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    auditstage_lines = []
    for i, line in enumerate(lines, 1):
        if 'AuditStage' in line:
            auditstage_lines.append((i, line.strip()))
    
    print(f"Found {len(auditstage_lines)} lines using AuditStage:")
    for line_num, line in auditstage_lines:
        print(f"   Line {line_num}: {line}")
    
    return auditstage_lines

def fix_all_imports():
    """Fix all import and usage issues"""
    
    pipeline_file = Path("enhanced_run_pipeline_day2.py")
    
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n🔧 Applying comprehensive fix...")
    
    # Ensure AuditStage is imported at the top
    if "from core.stage_gate_manager import" in content:
        # Find the import line
        import_match = re.search(r'from core\.stage_gate_manager import ([^\n]+)', content)
        if import_match:
            current_imports = import_match.group(1)
            if "AuditStage" not in current_imports:
                new_imports = current_imports + ", AuditStage"
                content = content.replace(
                    f"from core.stage_gate_manager import {current_imports}",
                    f"from core.stage_gate_manager import {new_imports}"
                )
                print("✅ Added AuditStage to imports")
    
    # Look for any method where AuditStage is used and ensure it's accessible
    # The issue might be in a method where self.stage_manager is accessed
    
    # Check if there are any bare AuditStage references that need to be qualified
    auditstage_pattern = r'(?<![\w.])AuditStage\.(\w+)'
    matches = re.findall(auditstage_pattern, content)
    
    if matches:
        print(f"Found {len(matches)} AuditStage enum references:")
        for match in set(matches):
            print(f"   AuditStage.{match}")
    
    # Special check for the validation test - the error might be in the test file itself
    validation_file = Path("final_validation_test.py")
    if validation_file.exists():
        with open(validation_file, 'r', encoding='utf-8') as f:
            validation_content = f.read()
        
        if "AuditStage" in validation_content and "from core.stage_gate_manager import" in validation_content:
            # Check if validation test has proper import
            if "from core.stage_gate_manager import" in validation_content:
                val_import_match = re.search(r'from core\.stage_gate_manager import ([^\n]+)', validation_content)
                if val_import_match and "AuditStage" not in val_import_match.group(1):
                    print("⚠️ Validation test also missing AuditStage import!")
                    new_val_imports = val_import_match.group(1) + ", AuditStage"
                    validation_content = validation_content.replace(
                        f"from core.stage_gate_manager import {val_import_match.group(1)}",
                        f"from core.stage_gate_manager import {new_val_imports}"
                    )
                    
                    with open(validation_file, 'w', encoding='utf-8') as f:
                        f.write(validation_content)
                    print("✅ Fixed validation test imports")
    
    # Write the fixed pipeline content
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def test_specific_failure_point():
    """Test the specific point where the failure occurs"""
    
    print("\n🧪 Testing specific failure point...")
    
    try:
        # Import everything we need
        from core.stage_gate_manager import StageGateManager, AuditStage, create_audit_session
        from enhanced_run_pipeline_day2 import EnhancedAuditPipelineDay2
        
        print("✅ All imports successful")
        
        # Create pipeline instance
        pipeline = EnhancedAuditPipelineDay2("Test Client", "test.com")
        print("✅ Pipeline creation successful")
        
        # Try to access AuditStage within the pipeline context
        stage = AuditStage.DISCOVERY
        print(f"✅ AuditStage accessible: {stage.name}")
        
        # Try the specific operation that might be failing
        # The error occurs after Stage 1 completion, so let's test stage advancement
        can_advance = pipeline.stage_manager.state.current_stage == AuditStage.DISCOVERY
        print(f"✅ Stage comparison works: {can_advance}")
        
        # Clean up
        if pipeline.stage_manager.state_file.exists():
            pipeline.stage_manager.state_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed at: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return False

def create_simple_test():
    """Create a simple test that isolates the issue"""
    
    test_content = '''#!/usr/bin/env python3
"""
Simple test to isolate AuditStage issue
"""

def test_auditstage():
    try:
        from core.stage_gate_manager import AuditStage, create_audit_session
        print("✅ Import successful")
        
        manager = create_audit_session("Simple Test")
        print("✅ Manager creation successful")
        
        stage = AuditStage.DISCOVERY
        print(f"✅ AuditStage access successful: {stage.name}")
        
        # Test comparison
        is_discovery = manager.state.current_stage == AuditStage.DISCOVERY
        print(f"✅ Stage comparison successful: {is_discovery}")
        
        # Clean up
        if manager.state_file.exists():
            manager.state_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Simple test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_auditstage()
    print(f"Simple test result: {'PASSED' if success else 'FAILED'}")
'''
    
    with open("simple_auditstage_test.py", "w") as f:
        f.write(test_content)
    
    print("✅ Created simple_auditstage_test.py")

def main():
    """Run comprehensive analysis and fix"""
    
    print("🚀 COMPREHENSIVE AUDITSTAGE FIX")
    print("=" * 50)
    
    # Step 1: Analyze current usage
    analyze_auditstage_usage()
    
    # Step 2: Apply comprehensive fix
    fix_all_imports()
    
    # Step 3: Test the specific failure point
    test_specific_failure_point()
    
    # Step 4: Create simple test
    create_simple_test()
    
    print("\n" + "=" * 50)
    print("🔧 FIXES APPLIED")
    print("Run these tests in order:")
    print("1. python simple_auditstage_test.py")
    print("2. python final_validation_test.py")

if __name__ == "__main__":
    main()

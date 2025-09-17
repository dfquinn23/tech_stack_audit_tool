#!/usr/bin/env python3
"""
Targeted fix for all identified issues
"""

from pathlib import Path

def fix_duplicate_import():
    """Fix the duplicate AuditStage import"""
    
    pipeline_file = Path("enhanced_run_pipeline_day2.py")
    
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Fixing duplicate AuditStage import...")
    
    # Fix the duplicate import
    old_import = "from core.stage_gate_manager import StageGateManager, AuditStage, AuditStage, create_audit_session, load_audit_session"
    new_import = "from core.stage_gate_manager import StageGateManager, AuditStage, create_audit_session, load_audit_session"
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        print("✅ Fixed duplicate AuditStage import")
    else:
        print("⚠️ Duplicate import not found")
    
    # Write back
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def fix_constructor_logic():
    """Fix the constructor logic that's causing the audit loading error"""
    
    pipeline_file = Path("enhanced_run_pipeline_day2.py")
    
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Checking constructor logic...")
    
    # Look for the constructor logic issue
    # The error suggests it's trying to load_audit_session instead of create_audit_session
    
    lines = content.split('\n')
    in_init = False
    init_lines = []
    
    for i, line in enumerate(lines):
        if 'def __init__(self' in line and 'EnhancedAuditPipelineDay2' in lines[max(0, i-5):i+1]:
            in_init = True
            init_lines.append((i, line))
        elif in_init and line.strip().startswith('def ') and '__init__' not in line:
            in_init = False
        elif in_init:
            init_lines.append((i, line))
    
    print(f"Found __init__ method with {len(init_lines)} lines")
    
    # Look for problematic logic
    for line_num, line in init_lines:
        if 'load_audit_session' in line and 'audit_id' in line:
            print(f"⚠️ Found problematic line {line_num+1}: {line.strip()}")
            # This might be the issue - it's trying to load instead of create
    
    # The issue is likely in the constructor where it decides whether to load or create
    # Let's check if there's logic that incorrectly chooses load over create
    
    return True

def create_simple_test_file():
    """Create a simple test file without unicode issues"""
    
    test_content = '''#!/usr/bin/env python3
"""
Simple test to verify AuditStage fix
"""

def test_auditstage():
    try:
        from core.stage_gate_manager import AuditStage, create_audit_session
        print("PASS: Import successful")
        
        manager = create_audit_session("Simple Test")
        print("PASS: Manager creation successful")
        
        stage = AuditStage.DISCOVERY
        print(f"PASS: AuditStage access successful: {stage.name}")
        
        # Test comparison
        is_discovery = manager.state.current_stage == AuditStage.DISCOVERY
        print(f"PASS: Stage comparison successful: {is_discovery}")
        
        # Clean up
        if manager.state_file.exists():
            manager.state_file.unlink()
        
        print("SUCCESS: All tests passed")
        return True
        
    except Exception as e:
        print(f"FAIL: Simple test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_auditstage()
    print(f"Overall result: {'PASSED' if success else 'FAILED'}")
'''
    
    with open("simple_test.py", "w", encoding='utf-8') as f:
        f.write(test_content)
    
    print("✅ Created simple_test.py")

def test_pipeline_creation():
    """Test pipeline creation with proper parameters"""
    
    print("\n🧪 Testing pipeline creation...")
    
    try:
        from enhanced_run_pipeline_day2 import EnhancedAuditPipelineDay2
        
        # The error suggests the constructor is expecting different parameters
        # Let's try creating it the way the validation test does
        
        # First, let's see what parameters the constructor expects
        import inspect
        sig = inspect.signature(EnhancedAuditPipelineDay2.__init__)
        print(f"Constructor signature: {sig}")
        
        # Try creating with different parameter combinations
        try:
            # Try with client_name only
            pipeline = EnhancedAuditPipelineDay2(client_name="Test Client")
            print("✅ Created with client_name only")
            
            # Clean up
            if hasattr(pipeline, 'stage_manager') and pipeline.stage_manager.state_file.exists():
                pipeline.stage_manager.state_file.unlink()
                
            return True
            
        except Exception as e1:
            print(f"Failed with client_name only: {e1}")
            
            try:
                # Try with client_name and client_domain
                pipeline = EnhancedAuditPipelineDay2(client_name="Test Client", client_domain="test.com")
                print("✅ Created with client_name and client_domain")
                
                # Clean up
                if hasattr(pipeline, 'stage_manager') and pipeline.stage_manager.state_file.exists():
                    pipeline.stage_manager.state_file.unlink()
                    
                return True
                
            except Exception as e2:
                print(f"Failed with client_name and client_domain: {e2}")
                
                try:
                    # Try the way it's used in validation test
                    from core.stage_gate_manager import create_audit_session
                    manager = create_audit_session("Test Client", "test.com")
                    pipeline = EnhancedAuditPipelineDay2(audit_id=manager.audit_id)
                    print("✅ Created with existing audit_id")
                    
                    # Clean up
                    if manager.state_file.exists():
                        manager.state_file.unlink()
                        
                    return True
                    
                except Exception as e3:
                    print(f"Failed with audit_id: {e3}")
                    return False
        
    except Exception as e:
        print(f"❌ Could not import pipeline: {e}")
        return False

def main():
    """Run all targeted fixes"""
    
    print("🎯 TARGETED FIX FOR ALL ISSUES")
    print("=" * 40)
    
    # Fix 1: Duplicate import
    fix_duplicate_import()
    
    # Fix 2: Check constructor logic
    fix_constructor_logic()
    
    # Fix 3: Create simple test
    create_simple_test_file()
    
    # Fix 4: Test pipeline creation
    test_pipeline_creation()
    
    print("\n" + "=" * 40)
    print("🔧 Run these tests:")
    print("1. python simple_test.py")
    print("2. python final_validation_test.py")

if __name__ == "__main__":
    main()

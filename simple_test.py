#!/usr/bin/env python3
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

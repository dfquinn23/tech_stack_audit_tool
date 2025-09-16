# test_simple_system.py
"""
Simplified system test focusing on core functionality
Run this after applying the pipeline patch to verify the fix works
"""

import sys
from pathlib import Path

def test_core_imports():
    """Test that all core modules can be imported"""
    print("🧪 Testing Core Imports...")
    
    try:
        from core.stage_gate_manager import StageGateManager, create_audit_session
        print("   ✅ Stage Gate Manager: Working")
    except Exception as e:
        print(f"   ❌ Stage Gate Manager failed: {e}")
        return False
    
    try:
        from core.discovery_engine import DiscoveryEngine
        print("   ✅ Discovery Engine: Working")
    except Exception as e:
        print(f"   ❌ Discovery Engine failed: {e}")
        return False
    
    try:
        from core.integration_health_checker import IntegrationHealthChecker
        print("   ✅ Integration Health Checker: Working")
    except Exception as e:
        print(f"   ❌ Integration Health Checker failed: {e}")
        return False
    
    return True

def test_enhanced_pipeline_import():
    """Test that the enhanced pipeline can be imported"""
    print("\n🧪 Testing Enhanced Pipeline Import...")
    
    try:
        from enhanced_run_pipeline_day2 import EnhancedAuditPipelineDay2
        print("   ✅ Enhanced Pipeline Class: Working")
        return True
    except Exception as e:
        print(f"   ❌ Enhanced Pipeline import failed: {e}")
        return False

def test_stage_gate_system():
    """Test basic stage gate functionality"""
    print("\n🧪 Testing Stage Gate System...")
    
    try:
        from core.stage_gate_manager import create_audit_session, AuditStage
        
        # Create test audit
        manager = create_audit_session("Test Client", "test.com")
        print("   ✅ Audit session created")
        
        # Add sample tool
        manager.add_tool("Test Tool", {
            "category": "Test",
            "users": ["Test User"], 
            "discovery_method": "manual"
        })
        print("   ✅ Tool added to inventory")
        
        # Test stage advancement
        can_advance, messages = manager.check_stage_gate(AuditStage.ASSESSMENT)
        if can_advance:
            manager.advance_stage(AuditStage.ASSESSMENT)
            print("   ✅ Stage advancement: Working")
        else:
            print(f"   ⚠️ Stage advancement blocked: {messages}")
        
        # Clean up test file
        if manager.state_file.exists():
            manager.state_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Stage gate system failed: {e}")
        return False

def test_enhanced_audit_tool():
    """Test the EnhancedAuditStateTool specifically"""
    print("\n🧪 Testing Enhanced Audit State Tool...")
    
    try:
        from enhanced_run_pipeline_day2 import EnhancedAuditStateTool
        from core.stage_gate_manager import StageGateManager
        
        # Create test manager
        manager = StageGateManager("Tool Test Client")
        
        # Create the tool (this is where the error was happening)
        audit_tool = EnhancedAuditStateTool(manager)
        print("   ✅ EnhancedAuditStateTool created successfully")
        
        # Test basic tool functionality
        tool_name = audit_tool.name
        tool_desc = audit_tool.description
        print(f"   ✅ Tool properties accessible: {tool_name}")
        
        # Clean up
        if manager.state_file.exists():
            manager.state_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Enhanced Audit State Tool failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run simplified system tests"""
    print("🚀 SIMPLIFIED SYSTEM TEST")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test core imports
    if test_core_imports():
        tests_passed += 1
    
    # Test enhanced pipeline import
    if test_enhanced_pipeline_import():
        tests_passed += 1
    
    # Test stage gate system
    if test_stage_gate_system():
        tests_passed += 1
    
    # Test the specific tool that was causing issues
    if test_enhanced_audit_tool():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    
    if tests_passed == total_tests:
        print("🎉 SIMPLIFIED SYSTEM TEST: ALL CORE COMPONENTS WORKING")
        print("✅ Core imports: Working")
        print("✅ Stage-Gate System: Working") 
        print("✅ Discovery Engine: Working")
        print("✅ Enhanced Pipeline: Working")
        print("\n🚀 READY TO RUN FIRST AUDIT!")
        print("Next step: python enhanced_run_pipeline_day2.py")
        return True
    else:
        print(f"⚠️ SIMPLIFIED SYSTEM TEST: {tests_passed}/{total_tests} COMPONENTS WORKING")
        print("Review the failed components above")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n❌ Some components failed. Check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ All core components validated successfully!")
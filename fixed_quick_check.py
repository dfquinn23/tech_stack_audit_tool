#!/usr/bin/env python3
"""
Fixed Quick System Check for Tech Stack Audit Tool
Fast validation of core components before running full tests
"""

import sys
import os
from pathlib import Path

def main():
    """Main check function with all imports at the top"""
    print("⚡ QUICK SYSTEM CHECK")
    print("=" * 30)
    
    issues_found = []
    checks_passed = 0
    total_checks = 6
    
    # Check 1: Python version
    print("1. Python Version:", end=" ")
    if sys.version_info >= (3, 8):
        print(f"✅ {sys.version_info.major}.{sys.version_info.minor}")
        checks_passed += 1
    else:
        print(f"❌ {sys.version_info.major}.{sys.version_info.minor} (need 3.8+)")
        issues_found.append("Upgrade Python to 3.8+")
    
    # Check 2: Required directories
    print("2. Directory Structure:", end=" ")
    required_dirs = ["core", "data", "output"]
    try:
        missing_dirs = []
        for d in required_dirs:
            if not Path(d).exists():
                missing_dirs.append(d)
        
        if not missing_dirs:
            print("✅ All directories exist")
            checks_passed += 1
        else:
            print(f"❌ Missing: {missing_dirs}")
            issues_found.append(f"Create directories: {', '.join(missing_dirs)}")
    except Exception as e:
        print(f"❌ Error checking directories: {e}")
        issues_found.append("Error checking directory structure")
    
    # Check 3: Environment file
    print("3. Environment Config:", end=" ")
    try:
        if Path(".env").exists():
            print("✅ .env file found")
            checks_passed += 1
        else:
            print("❌ .env file missing")
            issues_found.append("Create .env file from .env.example")
    except Exception as e:
        print(f"❌ Error checking .env: {e}")
        issues_found.append("Error checking environment file")
    
    # Check 4: Core module files
    print("4. Core Module Files:", end=" ")
    try:
        core_files = [
            "core/stage_gate_manager.py",
            "core/discovery_engine.py", 
            "core/integration_health_checker.py"
        ]
        missing_files = []
        for f in core_files:
            if not Path(f).exists():
                missing_files.append(f)
        
        if not missing_files:
            print("✅ All core modules present")
            checks_passed += 1
        else:
            print(f"❌ Missing: {missing_files}")
            issues_found.append("Install missing core modules")
    except Exception as e:
        print(f"❌ Error checking core files: {e}")
        issues_found.append("Error checking core module files")
    
    # Check 5: Main pipeline file
    print("5. Main Pipeline:", end=" ")
    try:
        if Path("enhanced_run_pipeline_day2.py").exists():
            print("✅ Pipeline file found")
            checks_passed += 1
        else:
            print("❌ Pipeline file missing")
            issues_found.append("Install enhanced_run_pipeline_day2.py")
    except Exception as e:
        print(f"❌ Error checking pipeline: {e}")
        issues_found.append("Error checking pipeline file")
    
    # Check 6: Basic import test
    print("6. Basic Import Test:", end=" ")
    try:
        # Try importing the most basic modules
        import json
        import asyncio
        from datetime import datetime
        print("✅ Basic imports working")
        checks_passed += 1
    except Exception as e:
        print(f"❌ Import failed: {e}")
        issues_found.append("Fix Python environment/dependencies")
    
    # Summary
    print("\n" + "=" * 30)
    print(f"📊 QUICK CHECK RESULTS: {checks_passed}/{total_checks}")
    
    if checks_passed == total_checks:
        print("🎉 QUICK CHECK PASSED!")
        print("\n🚀 Next steps:")
        print("   python system_test_runner.py  # Run full system test")
        print("   python test_complete_system.py  # If you have existing tests")
        return True
    else:
        print("⚠️  ISSUES FOUND:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        print("\n🔧 Fix these issues then run the quick check again")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
Check Directory Contents
Simple script to see what files and directories exist
"""

import os
import sys

def main():
    print("📁 DIRECTORY CONTENTS CHECK")
    print("=" * 40)
    print(f"Current directory: {os.getcwd()}")
    print()
    
    # List all items in current directory
    try:
        items = sorted(os.listdir("."))
        
        files = []
        directories = []
        
        for item in items:
            if os.path.isdir(item):
                # Count files in directory
                try:
                    file_count = len(os.listdir(item))
                    directories.append(f"{item}/ ({file_count} items)")
                except:
                    directories.append(f"{item}/ (can't read)")
            else:
                files.append(item)
        
        print("📁 DIRECTORIES:")
        if directories:
            for d in directories:
                print(f"   {d}")
        else:
            print("   (no directories found)")
        
        print("\n📄 FILES:")
        if files:
            for f in files:
                print(f"   {f}")
        else:
            print("   (no files found)")
        
        # Check for specific expected files
        print("\n🔍 LOOKING FOR KEY FILES:")
        expected_files = [
            "enhanced_run_pipeline_day2.py",
            "test_complete_system.py", 
            "requirements.txt",
            ".env"
        ]
        
        for expected_file in expected_files:
            if expected_file in files:
                print(f"   ✅ {expected_file}")
            else:
                print(f"   ❌ {expected_file} (missing)")
        
        # Check for expected directories
        print("\n📁 LOOKING FOR KEY DIRECTORIES:")
        expected_dirs = ["core", "data", "output", "agents"]
        
        for expected_dir in expected_dirs:
            if any(d.startswith(expected_dir + "/") for d in directories):
                print(f"   ✅ {expected_dir}/")
            else:
                print(f"   ❌ {expected_dir}/ (missing)")
        
    except Exception as e:
        print(f"❌ Error reading directory: {e}")

if __name__ == "__main__":
    main()

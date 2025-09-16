#!/usr/bin/env python3
"""
Repository cleanup script for Tech Stack Audit Tool
Removes duplicate, legacy, and one-time use files
"""

import os
import shutil
from pathlib import Path

def cleanup_repo():
    """Clean up repository by removing unnecessary files"""
    
    # Files to delete (one-time fixes, duplicates, legacy)
    files_to_delete = [
        "patch_enhanced_pipeline.py",
        "pipeline_patch.py", 
        "quick_fix_integration.py",
        "run_pipeline_utilities.py",
    ]
    
    print("🧹 Starting repository cleanup...")
    print("=" * 50)
    
    # Delete one-time use files
    deleted_files = 0
    for file_path in files_to_delete:
        if Path(file_path).exists():
            try:
                os.remove(file_path)
                print(f"✅ Deleted: {file_path}")
                deleted_files += 1
            except Exception as e:
                print(f"❌ Failed to delete {file_path}: {e}")
        else:
            print(f"⚠️  Not found: {file_path}")
    
    # Rename README.md.txt to README.md if it exists
    if Path("README.md.txt").exists() and not Path("README.md").exists():
        try:
            shutil.move("README.md.txt", "README.md")
            print("✅ Renamed README.md.txt to README.md")
        except Exception as e:
            print(f"❌ Failed to rename README: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"🎉 Cleanup completed!")
    print(f"   • Deleted {deleted_files} unnecessary files")
    print(f"   • Repository structure cleaned up")

def show_current_structure():
    """Show current directory structure"""
    print("\n📁 Current repository structure:")
    
    # Key paths to show
    key_paths = [
        "core/",
        "agents/", 
        "data/",
        "documentation_claude/",
        "enhanced_run_pipeline_day2.py",
        "test_complete_system.py",
        "requirements.txt",
        "README.md"
    ]
    
    for path in key_paths:
        if Path(path).exists():
            if Path(path).is_dir():
                file_count = len(list(Path(path).glob("*")))
                print(f"   ✅ {path} ({file_count} files)")
            else:
                print(f"   ✅ {path}")
        else:
            print(f"   ❌ {path} (missing)")

if __name__ == "__main__":
    print("🚀 Repository Cleanup Tool")
    print("This will remove duplicate, legacy, and one-time use files")
    
    response = input("\nProceed with cleanup? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        cleanup_repo()
        show_current_structure()
    else:
        print("Cleanup cancelled.")
        show_current_structure()
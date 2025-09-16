#!/usr/bin/env python3
"""
One-command fix for all remaining issues
Fixes pipeline references and creates missing files
"""

import sys
import re
from pathlib import Path

def fix_pipeline_references():
    """Fix all _stage_manager references in the pipeline"""
    
    pipeline_file = Path("enhanced_run_pipeline_day2.py")
    if not pipeline_file.exists():
        print("❌ enhanced_run_pipeline_day2.py not found")
        return False
    
    print("🔧 Fixing pipeline references...")
    
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the main issue: change _stage_manager back to stage_manager
    changes = [
        ("self._stage_manager", "self.stage_manager"),
        ("self._health_checker", "self.health_checker"), 
        ("self._gap_analyzer", "self.gap_analyzer"),
    ]
    
    changes_made = 0
    original_content = content
    
    for old_ref, new_ref in changes:
        if old_ref in content:
            content = content.replace(old_ref, new_ref)
            changes_made += 1
    
    # Fix the constructor
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
        changes_made += 1
        print("   ✅ Fixed constructor")
    
    # Only write if we made changes
    if content != original_content:
        with open(pipeline_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✅ Fixed {changes_made} references")
        return True
    else:
        print("   ⚠️ No changes needed")
        return True

def create_env_example():
    """Create .env.example template"""
    env_example_content = """# Tech Stack Audit Tool - Environment Configuration Template
# Copy this file to .env and fill in your actual API keys

# OpenAI Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Optional API Keys for Enhanced Discovery
ZOOM_API_KEY=your_zoom_api_key_here
MICROSOFT_GRAPH_CLIENT_ID=your_microsoft_client_id_here
MICROSOFT_GRAPH_CLIENT_SECRET=your_microsoft_client_secret_here
"""
    
    example_file = Path(".env.example")
    if not example_file.exists():
        with open(example_file, 'w') as f:
            f.write(env_example_content)
        print("✅ Created .env.example")
        return True
    else:
        print("⚠️ .env.example already exists")
        return True

def main():
    """Run all fixes"""
    print("🚀 Running All Fixes")
    print("=" * 40)
    
    success_count = 0
    
    # Fix 1: Pipeline references
    if fix_pipeline_references():
        success_count += 1
    
    # Fix 2: Create .env.example
    if create_env_example():
        success_count += 1
    
    print("\n" + "=" * 40)
    if success_count == 2:
        print("🎉 All fixes completed successfully!")
        print("\n🧪 Run test to verify:")
        print("   python test_complete_system.py")
        print("\n🧹 Optional cleanup:")
        print("   python cleanup_repo.py")
    else:
        print("⚠️ Some fixes may have failed - check output above")

if __name__ == "__main__":
    main()
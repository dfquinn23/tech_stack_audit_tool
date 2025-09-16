#!/usr/bin/env python3
"""
Setup Required Directories for Tech Stack Audit Tool
Creates all necessary directories if they don't exist
"""

import os
from pathlib import Path

def create_directories():
    """Create all required directories"""
    print("📁 Creating required directories...")
    
    directories = [
        "core",
        "data", 
        "data/audit_sessions",
        "data/discovery_cache",
        "data/integration_cache",
        "output",
        "agents"
    ]
    
    created_count = 0
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ Created: {directory}/")
                created_count += 1
            except Exception as e:
                print(f"   ❌ Failed to create {directory}: {e}")
        else:
            print(f"   ✅ Exists: {directory}/")
    
    print(f"\n📊 Created {created_count} new directories")
    return True

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    print("\n🔧 Checking environment configuration...")
    
    env_file = Path(".env")
    if env_file.exists():
        print("   ✅ .env file already exists")
        return True
    
    env_template = """# Tech Stack Audit Tool - Environment Configuration
# Add your actual API keys here

# OpenAI Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Optional API Keys for Enhanced Discovery
ZOOM_API_KEY=your_zoom_api_key_here
MICROSOFT_GRAPH_CLIENT_ID=your_microsoft_client_id_here
MICROSOFT_GRAPH_CLIENT_SECRET=your_microsoft_client_secret_here
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_template)
        print("   ✅ Created .env file template")
        print("   ⚠️  IMPORTANT: Add your OpenAI API key to .env file!")
        return True
    except Exception as e:
        print(f"   ❌ Failed to create .env file: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Tech Stack Audit Tool Setup")
    print("=" * 40)
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    print("\n✅ Setup completed!")
    print("\n🔧 Next steps:")
    print("   1. Add your OpenAI API key to .env file")
    print("   2. Run: python fixed_quick_check.py")
    print("   3. If quick check passes, run the full system test")

if __name__ == "__main__":
    main()

# setup.py
"""
Setup script for Tech Stack Audit Tool
Creates necessary directories and validates configuration
"""

import os
import sys
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = [
        "data/audit_sessions",
        "data/discovery_cache", 
        "data/integration_cache",
        "output",
        "core",
        "agents"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_env_file():
    """Check .env file configuration"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("⚠️ .env file not found. Creating template...")
        with open(".env", "w") as f:
            f.write("""# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Optional API Keys for Enhanced Discovery
ZOOM_API_KEY=your_zoom_api_key
MICROSOFT_GRAPH_CLIENT_ID=your_client_id
MICROSOFT_GRAPH_CLIENT_SECRET=your_client_secret
""")
        print("📝 Created .env template - please add your API keys")
    else:
        print("✅ .env file exists")
        
        # Check for required keys
        with open(".env", "r") as f:
            content = f.read()
            
        if "OPENAI_API_KEY=your_openai_api_key_here" in content:
            print("⚠️ Please update your OpenAI API key in .env file")
        elif "OPENAI_API_KEY=" in content:
            print("✅ OpenAI API key configured")

def validate_imports():
    """Validate that key imports work"""
    try:
        import crewai
        print("✅ CrewAI imported successfully")
    except ImportError:
        print("❌ CrewAI not found - run: pip install -r requirements.txt")
        return False
        
    try:
        import langchain_openai
        print("✅ LangChain OpenAI imported successfully")
    except ImportError:
        print("❌ LangChain OpenAI not found - run: pip install -r requirements.txt")
        return False
    
    try:
        import aiohttp
        print("✅ Async HTTP imported successfully")
    except ImportError:
        print("❌ aiohttp not found - run: pip install -r requirements.txt")
        return False
        
    return True

def main():
    """Main setup function"""
    print("🚀 Tech Stack Audit Tool Setup")
    print("=" * 40)
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Check environment
    print("\n🔧 Checking environment...")
    check_env_file()
    
    # Validate imports
    print("\n📦 Validating dependencies...")
    if validate_imports():
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Add your OpenAI API key to .env file")
        print("2. Run: python test_complete_system.py")
        print("3. If tests pass, run: python enhanced_run_pipeline_day2.py")
    else:
        print("\n❌ Setup incomplete - install dependencies first")
        print("Run: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
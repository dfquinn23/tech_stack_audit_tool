#!/usr/bin/env python3
"""
Create .env.example from existing .env file
Replaces actual values with placeholders
"""

import re
from pathlib import Path

def create_env_example():
    """Create .env.example from .env with sanitized values"""
    
    env_file = Path(".env")
    example_file = Path(".env.example")
    
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    if example_file.exists():
        print("⚠️ .env.example already exists")
        response = input("Overwrite? (y/n): ").lower().strip()
        if response not in ['y', 'yes']:
            print("Cancelled")
            return False
    
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Replace actual API keys with placeholders
        replacements = {
            r'OPENAI_API_KEY=sk-.*': 'OPENAI_API_KEY=your_openai_api_key_here',
            r'OPENAI_API_KEY=.*': 'OPENAI_API_KEY=your_openai_api_key_here',
            r'ZOOM_API_KEY=.*': 'ZOOM_API_KEY=your_zoom_api_key_here',
            r'MICROSOFT_GRAPH_CLIENT_ID=.*': 'MICROSOFT_GRAPH_CLIENT_ID=your_microsoft_client_id_here',
            r'MICROSOFT_GRAPH_CLIENT_SECRET=.*': 'MICROSOFT_GRAPH_CLIENT_SECRET=your_microsoft_client_secret_here',
        }
        
        example_content = content
        for pattern, replacement in replacements.items():
            example_content = re.sub(pattern, replacement, example_content)
        
        # Add header comment
        header = """# Tech Stack Audit Tool - Environment Configuration Template
# Copy this file to .env and fill in your actual API keys

"""
        
        with open(example_file, 'w') as f:
            f.write(header + example_content)
        
        print("✅ Created .env.example")
        print("   Your .env file with real keys is unchanged")
        print("   .env.example contains placeholder values for the repo")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env.example: {e}")
        return False

if __name__ == "__main__":
    create_env_example()
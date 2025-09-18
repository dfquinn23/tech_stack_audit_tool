# debug_file_upload.py
"""
Debug file upload issues in the Streamlit dashboard
Help identify where uploaded CSV files are going and why the same tools appear
"""

import os
from pathlib import Path
import pandas as pd

def check_data_directory():
    """Check what files exist in the data directory"""
    
    print("CHECKING DATA DIRECTORY CONTENTS")
    print("=" * 50)
    
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ data/ directory does not exist")
        return
    
    print(f"📁 Contents of data/ directory:")
    for item in data_dir.iterdir():
        if item.is_file():
            size = item.stat().st_size
            modified = item.stat().st_mtime
            print(f"   📄 {item.name} ({size} bytes)")
        elif item.is_dir():
            file_count = len(list(item.glob("*")))
            print(f"   📁 {item.name}/ ({file_count} files)")
    
    # Look specifically for temp files
    print(f"\n🔍 Looking for temp CSV files...")
    temp_files = list(data_dir.glob("temp_*.csv"))
    if temp_files:
        print(f"   Found {len(temp_files)} temp files:")
        for temp_file in temp_files:
            print(f"   📄 {temp_file.name}")
            try:
                df = pd.read_csv(temp_file)
                print(f"      → {len(df)} rows, columns: {list(df.columns)}")
                if len(df) > 0:
                    print(f"      → Tools: {df.iloc[:, 0].tolist()}")
            except Exception as e:
                print(f"      → Error reading: {e}")
    else:
        print("   ❌ No temp_*.csv files found")

def check_current_directory():
    """Check what files exist in current directory"""
    
    print(f"\n📁 CURRENT DIRECTORY CONTENTS")
    print("=" * 30)
    
    current_dir = Path(".")
    csv_files = list(current_dir.glob("*.csv"))
    temp_files = list(current_dir.glob("temp_*.csv"))
    
    if csv_files:
        print(f"📄 CSV files in current directory:")
        for csv_file in csv_files:
            print(f"   {csv_file.name}")
    
    if temp_files:
        print(f"📄 Temp files in current directory:")
        for temp_file in temp_files:
            print(f"   {temp_file.name}")

def check_streamlit_cache():
    """Check if Streamlit is caching uploaded files"""
    
    print(f"\n💾 STREAMLIT CACHE CHECK")
    print("=" * 30)
    
    # Common Streamlit cache locations
    cache_locations = [
        Path(".streamlit"),
        Path("~/.streamlit").expanduser(),
        Path.home() / ".streamlit",
        Path(os.getenv('APPDATA', '')) / "streamlit" if os.getenv('APPDATA') else None,
    ]
    
    for cache_dir in cache_locations:
        if cache_dir and cache_dir.exists():
            print(f"📁 Found Streamlit cache: {cache_dir}")
            for item in cache_dir.rglob("*"):
                if item.is_file() and item.suffix == '.csv':
                    print(f"   📄 {item}")

def analyze_pipeline_file_handling():
    """Analyze how the pipeline handles file uploads"""
    
    print(f"\n🔍 PIPELINE FILE HANDLING ANALYSIS")
    print("=" * 40)
    
    pipeline_file = Path("enhanced_run_pipeline_day2.py")
    if not pipeline_file.exists():
        print("❌ enhanced_run_pipeline_day2.py not found")
        return
    
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for file handling patterns
    file_patterns = [
        "temp_",
        ".csv",
        "pd.read_csv",
        "to_csv",
        "uploaded_file",
        "file_uploader"
    ]
    
    print("🔍 File handling patterns found:")
    for pattern in file_patterns:
        lines_with_pattern = [i+1 for i, line in enumerate(content.split('\n')) if pattern in line]
        if lines_with_pattern:
            print(f"   '{pattern}': lines {lines_with_pattern}")

def check_audit_sessions():
    """Check recent audit sessions to see what data they contain"""
    
    print(f"\n📊 RECENT AUDIT SESSIONS")
    print("=" * 30)
    
    sessions_dir = Path("data/audit_sessions")
    if not sessions_dir.exists():
        print("❌ No audit_sessions directory found")
        return
    
    session_files = list(sessions_dir.glob("*.json"))
    session_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"📁 Found {len(session_files)} audit sessions")
    
    # Check the 3 most recent sessions
    for i, session_file in enumerate(session_files[:3]):
        print(f"\n📄 Session {i+1}: {session_file.name}")
        try:
            import json
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            client_name = session_data.get('client_name', 'Unknown')
            tools = session_data.get('tool_inventory', {})
            created_at = session_data.get('created_at', 'Unknown')
            
            print(f"   Client: {client_name}")
            print(f"   Created: {created_at}")
            print(f"   Tools ({len(tools)}): {list(tools.keys())}")
            
        except Exception as e:
            print(f"   ❌ Error reading session: {e}")

def main():
    """Run comprehensive file upload debugging"""
    
    print("🔍 FILE UPLOAD DEBUGGING")
    print("=" * 60)
    
    check_data_directory()
    check_current_directory()
    check_streamlit_cache()
    analyze_pipeline_file_handling()
    check_audit_sessions()
    
    print(f"\n" + "=" * 60)
    print("🎯 DEBUGGING SUMMARY")
    print("\nThis analysis should help identify:")
    print("1. Where uploaded CSV files are actually stored")
    print("2. Whether temp files are being created/deleted")
    print("3. What data is actually in recent audit sessions")
    print("4. How the pipeline processes uploaded files")
    
    print(f"\n📝 NEXT STEPS:")
    print("1. Share this debug output")
    print("2. Try uploading a CSV with completely different tools")
    print("3. Check if the new tools appear in the audit session data")

if __name__ == "__main__":
    main()

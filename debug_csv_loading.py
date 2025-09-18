# debug_csv_loading.py
"""
Debug what's happening with CSV loading in the pipeline
"""
import pandas as pd
from pathlib import Path

def debug_csv_loading():
    """Debug the CSV loading issue"""
    print("🔍 DEBUGGING CSV LOADING")
    print("=" * 50)
    
    # Check what's in the CGA file
    cga_file = Path("data/cga_real_tools.csv")
    print(f"📄 CGA File: {cga_file}")
    print(f"   Exists: {cga_file.exists()}")
    print(f"   Size: {cga_file.stat().st_size} bytes")
    
    # Read the file manually
    if cga_file.exists():
        print(f"\n📋 Raw file contents:")
        with open(cga_file, 'r') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            print(f"   {i+1}: {repr(line)}")  # repr shows hidden characters
    
    # Try loading with pandas
    print(f"\n📊 Pandas loading test:")
    try:
        df = pd.read_csv(cga_file)
        print(f"   Loaded {len(df)} rows, {len(df.columns)} columns")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Tool names: {df['Tool Name'].tolist()}")
    except Exception as e:
        print(f"   ❌ Pandas error: {e}")
    
    # Check what the pipeline is actually loading
    print(f"\n🔍 Finding where pipeline loads default data...")
    
    pipeline_file = Path("enhanced_run_pipeline_day2.py")
    if pipeline_file.exists():
        with open(pipeline_file, 'r') as f:
            content = f.read()
        
        # Look for hardcoded tool lists
        if "Advent Axys" in content:
            print("   ❌ Found 'Advent Axys' hardcoded in pipeline file!")
            
            # Find the line numbers
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "Advent Axys" in line:
                    print(f"      Line {i+1}: {line.strip()}")
        
        # Look for CSV loading logic
        csv_loading_lines = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if ".csv" in line.lower() or "read_csv" in line.lower():
                csv_loading_lines.append((i+1, line.strip()))
        
        if csv_loading_lines:
            print(f"\n📄 CSV loading logic found:")
            for line_num, line in csv_loading_lines:
                print(f"   Line {line_num}: {line}")
        else:
            print(f"\n❌ No CSV loading logic found!")
    
    # Check the tech_stack_list.csv file
    default_file = Path("data/tech_stack_list.csv")
    if default_file.exists():
        print(f"\n📄 Default file check: {default_file}")
        try:
            df_default = pd.read_csv(default_file)
            print(f"   Tools in default file: {df_default['Tool Name'].tolist()}")
        except Exception as e:
            print(f"   Error reading default file: {e}")

if __name__ == "__main__":
    debug_csv_loading()
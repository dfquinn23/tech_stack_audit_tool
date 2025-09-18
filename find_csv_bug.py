# find_csv_loading_bug.py
"""
Find the actual CSV loading bug in the pipeline
"""
import re
from pathlib import Path

def find_csv_loading_logic():
    """Find where CSV loading happens in the pipeline"""
    
    pipeline_file = Path("enhanced_run_pipeline_day2.py")
    if not pipeline_file.exists():
        print("Pipeline file not found!")
        return
    
    print("FINDING CSV LOADING BUG")
    print("=" * 40)
    
    try:
        # Read with proper encoding to avoid Unicode errors
        with open(pipeline_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        with open(pipeline_file, 'r', encoding='latin1') as f:
            content = f.read()
    
    lines = content.split('\n')
    
    # Find CSV-related lines
    csv_lines = []
    for i, line in enumerate(lines, 1):
        if any(keyword in line.lower() for keyword in ['csv', 'read_csv', 'pandas', 'df']):
            csv_lines.append((i, line.strip()))
    
    print("CSV-related code found:")
    for line_num, line in csv_lines:
        print(f"  Line {line_num}: {line}")
    
    # Find the method that processes CSV files
    methods_with_csv = []
    current_method = None
    method_start = 0
    
    for i, line in enumerate(lines, 1):
        # Find method definitions
        if re.match(r'^\s*def\s+\w+.*csv.*:', line, re.IGNORECASE):
            current_method = line.strip()
            method_start = i
        elif re.match(r'^\s*async\s+def\s+\w+.*csv.*:', line, re.IGNORECASE):
            current_method = line.strip()
            method_start = i
        # Find CSV usage within methods
        elif current_method and 'csv' in line.lower():
            methods_with_csv.append((current_method, method_start, i, line.strip()))
    
    if methods_with_csv:
        print(f"\nMethods handling CSV:")
        for method, start_line, csv_line, csv_code in methods_with_csv:
            print(f"  {method} (line {start_line})")
            print(f"    Line {csv_line}: {csv_code}")
    
    # Look for hardcoded tool lists
    hardcoded_tools = []
    for i, line in enumerate(lines, 1):
        if 'advent axys' in line.lower() or 'cssi' in line.lower():
            hardcoded_tools.append((i, line.strip()))
    
    if hardcoded_tools:
        print(f"\nHARDCODED TOOLS FOUND:")
        for line_num, line in hardcoded_tools:
            print(f"  Line {line_num}: {line}")
    
    # Find the run_complete_enhanced_audit method
    in_method = False
    method_lines = []
    
    for i, line in enumerate(lines, 1):
        if 'def run_complete_enhanced_audit' in line:
            in_method = True
            method_lines = []
        elif in_method and line.strip().startswith('def '):
            break
        elif in_method:
            method_lines.append((i, line))
    
    if method_lines:
        print(f"\nrun_complete_enhanced_audit method:")
        for line_num, line in method_lines[:20]:  # First 20 lines
            if 'csv' in line.lower():
                print(f"  Line {line_num}: {line.rstrip()}")

if __name__ == "__main__":
    find_csv_loading_logic()
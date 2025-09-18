# examine_load_input_function.py
"""
Find and examine the load_input function that's supposed to load CSV files
"""
from pathlib import Path
import re

def find_load_input_function():
    """Find where load_input is defined and what it does"""
    
    print("EXAMINING load_input() FUNCTION")
    print("=" * 40)
    
    # Check all Python files for load_input definition
    python_files = list(Path(".").glob("*.py")) + list(Path("core").glob("*.py"))
    
    load_input_found = False
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            continue
        
        lines = content.split('\n')
        
        # Look for load_input function definition
        for i, line in enumerate(lines, 1):
            if re.match(r'^\s*def\s+load_input\s*\(', line):
                print(f"Found load_input() in {py_file}, line {i}")
                load_input_found = True
                
                # Show the function definition and body
                function_lines = []
                j = i - 1  # Convert to 0-based index
                indent_level = len(line) - len(line.lstrip())
                
                # Get function signature
                function_lines.append(f"Line {i}: {line}")
                
                # Get function body until we hit same or lower indentation
                j += 1
                while j < len(lines):
                    current_line = lines[j]
                    if current_line.strip() == "":
                        function_lines.append(f"Line {j+1}: {current_line}")
                    elif len(current_line) - len(current_line.lstrip()) > indent_level:
                        function_lines.append(f"Line {j+1}: {current_line}")
                    else:
                        # Hit same or lower indentation - end of function
                        break
                    j += 1
                
                print("Function definition:")
                for func_line in function_lines[:20]:  # Show first 20 lines
                    print(f"  {func_line}")
                
                if len(function_lines) > 20:
                    print(f"  ... ({len(function_lines) - 20} more lines)")
                
                print()
    
    if not load_input_found:
        print("load_input() function NOT FOUND!")
        print("This means it's either:")
        print("1. Imported from another module")
        print("2. Defined in a different way")
        print("3. Missing entirely")
        
        # Look for imports
        pipeline_file = Path("enhanced_run_pipeline_day2.py")
        if pipeline_file.exists():
            with open(pipeline_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            import_lines = []
            for i, line in enumerate(content.split('\n'), 1):
                if 'load_input' in line:
                    import_lines.append(f"Line {i}: {line.strip()}")
            
            if import_lines:
                print("\nReferences to load_input:")
                for imp_line in import_lines:
                    print(f"  {imp_line}")

if __name__ == "__main__":
    find_load_input_function()
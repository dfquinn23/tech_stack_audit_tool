# fix_load_input_bug.py
"""
Fix the load_input() function to actually use the file_path parameter
"""
from pathlib import Path

def fix_load_input_function():
    """Fix the CSV loading bug in core/input_handler.py"""
    
    input_handler_file = Path("core/input_handler.py")
    if not input_handler_file.exists():
        print("core/input_handler.py not found!")
        return False
    
    print("FIXING CSV LOADING BUG")
    print("=" * 30)
    
    # Read the current file
    with open(input_handler_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Show the current buggy line
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if 'df = pd.read_csv("data/tech_stack_list.csv")' in line:
            print(f"FOUND BUG on line {i}:")
            print(f"  Current: {line.strip()}")
            print(f"  Problem: Ignores the file_path parameter!")
            break
    
    # Fix the bug: replace hardcoded path with file_path parameter
    old_line = '        df = pd.read_csv("data/tech_stack_list.csv")'
    new_line = '        df = pd.read_csv(file_path)'
    
    if old_line in content:
        fixed_content = content.replace(old_line, new_line)
        
        # Write the fixed content back
        with open(input_handler_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"  Fixed to: {new_line.strip()}")
        print("BUG FIXED!")
        return True
    else:
        print("Could not find the exact line to fix")
        return False

def verify_fix():
    """Verify the fix was applied correctly"""
    
    input_handler_file = Path("core/input_handler.py")
    
    with open(input_handler_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if 'df = pd.read_csv(file_path)' in line:
            print(f"VERIFICATION: Line {i} now correctly uses file_path parameter")
            return True
    
    print("VERIFICATION FAILED: Fix not applied correctly")
    return False

if __name__ == "__main__":
    if fix_load_input_function():
        if verify_fix():
            print("\nSUCCESS! The CSV loading bug is now fixed.")
            print("The tool will now properly read whatever CSV file you specify.")
            print("\nTest it with: python test_with_cga_data.py")
        else:
            print("Fix applied but verification failed")
    else:
        print("Failed to apply fix")
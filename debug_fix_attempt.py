# debug_fix_attempt.py
"""
Debug what happened when we tried to fix the load_input function
"""
from pathlib import Path

def debug_fix_attempt():
    """Debug why the fix script ran silently"""
    
    print("DEBUGGING FIX ATTEMPT")
    print("=" * 30)
    
    # Check if the file exists
    input_handler_file = Path("core/input_handler.py")
    print(f"File exists: {input_handler_file.exists()}")
    
    if not input_handler_file.exists():
        print("ERROR: core/input_handler.py not found!")
        return
    
    # Show current file contents
    try:
        with open(input_handler_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        print(f"File has {len(lines)} lines")
        
        # Show lines around the load_input function
        print("\nload_input function content:")
        in_function = False
        for i, line in enumerate(lines, 1):
            if 'def load_input' in line:
                in_function = True
                print(f"Line {i}: {line}")
            elif in_function and line.strip().startswith('def '):
                break
            elif in_function:
                print(f"Line {i}: {line}")
                if 'return df' in line:
                    break
        
        # Check if the bug still exists
        if 'df = pd.read_csv("data/tech_stack_list.csv")' in content:
            print("\nBUG STATUS: Still exists - hardcoded path found")
        elif 'df = pd.read_csv(file_path)' in content:
            print("\nBUG STATUS: Fixed - using file_path parameter")
        else:
            print("\nBUG STATUS: Unknown - neither pattern found")
            
    except Exception as e:
        print(f"Error reading file: {e}")

def manual_fix():
    """Apply the fix manually with detailed output"""
    
    print("\nAPPLYING MANUAL FIX")
    print("=" * 20)
    
    input_handler_file = Path("core/input_handler.py")
    
    try:
        # Read current content
        with open(input_handler_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"Original file size: {len(content)} characters")
        
        # Apply the fix
        old_line = '        df = pd.read_csv("data/tech_stack_list.csv")'
        new_line = '        df = pd.read_csv(file_path)'
        
        if old_line in content:
            print(f"Found target line to replace")
            fixed_content = content.replace(old_line, new_line)
            print(f"New file size: {len(fixed_content)} characters")
            
            # Write back
            with open(input_handler_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print("File written successfully")
            
            # Verify the fix
            with open(input_handler_file, 'r', encoding='utf-8') as f:
                verify_content = f.read()
            
            if 'df = pd.read_csv(file_path)' in verify_content:
                print("VERIFICATION: Fix applied successfully!")
                return True
            else:
                print("VERIFICATION: Fix not applied correctly")
                return False
        else:
            print("Target line not found - looking for alternatives...")
            
            # Look for any pandas read_csv calls
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'pd.read_csv(' in line and 'tech_stack_list.csv' in line:
                    print(f"Found alternative pattern on line {i}: {line.strip()}")
                    return False
            
            print("No CSV reading patterns found")
            return False
            
    except Exception as e:
        print(f"Error during manual fix: {e}")
        return False

if __name__ == "__main__":
    debug_fix_attempt()
    
    response = input("\nApply manual fix? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        if manual_fix():
            print("\nSUCCESS! Now test with:")
            print("python test_with_cga_data.py")
        else:
            print("Manual fix failed")
    else:
        print("Manual fix skipped")
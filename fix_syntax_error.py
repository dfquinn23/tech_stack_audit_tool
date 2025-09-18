# fix_syntax_error.py
"""
Fix the f-string syntax error in discovery_engine.py
The issue is nested quotes in: f"domain_footprint_{domain.replace(".", "_")}"
"""

from pathlib import Path
import re

def fix_fstring_syntax():
    """Fix the f-string syntax error"""
    
    print("🔧 FIXING F-STRING SYNTAX ERROR")
    print("=" * 40)
    
    discovery_file = Path("core/discovery_engine.py")
    if not discovery_file.exists():
        print("❌ discovery_engine.py not found")
        return False
    
    print("🔧 Fixing f-string in discovery_engine.py...")
    
    # Read the file
    with open(discovery_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix the problematic f-string
    # The issue: f"domain_footprint_{domain.replace(".", "_")}"
    # Should be: f"domain_footprint_{domain.replace('.', '_')}"
    
    fixes = [
        # Fix the nested quotes issue
        (r'f"domain_footprint_\{domain\.replace\("\."\, "_"\)\}"', 
         'f"domain_footprint_{domain.replace(\'.\', \'_\')}"'),
        
        # Alternative pattern in case the regex doesn't match exactly
        (r'domain\.replace\("\."\, "_"\)', 
         "domain.replace('.', '_')"),
        
        # More general fix for this specific line
        (r'cache_key = f"domain_footprint_\{domain\.replace\("\."\, "_"\)\}"',
         'cache_key = f"domain_footprint_{domain.replace(\'.\', \'_\')}"'),
    ]
    
    fixed = False
    for old_pattern, new_pattern in fixes:
        if re.search(old_pattern, content):
            content = re.sub(old_pattern, new_pattern, content)
            print(f"   ✅ Fixed f-string pattern: {old_pattern[:30]}...")
            fixed = True
    
    # If the regex didn't work, try a simpler string replacement
    if not fixed:
        problematic_line = 'cache_key = f"domain_footprint_{domain.replace(".", "_")}"'
        fixed_line = "cache_key = f'domain_footprint_{domain.replace(\".\", \"_\")}'"
        
        if problematic_line in content:
            content = content.replace(problematic_line, fixed_line)
            print("   ✅ Fixed f-string with string replacement")
            fixed = True
        else:
            # Try to find any line with the replace pattern and fix it
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'domain.replace(".", "_")' in line and 'f"' in line:
                    # Replace double quotes inside f-string with single quotes
                    lines[i] = line.replace('domain.replace(".", "_")', "domain.replace('.', '_')")
                    print(f"   ✅ Fixed line {i+1}")
                    fixed = True
                    break
            
            if fixed:
                content = '\n'.join(lines)
    
    if fixed:
        # Write the fixed content back
        with open(discovery_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ F-string syntax error fixed!")
        return True
    else:
        print("❌ Could not find the problematic f-string to fix")
        print("   Manually check discovery_engine.py around line 152")
        return False

def clean_unicode_file():
    """Remove the problematic unicode file if it exists"""
    example_file = Path("domain_input_examples.py")
    if example_file.exists():
        try:
            example_file.unlink()
            print("✅ Removed problematic unicode example file")
        except:
            print("⚠️ Could not remove example file")

def main():
    """Fix both issues"""
    print("🚀 FIXING SYNTAX AND UNICODE ERRORS")
    print("=" * 50)
    
    # Fix 1: F-string syntax error
    if fix_fstring_syntax():
        print("✅ Syntax error fixed")
    else:
        print("❌ Syntax error fix failed")
        return False
    
    # Fix 2: Remove problematic unicode file
    clean_unicode_file()
    
    print("\n🎉 All fixes completed!")
    print("🧪 Try your Streamlit app again")
    return True

if __name__ == "__main__":
    main()

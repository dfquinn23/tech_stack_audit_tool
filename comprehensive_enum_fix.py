# comprehensive_enum_fix.py
"""
Comprehensive fix for all enum .value attribute errors
Finds and fixes ALL instances of .value calls in integration_health_checker.py
"""

from pathlib import Path
import re

def fix_all_enum_values():
    """Fix all enum .value calls in the integration health checker"""
    
    print("🔧 COMPREHENSIVE ENUM VALUE FIX")
    print("=" * 50)
    
    integration_file = Path("core/integration_health_checker.py")
    if not integration_file.exists():
        print("❌ integration_health_checker.py not found")
        return False
    
    print("🔧 Fixing ALL enum .value calls...")
    
    # Read the file
    with open(integration_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create a helper function to safely get enum values
    helper_function = '''
def _safe_enum_value(enum_obj):
    """Safely get the value from an enum object or return the object if it's already a string"""
    if hasattr(enum_obj, 'value'):
        return enum_obj.value
    else:
        return str(enum_obj)

'''
    
    # Add the helper function at the top after imports
    if "_safe_enum_value" not in content:
        # Find a good place to insert it (after imports)
        import_pattern = r'(from datetime import.*?\n)'
        match = re.search(import_pattern, content, re.DOTALL)
        if match:
            insert_point = match.end()
            content = content[:insert_point] + helper_function + content[insert_point:]
            print("   ✅ Added safe enum value helper function")
        else:
            # Fallback: add after the first import
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    lines.insert(i + 1, helper_function)
                    content = '\n'.join(lines)
                    break
    
    # Now find and replace ALL .value calls on assessment attributes
    enum_patterns = [
        # Direct attribute access patterns
        (r'assessment\.status\.value', '_safe_enum_value(assessment.status)'),
        (r'assessment\.business_impact\.value', '_safe_enum_value(assessment.business_impact)'),
        (r'assessment\.integration_type\.value', '_safe_enum_value(assessment.integration_type)'),
        
        # In dictionary/list comprehensions
        (r'"status": assessment\.status\.value', '"status": _safe_enum_value(assessment.status)'),
        (r'"integration_type": assessment\.integration_type\.value', '"integration_type": _safe_enum_value(assessment.integration_type)'),
        (r'"business_impact": assessment\.business_impact\.value', '"business_impact": _safe_enum_value(assessment.business_impact)'),
        
        # Variable assignments
        (r'status = assessment\.status\.value', 'status = _safe_enum_value(assessment.status)'),
        (r'integration_type = assessment\.integration_type\.value', 'integration_type = _safe_enum_value(assessment.integration_type)'),
        (r'business_impact = assessment\.business_impact\.value', 'business_impact = _safe_enum_value(assessment.business_impact)'),
    ]
    
    fixes_applied = 0
    for pattern, replacement in enum_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            fixes_applied += 1
            print(f"   ✅ Fixed pattern: {pattern[:30]}...")
    
    # Write the fixed content back
    with open(integration_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Applied {fixes_applied} enum value fixes!")
    return True

def fix_line_by_line():
    """Alternative approach: Fix line by line"""
    
    integration_file = Path("core/integration_health_checker.py")
    if not integration_file.exists():
        return False
    
    print("🔧 Line-by-line enum fix...")
    
    with open(integration_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = 0
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Replace all .value calls with safe versions
        if '.status.value' in line and 'assessment' in line:
            lines[i] = line.replace('.status.value', '.status.value if hasattr(assessment.status, \'value\') else str(assessment.status)')
            lines[i] = lines[i].replace('assessment.status.value if hasattr(assessment.status, \'value\') else str(assessment.status)', 'str(assessment.status)')
            fixed_lines += 1
            print(f"   ✅ Fixed line {i+1}: status.value")
        
        elif '.integration_type.value' in line and 'assessment' in line:
            lines[i] = line.replace('.integration_type.value', '.integration_type.value if hasattr(assessment.integration_type, \'value\') else str(assessment.integration_type)')
            lines[i] = lines[i].replace('assessment.integration_type.value if hasattr(assessment.integration_type, \'value\') else str(assessment.integration_type)', 'str(assessment.integration_type)')
            fixed_lines += 1
            print(f"   ✅ Fixed line {i+1}: integration_type.value")
        
        elif '.business_impact.value' in line and 'assessment' in line:
            lines[i] = line.replace('.business_impact.value', '.business_impact.value if hasattr(assessment.business_impact, \'value\') else str(assessment.business_impact)')
            lines[i] = lines[i].replace('assessment.business_impact.value if hasattr(assessment.business_impact, \'value\') else str(assessment.business_impact)', 'str(assessment.business_impact)')
            fixed_lines += 1
            print(f"   ✅ Fixed line {i+1}: business_impact.value")
    
    if fixed_lines > 0:
        with open(integration_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"   ✅ Fixed {fixed_lines} lines")
        return True
    
    return False

def simple_string_conversion():
    """Simplest approach: Just convert everything to strings"""
    
    integration_file = Path("core/integration_health_checker.py")
    if not integration_file.exists():
        return False
    
    print("🔧 Simple string conversion approach...")
    
    with open(integration_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple replacements - just wrap everything in str()
    simple_fixes = [
        ('assessment.status.value', 'str(assessment.status)'),
        ('assessment.integration_type.value', 'str(assessment.integration_type)'),
        ('assessment.business_impact.value', 'str(assessment.business_impact)'),
    ]
    
    fixes_applied = 0
    for old, new in simple_fixes:
        if old in content:
            content = content.replace(old, new)
            fixes_applied += 1
            print(f"   ✅ Replaced {old} with {new}")
    
    if fixes_applied > 0:
        with open(integration_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Applied {fixes_applied} simple string conversions!")
        return True
    
    return False

def main():
    """Try different fix approaches"""
    print("🚀 COMPREHENSIVE ENUM FIXES")
    print("=" * 50)
    
    # Try the simple approach first
    print("🔧 Attempting simple string conversion...")
    if simple_string_conversion():
        print("✅ Simple fix applied successfully!")
        return True
    
    # Try the line-by-line approach
    print("🔧 Attempting line-by-line fix...")
    if fix_line_by_line():
        print("✅ Line-by-line fix applied successfully!")
        return True
    
    # Try the comprehensive approach
    print("🔧 Attempting comprehensive fix...")
    if fix_all_enum_values():
        print("✅ Comprehensive fix applied successfully!")
        return True
    
    print("❌ All fix attempts failed")
    print("📝 Manual fix needed:")
    print("   1. Open core/integration_health_checker.py")
    print("   2. Find all lines with '.status.value', '.integration_type.value', etc.")
    print("   3. Replace them with str(assessment.status), str(assessment.integration_type), etc.")
    
    return False

if __name__ == "__main__":
    if main():
        print("\n🎉 Enum fixes completed!")
        print("🚀 Try your audit again")
    else:
        print("\n❌ Fixes failed - manual intervention needed")

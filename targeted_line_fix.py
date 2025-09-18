# targeted_line_fix.py
"""
Very targeted fix for the specific lines causing enum errors
Focuses on lines 477-479 and the generate_integration_summary method
"""

from pathlib import Path

def targeted_fix():
    """Fix the specific problematic lines"""
    
    print("🎯 TARGETED LINE FIX")
    print("=" * 30)
    
    integration_file = Path("core/integration_health_checker.py")
    if not integration_file.exists():
        print("❌ integration_health_checker.py not found")
        return False
    
    # Read the file
    with open(integration_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Looking for generate_integration_summary method...")
    
    # Find the generate_integration_summary method and fix all .value calls in it
    method_pattern = r'(def generate_integration_summary\(self, assessments.*?\n        return \{.*?\})'
    
    import re
    match = re.search(method_pattern, content, re.DOTALL)
    
    if match:
        method_content = match.group(1)
        print("   ✅ Found generate_integration_summary method")
        
        # Replace all .value calls in this method with str() calls
        fixed_method = method_content
        fixed_method = fixed_method.replace('assessment.status.value', 'str(assessment.status)')
        fixed_method = fixed_method.replace('assessment.integration_type.value', 'str(assessment.integration_type)')
        fixed_method = fixed_method.replace('assessment.business_impact.value', 'str(assessment.business_impact)')
        
        # Replace the method in the full content
        content = content.replace(method_content, fixed_method)
        
        print("   ✅ Fixed all .value calls in generate_integration_summary")
        
        # Write back the fixed content
        with open(integration_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    else:
        print("   ❌ Could not find generate_integration_summary method")
        
        # Fallback: just replace all .value calls globally
        print("   🔧 Applying global .value replacements...")
        
        replacements = [
            ('assessment.status.value', 'str(assessment.status)'),
            ('assessment.integration_type.value', 'str(assessment.integration_type)'),
            ('assessment.business_impact.value', 'str(assessment.business_impact)'),
        ]
        
        changes = 0
        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                changes += 1
                print(f"     ✅ {old} → {new}")
        
        if changes > 0:
            with open(integration_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   ✅ Applied {changes} global replacements")
            return True
        else:
            print("   ❌ No replacements found")
            return False

def show_problem_area():
    """Show the specific lines around the error"""
    
    integration_file = Path("core/integration_health_checker.py")
    if not integration_file.exists():
        return
    
    with open(integration_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("🔍 Lines around the error (475-485):")
    for i in range(474, min(485, len(lines))):
        line_num = i + 1
        line_content = lines[i].rstrip()
        marker = " ← ERROR" if line_num in [477, 479] else ""
        print(f"   {line_num:3d}: {line_content}{marker}")

if __name__ == "__main__":
    print("🚀 TARGETED ENUM FIX")
    print("=" * 40)
    
    # Show the problem area first
    show_problem_area()
    
    print("\n🔧 Applying targeted fix...")
    if targeted_fix():
        print("\n🎉 Targeted fix completed!")
        print("🚀 Try your audit again")
    else:
        print("\n❌ Targeted fix failed")
        print("📝 Try the comprehensive fix instead:")
        print("   python comprehensive_enum_fix.py")

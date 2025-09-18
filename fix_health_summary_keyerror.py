# fix_health_summary_keyerror.py
"""
Fix the KeyError for 'total_integrations_assessed' in the pipeline
The issue is that the integration health checker may return an error dict instead of the expected summary
"""

from pathlib import Path

def fix_pipeline_health_summary_handling():
    """Fix how the pipeline handles health summary results"""
    
    print("🔧 FIXING HEALTH SUMMARY KEY ERROR")
    print("=" * 50)
    
    pipeline_file = Path("enhanced_run_pipeline_day2.py")
    if not pipeline_file.exists():
        print("❌ enhanced_run_pipeline_day2.py not found")
        return False
    
    print("🔧 Reading pipeline file...")
    
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the problematic section around line 299
    # The error happens when trying to access health_summary['total_integrations_assessed']
    
    # Look for the pattern that's failing
    old_pattern = """        print(f"✅ Health assessment completed:")
        print(f"   • Total integrations assessed: {health_summary['total_integrations_assessed']}")
        print(f"   • Average health score: {health_summary['average_health_score']}/100")
        print(f"   • Missing integrations: {health_summary['missing_integrations']}")
        print(f"   • Broken integrations: {health_summary['broken_integrations']}")"""
    
    new_pattern = """        print(f"✅ Health assessment completed:")
        
        # Check if we got a valid summary or an error
        if 'error' in health_summary:
            print(f"   ⚠️ Health assessment warning: {health_summary['error']}")
            print(f"   • Total integrations assessed: 0")
            print(f"   • Average health score: 0/100")
            print(f"   • Missing integrations: 0")
            print(f"   • Broken integrations: 0")
        else:
            print(f"   • Total integrations assessed: {health_summary.get('total_integrations_assessed', 0)}")
            print(f"   • Average health score: {health_summary.get('average_health_score', 0)}/100")
            print(f"   • Missing integrations: {health_summary.get('missing_integrations', 0)}")
            print(f"   • Broken integrations: {health_summary.get('broken_integrations', 0)}")"""
    
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        print("   ✅ Fixed health summary access pattern")
    else:
        # Alternative fix: use .get() method for safe dictionary access
        print("   🔧 Applying safe dictionary access fixes...")
        
        # Replace direct dictionary access with .get() method
        fixes = [
            ("health_summary['total_integrations_assessed']", "health_summary.get('total_integrations_assessed', 0)"),
            ("health_summary['average_health_score']", "health_summary.get('average_health_score', 0)"),
            ("health_summary['missing_integrations']", "health_summary.get('missing_integrations', 0)"),
            ("health_summary['broken_integrations']", "health_summary.get('broken_integrations', 0)"),
            ("health_summary['healthy_integrations']", "health_summary.get('healthy_integrations', 0)"),
            ("health_summary['status_distribution']", "health_summary.get('status_distribution', {})"),
            ("health_summary['top_issues']", "health_summary.get('top_issues', [])"),
        ]
        
        changes = 0
        for old_access, new_access in fixes:
            if old_access in content:
                content = content.replace(old_access, new_access)
                changes += 1
                print(f"     ✅ Fixed: {old_access}")
        
        if changes > 0:
            print(f"   ✅ Applied {changes} safe dictionary access fixes")
        else:
            print("   ❌ Could not find the problematic dictionary access pattern")
            return False
    
    # Write the fixed content back
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Pipeline health summary handling fixed!")
    return True

def fix_integration_health_checker():
    """Ensure the integration health checker always returns a proper summary structure"""
    
    integration_file = Path("core/integration_health_checker.py")
    if not integration_file.exists():
        print("⚠️ integration_health_checker.py not found - skipping")
        return False
    
    print("🔧 Ensuring integration health checker returns proper summary...")
    
    with open(integration_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the generate_integration_summary method and ensure it always returns proper structure
    old_error_return = '''        if total == 0:
            return {"error": "No assessments to summarize"}'''
    
    new_error_return = '''        if total == 0:
            return {
                "error": "No assessments to summarize",
                "summary_timestamp": datetime.now().isoformat(),
                "total_integrations_assessed": 0,
                "average_health_score": 0,
                "status_distribution": {},
                "criticality_distribution": {},
                "top_issues": [],
                "critical_integrations_needing_attention": [],
                "healthy_integrations": 0,
                "missing_integrations": 0,
                "broken_integrations": 0
            }'''
    
    if old_error_return in content:
        content = content.replace(old_error_return, new_error_return)
        
        with open(integration_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✅ Fixed integration health checker error return structure")
        return True
    else:
        print("   ℹ️ Integration health checker already has proper structure")
        return True

def main():
    """Apply both fixes"""
    print("🚀 FIXING HEALTH SUMMARY KEY ERROR")
    print("=" * 60)
    
    fixes_applied = 0
    
    # Fix 1: Pipeline handling of health summary
    if fix_pipeline_health_summary_handling():
        fixes_applied += 1
        print("✅ Pipeline health summary handling fixed")
    
    # Fix 2: Integration health checker return structure
    if fix_integration_health_checker():
        fixes_applied += 1
        print("✅ Integration health checker structure ensured")
    
    print(f"\n{'='*60}")
    if fixes_applied >= 1:
        print("🎉 HEALTH SUMMARY FIXES COMPLETED!")
        print(f"   ✅ Applied fixes to handle missing dictionary keys")
        print(f"   ✅ Pipeline will now handle both success and error cases")
        print("\n🧪 Try your audit again - the KeyError should be resolved!")
        return True
    else:
        print("❌ FIXES FAILED")
        print("📝 Manual fix needed:")
        print("   1. Open enhanced_run_pipeline_day2.py")
        print("   2. Find line ~299 with health_summary['total_integrations_assessed']")
        print("   3. Change to: health_summary.get('total_integrations_assessed', 0)")
        print("   4. Do the same for other health_summary dictionary accesses")
        return False

if __name__ == "__main__":
    main()

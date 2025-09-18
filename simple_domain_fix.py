# simple_domain_fix.py
"""
Simple fix to accept domain names without protocols
Changes the input to accept just 'crescentgroveadvisors.com' instead of full URLs
"""

from pathlib import Path
import re

def fix_domain_input():
    """Update code to accept simple domain names instead of full URLs"""
    
    print("🔧 SIMPLE DOMAIN INPUT FIX")
    print("=" * 40)
    
    files_to_update = []
    
    # Fix 1: Discovery Engine
    discovery_file = Path("core/discovery_engine.py")
    if discovery_file.exists():
        print("🔧 Updating discovery_engine.py...")
        
        with open(discovery_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add domain normalization function
        normalize_function = '''    def _normalize_domain(self, domain: str) -> str:
        """Normalize domain input to just the domain name"""
        if not domain:
            return domain
            
        # Remove protocol if present
        domain = re.sub(r'^https?://', '', domain)
        
        # Remove www. if present
        domain = re.sub(r'^www\.', '', domain)
        
        # Remove trailing slashes
        domain = domain.rstrip('/')
        
        # Remove any path components
        domain = domain.split('/')[0]
        
        return domain.lower().strip()
'''
        
        # Add the function after the __init__ method
        if "_normalize_domain" not in content:
            # Find the end of __init__ method
            init_pattern = r'(def __init__\(self[^)]*\):.*?)((?=\n    def|\n\n|\nclass|\Z))'
            match = re.search(init_pattern, content, re.DOTALL)
            
            if match:
                content = content[:match.end(1)] + "\n" + normalize_function + content[match.end(1):]
                print("   ✅ Added domain normalization function")
            else:
                # Fallback: add after class definition
                class_def = "class DiscoveryEngine:"
                if class_def in content:
                    content = content.replace(class_def, class_def + "\n" + normalize_function)
                    print("   ✅ Added domain normalization function (fallback)")
        
        # Update methods that use domain parameter to normalize it first
        methods_to_update = [
            "discover_domain_footprint",
            "enhance_tool_inventory"
        ]
        
        for method_name in methods_to_update:
            # Find the method and add domain normalization at the start
            method_pattern = rf'(async def {method_name}\(self[^)]*domain[^)]*\):.*?)(\n        [^#\n])'
            
            def add_normalization(match):
                method_start = match.group(1)
                next_line = match.group(2)
                
                # Check if normalization already exists
                if "domain = self._normalize_domain(domain)" in method_start:
                    return match.group(0)  # Already normalized
                
                normalization_line = f'\n        domain = self._normalize_domain(domain)'
                return method_start + normalization_line + next_line
            
            old_content = content
            content = re.sub(method_pattern, add_normalization, content, flags=re.DOTALL)
            
            if content != old_content:
                print(f"   ✅ Added domain normalization to {method_name}")
        
        # Update cache key generation to use normalized domain
        cache_patterns = [
            (r'cache_key = f"domain_footprint_{domain}"', 
             'cache_key = f"domain_footprint_{domain.replace(".", "_")}"'),
        ]
        
        for old_pattern, new_pattern in cache_patterns:
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_pattern, content)
                print("   ✅ Updated cache key generation")
        
        # Add re import if needed
        if "import re" not in content:
            if "import asyncio" in content:
                content = content.replace("import asyncio", "import re\nimport asyncio")
                print("   ✅ Added re import")
        
        # Write back the updated content
        with open(discovery_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        files_to_update.append("discovery_engine.py")
    
    # Fix 2: Update pipeline to show better domain input guidance
    pipeline_file = Path("enhanced_run_pipeline_day2.py")
    if pipeline_file.exists():
        print("🔧 Updating pipeline domain handling...")
        
        with open(pipeline_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update any domain validation or display
        updates_made = False
        
        # Look for domain-related print statements and make them clearer
        domain_prints = [
            (r'print\(f"   Client Domain: \{[^}]+\}"\)', 
             'print(f"   Client Domain: {self.stage_manager.state.client_domain or \'Not specified\'}")'),
        ]
        
        for old_pattern, new_pattern in domain_prints:
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_pattern, content)
                updates_made = True
        
        if updates_made:
            with open(pipeline_file, 'w', encoding='utf-8') as f:
                f.write(content)
            files_to_update.append("enhanced_run_pipeline_day2.py")
            print("   ✅ Updated pipeline domain handling")
    
    # Clean up existing cache with old naming
    print("🧹 Cleaning up old cache files...")
    cache_dir = Path("data/discovery_cache")
    if cache_dir.exists():
        old_cache_files = []
        for cache_file in cache_dir.glob("*https*"):
            old_cache_files.append(cache_file)
        
        for old_file in old_cache_files:
            try:
                old_file.unlink()
                print(f"   ✅ Removed old cache: {old_file.name[:30]}...")
            except:
                pass
        
        if old_cache_files:
            print(f"   ✅ Cleaned {len(old_cache_files)} old cache files")
    
    print(f"\n🎉 Simple domain fix completed!")
    print(f"   ✅ Updated {len(files_to_update)} files")
    print("\n📝 Now you can use simple domain names:")
    print("   ✅ crescentgroveadvisors.com")
    print("   ✅ example.com") 
    print("   ✅ www.company.com (will be normalized to company.com)")
    print("   ❌ https://example.com (will work but gets normalized)")
    
    return len(files_to_update) > 0

def create_domain_examples():
    """Create example showing how to use simple domains"""
    
    example_content = '''# domain_input_examples.py
"""
Examples of how to use domain inputs after the simple domain fix
"""

# ✅ GOOD - Simple domain names (recommended)
good_domains = [
    "crescentgroveadvisors.com",
    "example.com",
    "mycompany.org",
    "client-site.net"
]

# ✅ ACCEPTABLE - These will be automatically normalized
acceptable_domains = [
    "www.crescentgroveadvisors.com",  # → crescentgroveadvisors.com
    "https://example.com",            # → example.com
    "https://www.mycompany.org/",     # → mycompany.org
]

# ❌ AVOID - These might cause issues
avoid_domains = [
    "https://example.com/some/path",  # Path will be stripped
    "subdomain.example.com",          # Will work but may not find main site tools
]

# Example usage in your audit:
if __name__ == "__main__":
    from enhanced_run_pipeline_day2 import EnhancedAuditPipelineDay2
    
    # Simple, clean domain input
    pipeline = EnhancedAuditPipelineDay2(
        client_name="Crescent Grove Advisors",
        client_domain="crescentgroveadvisors.com"  # ← Just the domain!
    )
    
    print("Domain will be automatically normalized and cached safely!")
'''
    
    example_file = Path("domain_input_examples.py")
    with open(example_file, 'w') as f:
        f.write(example_content)
    
    print("📝 Created domain_input_examples.py with usage examples")

if __name__ == "__main__":
    if fix_domain_input():
        create_domain_examples()
        print("\n🧪 Test with simple domain:")
        print('   pipeline = EnhancedAuditPipelineDay2("Client", "crescentgroveadvisors.com")')
    else:
        print("❌ No files were updated - check if files exist")

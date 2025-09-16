# fix_integration_datetime.py
"""
Quick fix for integration assessment datetime issues
Run this if you get datetime-related errors in integration assessment
"""

import sys
from pathlib import Path

def fix_integration_health_checker():
    """Fix datetime serialization issues in integration health checker"""
    
    health_checker_file = Path("core/integration_health_checker.py")
    if not health_checker_file.exists():
        print("❌ integration_health_checker.py not found")
        return False
    
    print("🔧 Applying datetime serialization fix...")
    
    # Read the current file
    with open(health_checker_file, 'r') as f:
        content = f.read()
    
    # Fix the datetime serialization in _save_cache method
    old_code = '''def _save_cache(self, cache_key: str, assessment_dict: Dict):
        """Save assessment to cache"""
        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'assessment': assessment_dict
        }
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2, default=str)'''
    
    new_code = '''def _save_cache(self, cache_key: str, assessment_dict: Dict):
        """Save assessment to cache"""
        # Convert datetime objects to strings for JSON serialization
        serializable_dict = {}
        for key, value in assessment_dict.items():
            if hasattr(value, 'isoformat'):  # datetime object
                serializable_dict[key] = value.isoformat()
            elif isinstance(value, list):
                # Handle lists that might contain non-serializable objects
                serializable_dict[key] = [str(item) if hasattr(item, '__dict__') else item for item in value]
            else:
                serializable_dict[key] = value
        
        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'assessment': serializable_dict
        }
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2, default=str)'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        # Write the fixed content back
        with open(health_checker_file, 'w') as f:
            f.write(content)
        
        print("✅ Integration health checker datetime fix applied")
        return True
    else:
        print("⚠️ Datetime fix not needed or already applied")
        return True

if __name__ == "__main__":
    if fix_integration_health_checker():
        print("✅ Fix completed successfully")
    else:
        print("❌ Fix failed")

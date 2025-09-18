# fix_streamlit_upload.py
"""
Quick fix for Streamlit file upload issue
The dashboard isn't actually saving uploaded CSV files
"""

import sys
from pathlib import Path

def fix_streamlit_upload():
    """Fix the file upload handling in streamlit_dashboard.py"""
    
    dashboard_file = Path("streamlit_dashboard.py")
    if not dashboard_file.exists():
        print("❌ streamlit_dashboard.py not found")
        return False
    
    print("🔧 Fixing Streamlit file upload handling...")
    
    # Read the current file
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the file upload section and check if it's actually saving files
    if "uploaded_file" in content and "temp_" in content:
        # The upload logic exists but isn't working
        # Let's add debug info to see what's happening
        
        # Add after the file upload section
        debug_code = '''
        # Debug: Actually save the uploaded file
        if uploaded_file is not None:
            # Create temp file properly
            import tempfile
            import os
            temp_path = f"data/temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Write the uploaded file content
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"✅ File saved to: {temp_path}")
            st.write(f"File size: {os.path.getsize(temp_path)} bytes")
            
            # Verify we can read it back
            try:
                import pandas as pd
                df = pd.read_csv(temp_path)
                st.write(f"Loaded {len(df)} rows from uploaded file")
                st.write("Preview:", df.head())
            except Exception as e:
                st.error(f"Error reading uploaded file: {e}")
        '''
        
        # This is a temporary fix - we need to see the actual streamlit code
        print("⚠️ Need to examine streamlit_dashboard.py content")
        print("The file upload logic exists but isn't working properly")
        
    else:
        print("❌ File upload logic not found in dashboard")
    
    return True

def bypass_streamlit_and_test_directly():
    """Bypass Streamlit and test with your real CGA data directly"""
    
    print("🚀 Creating direct test with your CGA tools...")
    
    # Create a proper CGA CSV file
    cga_tools_csv = """Tool Name,Category,Used By,Criticality
FactSet,Research,Portfolio Management,High
Morningstar Direct,Research,Portfolio Management,High  
Bloomberg Terminal,Research,Portfolio Management,High
Microsoft Excel,Research,Portfolio Management,Medium
Schwab PortfolioCenter,Portfolio Management,Portfolio Management,High
Orion Eclipse,Portfolio Management,Portfolio Management,High
Redtail CRM,CRM,Client Services,High
RightCapital,Financial Planning,Advisors,High
DocuSign,Operations,All,Medium
Microsoft Teams,Communication,All,High
Microsoft Outlook,Communication,All,High
Microsoft SharePoint,Collaboration,All,Medium
QuickBooks Desktop,Accounting,Operations,High
ADP Workforce Now,HR,Operations,Medium
Charles Schwab,Custodial,Trading,High
Fidelity Institutional,Custodial,Trading,High"""

    # Save to a test file
    test_file = Path("data/cga_real_tools.csv")
    with open(test_file, 'w') as f:
        f.write(cga_tools_csv)
    
    print(f"✅ Created {test_file} with your actual CGA tools")
    
    # Create test script
    test_script = f'''# test_with_cga_data.py
"""
Test the audit system directly with CGA data, bypassing Streamlit
"""
import asyncio
from enhanced_run_pipeline_day2 import EnhancedAuditPipelineDay2

async def main():
    print("🚀 Testing with Real CGA Data")
    
    # Create audit with CGA data
    pipeline = EnhancedAuditPipelineDay2(
        client_name="Crescent Grove Advisors (CGA)",
        client_domain="crescentgroveadvisors.com"
    )
    
    # Run complete audit with real CGA tools
    success = await pipeline.run_complete_enhanced_audit(
        csv_path="data/cga_real_tools.csv"
    )
    
    if success:
        print("🎉 CGA audit completed successfully!")
    else:
        print("❌ CGA audit failed")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    test_script_file = Path("test_with_cga_data.py")
    with open(test_script_file, 'w') as f:
        f.write(test_script)
    
    print(f"✅ Created {test_script_file}")
    print("\n🚀 Run this to test with your real CGA data:")
    print("   python test_with_cga_data.py")
    
    return True

if __name__ == "__main__":
    print("🔧 STREAMLIT FILE UPLOAD FIX")
    print("=" * 40)
    
    # First try to fix streamlit upload
    fix_streamlit_upload()
    
    print("\n" + "=" * 40)
    
    # Provide bypass solution
    bypass_streamlit_and_test_directly()
    
    print("\n📝 SUMMARY:")
    print("1. Streamlit file upload is broken - it's not actually saving your CSV files")
    print("2. Use the bypass script to test with your real CGA data")
    print("3. Once you verify it works, we can fix the Streamlit dashboard")
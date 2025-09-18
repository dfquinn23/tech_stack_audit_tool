# test_with_cga_data.py
"""
Test the audit system directly with CGA data, bypassing Streamlit
"""
import asyncio
import sys
from pathlib import Path
from enhanced_run_pipeline_day2 import EnhancedAuditPipelineDay2

async def main():
    print("=" * 60)
    print("TESTING WITH REAL CGA DATA")
    print("=" * 60)
    
    # First check if the CSV file exists
    csv_file = Path("data/cga_real_tools.csv")
    if not csv_file.exists():
        print(f"ERROR: {csv_file} not found!")
        return False
    
    print(f"Found CSV file: {csv_file}")
    print(f"File size: {csv_file.stat().st_size} bytes")
    
    # Show what's in the CSV
    with open(csv_file, 'r') as f:
        lines = f.readlines()
    print(f"CSV contains {len(lines)} lines:")
    for i, line in enumerate(lines[:5], 1):  # Show first 5 lines
        print(f"  {i}: {line.strip()}")
    
    print("\nCreating audit pipeline...")
    
    try:
        # Create audit with CGA data
        pipeline = EnhancedAuditPipelineDay2(
            client_name="Crescent Grove Advisors (CGA)",
            client_domain="crescentgroveadvisors.com"
        )
        
        print("Pipeline created successfully!")
        print(f"Audit ID: {pipeline.stage_manager.audit_id}")
        
        print("\nStarting complete audit...")
        
        # Run complete audit with real CGA tools
        success = await pipeline.run_complete_enhanced_audit(
            csv_path="data/cga_real_tools.csv"
        )
        
        if success:
            print("\n" + "=" * 60)
            print("CGA AUDIT COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            
            # Show what was generated
            output_dir = Path("output")
            if output_dir.exists():
                reports = list(output_dir.glob("*audit*"))
                if reports:
                    latest_report = max(reports, key=lambda x: x.stat().st_mtime)
                    print(f"Generated report: {latest_report}")
            
            return True
        else:
            print("\n" + "=" * 60)
            print("CGA AUDIT FAILED")
            print("=" * 60)
            return False
            
    except Exception as e:
        print(f"\nERROR during audit: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        if result:
            print("\nTest completed successfully!")
        else:
            print("\nTest failed!")
    except Exception as e:
        print(f"Script failed: {e}")
        import traceback
        traceback.print_exc()
#!/usr/bin/env python3
"""
Final System Validation Test
Confirms your complete Tech Stack Audit Tool is working properly
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

def check_system_health():
    """Quick health check of all components"""
    print("🏥 SYSTEM HEALTH CHECK")
    print("=" * 40)
    
    health_checks = []
    
    # Check 1: Core modules exist and import
    try:
        from core.stage_gate_manager import create_audit_session, AuditStage
        from core.discovery_engine import DiscoveryEngine
        from core.integration_health_checker import IntegrationHealthChecker
        from core.automation_opportunity_engine import AutomationOpportunityEngine
        health_checks.append(("Core Modules", True, "All core modules import successfully"))
    except Exception as e:
        health_checks.append(("Core Modules", False, f"Import error: {e}"))
    
    # Check 2: Enhanced pipeline imports
    try:
        from enhanced_run_pipeline_day2 import EnhancedAuditPipelineDay2
        health_checks.append(("Enhanced Pipeline", True, "Pipeline imports successfully"))
    except Exception as e:
        health_checks.append(("Enhanced Pipeline", False, f"Pipeline error: {e}"))
    
    # Check 3: Data directories exist
    required_dirs = ["data/audit_sessions", "data/discovery_cache", "data/integration_cache", "output"]
    missing_dirs = [d for d in required_dirs if not Path(d).exists()]
    if not missing_dirs:
        health_checks.append(("Directory Structure", True, "All required directories present"))
    else:
        health_checks.append(("Directory Structure", False, f"Missing: {missing_dirs}"))
    
    # Check 4: Sample data file
    if Path("data/tech_stack_list.csv").exists():
        health_checks.append(("Sample Data", True, "CSV file present"))
    else:
        health_checks.append(("Sample Data", False, "CSV file missing"))
    
    # Check 5: Environment configuration
    if Path(".env").exists():
        health_checks.append(("Environment", True, ".env file configured"))
    else:
        health_checks.append(("Environment", False, ".env file missing"))
    
    # Report results
    passed_checks = sum(1 for _, status, _ in health_checks if status)
    total_checks = len(health_checks)
    
    for component, status, message in health_checks:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {component}: {message}")
    
    print(f"\n📊 System Health: {passed_checks}/{total_checks} checks passed")
    return passed_checks == total_checks

async def test_sample_audit():
    from core.stage_gate_manager import AuditStage
    """Run a sample audit to validate the complete workflow"""
    print("\n🧪 SAMPLE AUDIT TEST")
    print("=" * 40)
    
    try:
        from enhanced_run_pipeline_day2 import EnhancedAuditPipelineDay2
        
        # Create test audit
        pipeline = EnhancedAuditPipelineDay2(
            client_name="Validation Test Client",
            client_domain="validation-test.com"
        )
        
        print(f"✅ Created audit session: {pipeline.stage_manager.audit_id}")
        
        # Test discovery stage with your sample data
        csv_path = "data/tech_stack_list.csv"
        if Path(csv_path).exists():
            success = await pipeline.execute_discovery_stage(csv_path, enable_auto_discovery=False)
            if success:
                print("✅ Discovery stage: PASSED")
                pipeline.stage_manager.advance_stage(AuditStage.ASSESSMENT)
                
                # Test assessment stage
                success = await pipeline.execute_assessment_stage_enhanced()
                if success:
                    print("✅ Assessment stage: PASSED")
                    pipeline.stage_manager.advance_stage(AuditStage.OPPORTUNITIES)
                    
                    # Test opportunities stage
                    success = await pipeline.execute_opportunities_stage_enhanced()
                    if success:
                        print("✅ Opportunities stage: PASSED")
                        pipeline.stage_manager.advance_stage(AuditStage.DELIVERY)
                        
                        # Test delivery stage
                        success = await pipeline.execute_delivery_stage_enhanced()
                        if success:
                            print("✅ Delivery stage: PASSED")
                            print(f"🎉 COMPLETE AUDIT PIPELINE: WORKING!")
                            
                            # Show results
                            summary = pipeline.stage_manager.export_summary()
                            print(f"\n📊 Audit Results:")
                            print(f"   • Tools analyzed: {summary['inventory_summary']['total_tools']}")
                            print(f"   • Integrations assessed: {summary['integration_summary']['total_integrations']}")
                            print(f"   • Opportunities identified: {summary['automation_summary']['total_opportunities']}")
                            
                            return True
        
        print("❌ Sample audit pipeline failed")
        return False
        
    except Exception as e:
        print(f"❌ Sample audit failed: {e}")
        return False

def show_next_steps():
    """Show recommended next steps"""
    print("\n🚀 NEXT STEPS")
    print("=" * 40)
    
    print("Your Tech Stack Audit Tool is ready for production! Here's what to do next:")
    print()
    print("1. 📝 **Configure for Your Clients**")
    print("   • Add your OpenAI API key to .env file")
    print("   • Customize opportunity templates in core/automation_opportunity_engine.py")
    print("   • Update financial assumptions (hourly rates, etc.)")
    print()
    print("2. 🎯 **Run Your First Real Audit**")
    print("   • Prepare client CSV with their tool list")
    print("   • Run: python enhanced_run_pipeline_day2.py")
    print("   • Review generated report in output/ directory")
    print()
    print("3. 📊 **Review System Capabilities**")
    print("   • Automated tool discovery via domain scanning")
    print("   • Systematic integration health assessment")
    print("   • Business process-driven gap analysis")
    print("   • ROI-quantified automation opportunities")
    print("   • Implementation-ready n8n workflow specs")
    print()
    print("4. 🔧 **Customization Options**")
    print("   • Add industry-specific opportunity templates")
    print("   • Customize integration patterns for client tools")
    print("   • Enhance discovery with additional API integrations")
    print("   • Create custom report sections")
    print()
    print("5. 📈 **Business Value**")
    print("   • 50% faster audits through systematic methodology")
    print("   • Zero repetition with persistent state management")
    print("   • Consistent quality across all client engagements")
    print("   • Quantified ROI for every recommendation")

async def main():
    """Run complete validation"""
    print("🚀 TECH STACK AUDIT TOOL - FINAL VALIDATION")
    print("=" * 60)
    print(f"Validation started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Health check
    system_healthy = check_system_health()
    
    if system_healthy:
        # Run sample audit
        audit_working = await test_sample_audit()
        
        if audit_working:
            print("\n🎉 VALIDATION COMPLETE: SYSTEM FULLY OPERATIONAL!")
            show_next_steps()
            return True
        else:
            print("\n⚠️ System healthy but audit pipeline needs attention")
            return False
    else:
        print("\n❌ System health issues detected - fix the failed checks above")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print(f"\n✅ Your Tech Stack Audit Tool is production-ready!")
        print(f"🚀 Start auditing clients with confidence!")
    else:
        print(f"\n🔧 Address the issues above, then re-run this validation")

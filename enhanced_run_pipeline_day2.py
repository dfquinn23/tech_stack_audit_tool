# enhanced_run_pipeline_day2.py
"""
Enhanced pipeline with Day 2 Integration Assessment components integrated
This version systematically handles Stage 2 (Assessment) with zero repetition
"""

from pydantic import Field
import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import Dict, List, Optional

# Environment setup
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except Exception:
    pass

from langchain_openai import ChatOpenAI
from crewai import Crew, Agent, Task

# Fix for CrewAI BaseTool import - try multiple import paths
try:
    from crewai_tools import BaseTool
except ImportError:
    try:
        from crewai.tools import BaseTool
    except ImportError:
        try:
            from crewai.tools.base_tool import BaseTool
        except ImportError:
            # Fallback - create a minimal BaseTool if none found
            class BaseTool:
                name: str = "Tool"
                description: str = "Base tool"

                def _run(self, *args, **kwargs):
                    return "Tool executed"

# Import stage-gate components
from core.stage_gate_manager import StageGateManager, AuditStage, create_audit_session, load_audit_session
from core.discovery_engine import DiscoveryEngine, enhance_existing_inventory
from core.integration_health_checker import (
    IntegrationHealthChecker,
    assess_tool_stack_integrations,
    IntegrationStatus
)
from core.integration_gap_analyzer import (
    IntegrationGapAnalyzer,
    analyze_integration_gaps,
    BusinessProcess
)
from core.input_handler import load_input

# Utility functions


def get_llm():
    """Get configured LLM instance"""
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        temperature=0
    )


def run_crew(crew: Crew):
    """Run a CrewAI crew and return results"""
    try:
        result = crew.kickoff()
        return result
    except Exception as e:
        print(f"⚠️ Crew execution failed: {e}")
        return f"Crew execution failed: {str(e)}"


def crew_to_text(crew_result) -> str:
    """Convert crew result to text string"""
    if isinstance(crew_result, str):
        return crew_result
    elif hasattr(crew_result, 'raw'):
        return crew_result.raw
    elif hasattr(crew_result, 'result'):
        return crew_result.result
    else:
        return str(crew_result)


class EnhancedAuditStateTool(BaseTool):
    """Enhanced CrewAI tool with Day 2 integration assessment capabilities"""
    name: str = "Enhanced Audit State Manager"
    description: str = "Access audit state, integration assessments, and gap analysis across pipeline stages"

    # Declare these as Pydantic fields but exclude them from serialization
    stage_manager: StageGateManager = Field(default=None, exclude=True)
    health_checker: IntegrationHealthChecker = Field(
        default=None, exclude=True)
    gap_analyzer: IntegrationGapAnalyzer = Field(default=None, exclude=True)

    def __init__(self, stage_manager: StageGateManager,
                 health_checker: IntegrationHealthChecker = None,
                 gap_analyzer: IntegrationGapAnalyzer = None, **kwargs):
        # Initialize with the field values
        super().__init__(
            stage_manager=stage_manager,
            health_checker=health_checker or IntegrationHealthChecker(),
            gap_analyzer=gap_analyzer or IntegrationGapAnalyzer(),
            **kwargs
        )

    def _run(self, action: str, **kwargs) -> str:
        """
        Enhanced actions including:
        - get_inventory: Return current tool inventory
        - get_integration_health: Get integration health summary
        - get_gap_analysis: Get integration gap analysis
        - add_integration_assessment: Add detailed integration assessment
        - get_business_process_analysis: Get analysis for specific business process
        - get_priority_gaps: Get prioritized integration gaps
        """
        try:
            if action == "get_inventory":
                return str(self.stage_manager.state.tool_inventory)

            elif action == "get_integration_health":
                integrations = self.stage_manager.state.integrations
                if not integrations:
                    return "No integration assessments available yet"

                summary = {
                    "total_integrations": len(integrations),
                    "healthy": len([i for i in integrations if i.get("status") == "healthy"]),
                    "degraded": len([i for i in integrations if i.get("status") == "degraded"]),
                    "broken": len([i for i in integrations if i.get("status") == "broken"]),
                    "missing": len([i for i in integrations if i.get("status") == "missing"])
                }
                return str(summary)

            elif action == "get_gap_analysis":
                gap_data = getattr(self.stage_manager.state,
                                   'gap_analysis', {})
                if not gap_data:
                    return "Gap analysis not yet performed"
                return str(gap_data)

            elif action == "add_integration_assessment":
                integration_data = kwargs.get("integration_data", {})
                if integration_data:
                    self.stage_manager.add_integration(integration_data)
                    return f"Added integration assessment: {integration_data.get('source_tool')} → {integration_data.get('target_tool')}"
                return "No integration data provided"

            elif action == "get_business_process_analysis":
                process_name = kwargs.get("process", "")
                return f"Business process analysis for {process_name} not yet implemented"

            elif action == "get_priority_gaps":
                gap_data = getattr(self.stage_manager.state,
                                   'gap_analysis', {})
                priority_gaps = gap_data.get('prioritized_gaps', [])
                return str(priority_gaps[:5])

            elif action == "get_firm_tools":
                return str(list(self.stage_manager.state.tool_inventory.keys()))

            else:
                return f"Unknown action: {action}. Available actions: get_inventory, get_integration_health, get_gap_analysis, add_integration_assessment, get_priority_gaps, get_firm_tools"

        except Exception as e:
            return f"Error executing {action}: {str(e)}"


class EnhancedAuditPipelineDay2:
    """Enhanced audit pipeline with systematic Day 2 Integration Assessment"""

    def __init__(self, audit_id: Optional[str] = None, client_name: Optional[str] = None,
                 client_domain: Optional[str] = None):
        self.llm = get_llm()

        # Load or create audit session
        if audit_id:
            self.stage_manager = load_audit_session(audit_id)
        else:
            if not client_name:
                raise ValueError("Must provide either audit_id or client_name")
            self.stage_manager = create_audit_session(
                client_name, client_domain)

        # Initialize assessment components
        self.discovery_engine = DiscoveryEngine()
        self.health_checker = IntegrationHealthChecker()
        self.gap_analyzer = IntegrationGapAnalyzer()

        # Create enhanced audit state tool for agents
        self.audit_tool = EnhancedAuditStateTool(
            self.stage_manager,
            self.health_checker,
            self.gap_analyzer
        )

        print(f"🚀 Initialized Enhanced Audit Pipeline (Day 2)")
        print(f"   Audit ID: {self.stage_manager.audit_id}")
        print(f"   Client: {self.stage_manager.state.client_name}")
        print(
            f"   Current Stage: {self.stage_manager.state.current_stage.name}")

    async def test_version_analysis(self):
        """Test version analysis on current tool inventory"""
        print("🔍 Running version analysis test...")

        # Create a simple test inventory if none exists
        if not self.stage_manager.state.tool_inventory:
            test_tools = {
                "Zoom": {"category": "Video", "users": ["All"], "criticality": "Medium"},
                "Slack": {"category": "Communication", "users": ["All"], "criticality": "High"},
                "Microsoft 365": {"category": "Productivity", "users": ["All"], "criticality": "High"}
            }

            for tool_name, tool_data in test_tools.items():
                self.stage_manager.add_tool(tool_name, tool_data)

            print(f"📋 Created test inventory with {len(test_tools)} tools")

        # Import and run version analysis
        from core.discovery_engine import analyze_tool_stack_versions

        current_tools = self.stage_manager.state.tool_inventory
        version_enhanced_tools = await analyze_tool_stack_versions(current_tools)

        # Show results
        print(f"\n📊 Version Analysis Results:")
        for tool_name, tool_data in version_enhanced_tools.items():
            if 'version_analysis' in tool_data:
                version_info = tool_data['version_analysis']
                print(
                    f"   • {tool_name}: {version_info['current_version']} → {version_info['latest_version']} ({version_info['comparison']['status']})")

        return True

    async def analyze_automation_features(self):
        """Analyze recent automation features for all tools in inventory"""
        print("\n💡 Analyzing Recent Automation Features...")

        current_tools = self.stage_manager.state.tool_inventory
        features_found_count = 0

        for tool_name, tool_data in current_tools.items():
            # Check for recent automation features
            feature_info = await self.discovery_engine.detect_recent_automation_features(tool_name)

            # Add feature intelligence to tool data
            if feature_info['features_found'] > 0:
                tool_data['automation_features'] = feature_info
                features_found_count += 1
                print(
                    f"   💡 {tool_name}: {feature_info['features_found']} automation opportunities identified")

        print(
            f"✅ Feature analysis complete: {features_found_count} tools with automation opportunities")

        # Save updated inventory
        self.stage_manager.save_state()
        return True

    async def execute_discovery_stage(self, csv_path: Optional[str] = None,
                                      enable_auto_discovery: bool = True) -> bool:
        """Stage 1: Discovery with automated enhancement + VERSION ANALYSIS"""

        if self.stage_manager.state.current_stage != AuditStage.DISCOVERY:
            print("⚠️ Not in Discovery stage. Use advance_to_stage() to navigate.")
            return False

        print("\n" + "="*60)
        print("🔍 STAGE 1: DISCOVERY")
        print("="*60)

        # Load initial tool inventory from CSV
        if csv_path and Path(csv_path).exists():
            print(f"📊 Loading initial inventory from {csv_path}")
            df = load_input(csv_path)

            initial_tools = {}
            for _, row in df.iterrows():
                tool_name = str(row["Tool Name"]).strip()
                initial_tools[tool_name] = {
                    'category': str(row["Category"]).strip(),
                    'users': [str(row["Used By"]).strip()],
                    'criticality': str(row["Criticality"]).strip(),
                    'discovery_method': 'manual_inventory'
                }

            # Update stage manager state
            for tool_name, tool_data in initial_tools.items():
                self.stage_manager.add_tool(tool_name, tool_data)

        # Enhanced discovery with automation
        if enable_auto_discovery and self.stage_manager.state.client_domain:
            print(
                f"🤖 Running automated discovery for {self.stage_manager.state.client_domain}")

            current_tools = self.stage_manager.state.tool_inventory
            enhanced_tools, discovery_summary = await enhance_existing_inventory(
                current_tools,
                self.stage_manager.state.client_domain
            )

            # Update with enhanced data
            self.stage_manager.state.tool_inventory = enhanced_tools
            self.stage_manager.save_state()

            print(f"✅ Discovery complete:")
            print(f"   • Total tools: {discovery_summary['total_tools']}")
            print(
                f"   • Auto-discovered: {discovery_summary['auto_discovered']}")
            print(f"   • API-enhanced: {discovery_summary['api_enhanced']}")

        # Version analysis
        print("\n🔍 Running version analysis...")
        from core.discovery_engine import analyze_tool_stack_versions

        current_tools = self.stage_manager.state.tool_inventory
        version_enhanced_tools = await analyze_tool_stack_versions(current_tools)

        # Update the tool inventory with version intelligence
        self.stage_manager.state.tool_inventory = version_enhanced_tools
        self.stage_manager.save_state()

        # Add automation feature analysis
        await self.analyze_automation_features()

        # Report version analysis results
        outdated_count = 0
        current_count = 0
        unknown_count = 0

        for tool_name, tool_data in version_enhanced_tools.items():
            if 'version_analysis' in tool_data:
                status = tool_data['version_analysis']['comparison']['status']
                if status == 'outdated':
                    outdated_count += 1
                elif status == 'current':
                    current_count += 1
                else:
                    unknown_count += 1

        print(f"✅ Version analysis complete:")
        print(f"   • Tools with updates available: {outdated_count}")
        print(f"   • Tools up-to-date: {current_count}")
        print(f"   • Tools with unknown status: {unknown_count}")

        # Validate Stage 1 gate
        can_advance, messages = self.stage_manager.check_stage_gate(
            AuditStage.ASSESSMENT)

        if can_advance:
            print(
                f"\n✅ Stage 1 Gate Passed: {len(self.stage_manager.state.tool_inventory)} tools catalogued with version intelligence")
            return True
        else:
            print(f"\n❌ Stage 1 Gate Failed:")
            for msg in messages:
                print(f"   • {msg}")
            return False

    async def execute_assessment_stage_enhanced(self) -> bool:
        """Stage 2: Enhanced Assessment with systematic integration analysis"""

        if self.stage_manager.state.current_stage != AuditStage.ASSESSMENT:
            print("⚠️ Not in Assessment stage. Complete Discovery first.")
            return False

        print("\n" + "="*60)
        print("🔗 STAGE 2: ENHANCED INTEGRATION ASSESSMENT")
        print("="*60)

        # Step 1: Systematic Integration Health Assessment
        print("🔍 Step 1: Comprehensive Integration Health Assessment...")

        assessments, health_summary = await assess_tool_stack_integrations(
            self.stage_manager.state.tool_inventory
        )

        print(f"✅ Health assessment completed:")
        print(
            f"   • Total integrations assessed: {health_summary.get('total_integrations_assessed', 0)}")
        print(
            f"   • Average health score: {health_summary.get('average_health_score', 0)}/100")
        print(
            f"   • Missing integrations: {health_summary.get('missing_integrations', 0)}")
        print(
            f"   • Broken integrations: {health_summary.get('broken_integrations', 0)}")

        # Step 2: Integration Gap Analysis
        print("\n🔍 Step 2: Business Process Integration Gap Analysis...")

        # Convert health assessments to integration records
        current_integrations = []
        for integration_key, assessment in assessments.items():
            integration_data = {
                "source_tool": assessment.source_tool,
                "target_tool": assessment.target_tool,
                "status": str(assessment.status),
                "integration_type": str(assessment.integration_type),
                "health_score": assessment.health_score,
                "business_criticality": assessment.business_criticality,
                "issues_found": assessment.issues_found,
                "recommendations": assessment.recommendations,
                "assessment_timestamp": assessment.assessment_timestamp.isoformat()
            }
            current_integrations.append(integration_data)
            self.stage_manager.add_integration(integration_data)

        # Run systematic gap analysis
        process_analyses, gap_report = analyze_integration_gaps(
            self.stage_manager.state.tool_inventory,
            current_integrations
        )

        print(f"✅ Gap analysis completed:")
        print(
            f"   • Integration gaps identified: {gap_report['analysis_summary']['total_gaps_identified']}")
        print(
            f"   • High priority gaps: {gap_report['analysis_summary']['high_priority_gaps']}")
        print(
            f"   • Estimated annual value: ${gap_report['analysis_summary']['total_estimated_annual_value']:,}")

        # Store gap analysis in stage manager state
        self.stage_manager.state.__dict__['gap_analysis'] = gap_report
        self.stage_manager.save_state()

        # Validate Stage 2 gate
        can_advance, messages = self.stage_manager.check_stage_gate(
            AuditStage.OPPORTUNITIES)

        if can_advance:
            print(f"\n✅ Enhanced Stage 2 Gate Passed:")
            print(f"   • {len(assessments)} integration assessments completed")
            print(
                f"   • {gap_report['analysis_summary']['total_gaps_identified']} gaps identified")
            print(
                f"   • ${gap_report['analysis_summary']['total_estimated_annual_value']:,} opportunity value quantified")
            return True
        else:
            print(f"\n❌ Enhanced Stage 2 Gate Failed:")
            for msg in messages:
                print(f"   • {msg}")
            return False

    async def execute_opportunities_stage_enhanced(self) -> bool:
        """Stage 3: Enhanced Opportunities with gap-driven automation identification"""

        if self.stage_manager.state.current_stage != AuditStage.OPPORTUNITIES:
            print("⚠️ Not in Opportunities stage. Complete Assessment first.")
            return False

        print("\n" + "="*60)
        print("🤖 STAGE 3: ENHANCED AUTOMATION OPPORTUNITIES")
        print("="*60)

        # Import automation opportunity engine
        from core.automation_opportunity_engine import generate_automation_opportunities

        # Get gap analysis data from previous stage
        gap_analysis = getattr(self.stage_manager.state, 'gap_analysis', {})
        if not gap_analysis:
            print("⚠️ No gap analysis data available. Re-run Stage 2.")
            return False

        # Generate automation opportunities based on gap analysis
        integration_gaps = gap_analysis.get('prioritized_gaps', [])

        opportunities, roadmap = generate_automation_opportunities(
            self.stage_manager.state.tool_inventory,
            integration_gaps,
            self.stage_manager.state.integrations
        )

        print(f"✅ Automation opportunities generated:")
        print(f"   • Total opportunities: {len(opportunities)}")
        print(
            f"   • High priority: {len([o for o in opportunities if o.priority_tier == 'high'])}")
        print(
            f"   • Estimated annual savings: ${roadmap['roadmap_summary']['total_estimated_annual_savings']:,}")

        # Add opportunities to stage manager
        for opportunity in opportunities:
            opp_data = {
                "name": opportunity.name,
                "priority_score": opportunity.total_score,
                "roi_estimate": opportunity.annual_cost_savings,
                "implementation_effort": opportunity.complexity.value,
                "n8n_workflow": {
                    "name": opportunity.n8n_workflow.name,
                    "trigger_type": opportunity.n8n_workflow.trigger_type,
                    "description": opportunity.n8n_workflow.description
                }
            }
            self.stage_manager.add_automation_opportunity(opp_data)

        # Validate Stage 3 gate
        can_advance, messages = self.stage_manager.check_stage_gate(
            AuditStage.DELIVERY)

        if can_advance:
            print(
                f"\n✅ Stage 3 Gate Passed: {len(opportunities)} opportunities identified")
            return True
        else:
            print(f"\n❌ Stage 3 Gate Failed:")
            for msg in messages:
                print(f"   • {msg}")
            return False

    async def execute_delivery_stage_enhanced(self) -> bool:
        """Stage 4: Enhanced Delivery with comprehensive assessment reporting"""

        if self.stage_manager.state.current_stage != AuditStage.DELIVERY:
            print("⚠️ Not in Delivery stage. Complete Opportunities first.")
            return False

        print("\n" + "="*60)
        print("📋 STAGE 4: ENHANCED DELIVERY")
        print("="*60)

        # Generate report
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        report_file = output_dir / \
            f"enhanced_audit_report_{self.stage_manager.audit_id}_{timestamp}.md"

        # Get gap analysis data
        gap_analysis = getattr(self.stage_manager.state, 'gap_analysis', {})

        # Generate comprehensive report
        report_content = f"""# Enhanced Tech Stack Audit Report

_Client: {self.stage_manager.state.client_name}_
_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_
_Audit ID: {self.stage_manager.audit_id}_

## Executive Summary

**Key Findings:**
- **Tools Assessed:** {len(self.stage_manager.state.tool_inventory)}
- **Integrations Analyzed:** {len(self.stage_manager.state.integrations)}
- **Gaps Identified:** {gap_analysis.get('analysis_summary', {}).get('total_gaps_identified', 0)}
- **Automation Opportunities:** {len(self.stage_manager.state.automation_opportunities)}
- **Estimated Annual Value:** ${gap_analysis.get('analysis_summary', {}).get('total_estimated_annual_value', 0):,}
- **Time Savings Potential:** {gap_analysis.get('analysis_summary', {}).get('total_annual_time_savings_hours', 0):,} hours/year

## Tool Inventory

The following tools were identified in your technology stack:

"""

        # Add tool details
        for tool_name, tool_data in self.stage_manager.state.tool_inventory.items():
            report_content += f"### {tool_name}\n"
            report_content += f"- **Category:** {tool_data.get('category', 'Unknown')}\n"
            report_content += f"- **Users:** {', '.join(tool_data.get('users', ['Unknown']))}\n"
            report_content += f"- **Criticality:** {tool_data.get('criticality', 'Unknown')}\n"
            report_content += f"- **Discovery Method:** {tool_data.get('discovery_method', 'Unknown')}\n\n"

        # Add integration summary
        report_content += f"""## Integration Assessment

**Summary:**
- Total integrations assessed: {len(self.stage_manager.state.integrations)}
- Integration gaps identified: {gap_analysis.get('analysis_summary', {}).get('total_gaps_identified', 0)}
- High priority gaps: {gap_analysis.get('analysis_summary', {}).get('high_priority_gaps', 0)}

## Automation Opportunities

We identified {len(self.stage_manager.state.automation_opportunities)} automation opportunities:

"""

        # Add opportunities
        for i, opp in enumerate(self.stage_manager.state.automation_opportunities, 1):
            report_content += f"{i}. **{opp.get('name', 'Unknown Opportunity')}**\n"
            report_content += f"   - Priority Score: {opp.get('priority_score', 0)}\n"
            report_content += f"   - Estimated Annual Savings: ${opp.get('roi_estimate', 0):,}\n"
            report_content += f"   - Implementation Effort: {opp.get('implementation_effort', 'Unknown')}\n\n"

        report_content += f"""
## Methodology

This report was generated using a systematic Stage-Gate audit methodology with:
- Automated tool discovery and API health checking
- Comprehensive integration health assessment
- Business process-driven gap analysis
- Template-based automation opportunity identification
- Data-driven ROI estimation

For questions about this assessment, contact the audit team with reference ID: {self.stage_manager.audit_id}
"""

        # Save report
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"📄 Enhanced report generated: {report_file}")

        # Mark delivery complete
        self.stage_manager.state.stage_completion[4] = True
        self.stage_manager.save_state()

        print(f"✅ Stage 4 Complete: Enhanced audit delivered")
        return True

    async def run_complete_enhanced_audit(self, csv_path: str = None, auto_advance: bool = True) -> bool:
        """Run the complete enhanced audit pipeline"""

        print(f"🚀 Starting Complete Enhanced Audit Pipeline")
        print(f"   Client: {self.stage_manager.state.client_name}")
        print(f"   Audit ID: {self.stage_manager.audit_id}")

        # Stage 1: Discovery
        success = await self.execute_discovery_stage(csv_path, enable_auto_discovery=True)
        if success:
            self.stage_manager.advance_stage(AuditStage.ASSESSMENT)
        elif not auto_advance:
            return False

        # Stage 2: Enhanced Assessment
        success = await self.execute_assessment_stage_enhanced()
        if success:
            self.stage_manager.advance_stage(AuditStage.OPPORTUNITIES)
        elif not auto_advance:
            return False

        # Stage 3: Enhanced Opportunities
        success = await self.execute_opportunities_stage_enhanced()
        if success:
            self.stage_manager.advance_stage(AuditStage.DELIVERY)
        elif not auto_advance:
            return False

        # Stage 4: Enhanced Delivery
        success = await self.execute_delivery_stage_enhanced()

        if success:
            print("\n🎉 ENHANCED AUDIT PIPELINE COMPLETED SUCCESSFULLY!")

            # Get final summary
            summary = self.stage_manager.export_summary()
            gap_analysis = getattr(
                self.stage_manager.state, 'gap_analysis', {})

            print(f"\n📊 Enhanced Final Results:")
            print(
                f"   • Tools Analyzed: {summary['inventory_summary']['total_tools']}")
            print(
                f"   • Integrations Assessed: {summary['integration_summary']['total_integrations']}")
            print(
                f"   • Integration Gaps: {gap_analysis.get('analysis_summary', {}).get('total_gaps_identified', 0)}")
            print(
                f"   • Automation Opportunities: {summary['automation_summary']['total_opportunities']}")
            print(
                f"   • Estimated Annual Value: ${gap_analysis.get('analysis_summary', {}).get('total_estimated_annual_value', 0):,}")

        return success

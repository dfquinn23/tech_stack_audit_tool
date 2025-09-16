# enhanced_run_pipeline_day2.py
"""
Enhanced pipeline with Day 2 Integration Assessment components integrated
This version systematically handles Stage 2 (Assessment) with zero repetition
"""

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
from crewai_tools import BaseTool

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

# Import your existing agents
from agents.research_agent import get_research_agent, get_research_task
from agents.summarizer_agent import get_summarizer_agent, get_summarizer_task
from agents.audit_agent import get_audit_agent, get_audit_task
from agents.integration_agent import get_integration_agent, get_integration_task
from agents.report_writer_agent import get_report_writer_agent, get_report_section_task

# Utility functions from your original pipeline
from run_pipeline import run_crew, crew_to_text, parse_bullet_list, get_llm

class EnhancedAuditStateTool(BaseTool):
    """Enhanced CrewAI tool with Day 2 integration assessment capabilities"""
    name: str = "Enhanced Audit State Manager"
    description: str = "Access audit state, integration assessments, and gap analysis across pipeline stages"
    
    def __init__(self, stage_manager: StageGateManager, 
                 health_checker: IntegrationHealthChecker = None,
                 gap_analyzer: IntegrationGapAnalyzer = None):
        super().__init__()
        self.stage_manager = stage_manager
        self.health_checker = health_checker or IntegrationHealthChecker()
        self.gap_analyzer = gap_analyzer or IntegrationGapAnalyzer()
    
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
                # This would be populated during assessment stage
                gap_data = getattr(self.stage_manager.state, 'gap_analysis', {})
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
                # Return analysis for specific business process
                return f"Business process analysis for {process_name} not yet implemented"
            
            elif action == "get_priority_gaps":
                # Return prioritized integration gaps
                gap_data = getattr(self.stage_manager.state, 'gap_analysis', {})
                priority_gaps = gap_data.get('prioritized_gaps', [])
                return str(priority_gaps[:5])  # Top 5 priority gaps
            
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
            self.stage_manager = create_audit_session(client_name, client_domain)
        
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
        print(f"   Current Stage: {self.stage_manager.state.current_stage.name}")
    
    async def execute_discovery_stage(self, csv_path: Optional[str] = None, 
                                    enable_auto_discovery: bool = True) -> bool:
        """Stage 1: Discovery with automated enhancement (same as Day 1)"""
        
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
            print(f"🤖 Running automated discovery for {self.stage_manager.state.client_domain}")
            
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
            print(f"   • Auto-discovered: {discovery_summary['auto_discovered']}")
            print(f"   • API-enhanced: {discovery_summary['api_enhanced']}")
        
        # Validate Stage 1 gate
        can_advance, messages = self.stage_manager.check_stage_gate(AuditStage.ASSESSMENT)
        
        if can_advance:
            print(f"\n✅ Stage 1 Gate Passed: {len(self.stage_manager.state.tool_inventory)} tools catalogued")
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
        print(f"   • Total integrations assessed: {health_summary['total_integrations_assessed']}")
        print(f"   • Average health score: {health_summary['average_health_score']}/100")
        print(f"   • Missing integrations: {health_summary['missing_integrations']}")
        print(f"   • Broken integrations: {health_summary['broken_integrations']}")
        
        # Step 2: Integration Gap Analysis
        print("\n🔍 Step 2: Business Process Integration Gap Analysis...")
        
        # Convert health assessments to integration records
        current_integrations = []
        for integration_key, assessment in assessments.items():
            integration_data = {
                "source_tool": assessment.source_tool,
                "target_tool": assessment.target_tool,
                "status": assessment.status.value,
                "integration_type": assessment.integration_type.value,
                "health_score": assessment.health_score,
                "business_criticality": assessment.business_criticality,
                "issues_found": assessment.issues_found,
                "recommendations": assessment.recommendations,
                "assessment_timestamp": assessment.assessment_timestamp.isoformat()
            }
            current_integrations.append(integration_data)
            
            # Add to stage manager
            self.stage_manager.add_integration(integration_data)
        
        # Run systematic gap analysis
        process_analyses, gap_report = analyze_integration_gaps(
            self.stage_manager.state.tool_inventory,
            current_integrations
        )
        
        print(f"✅ Gap analysis completed:")
        print(f"   • Integration gaps identified: {gap_report['analysis_summary']['total_gaps_identified']}")
        print(f"   • High priority gaps: {gap_report['analysis_summary']['high_priority_gaps']}")
        print(f"   • Estimated annual value: ${gap_report['analysis_summary']['total_estimated_annual_value']:,}")
        
        # Store gap analysis in stage manager state
        self.stage_manager.state.__dict__['gap_analysis'] = gap_report
        self.stage_manager.save_state()
        
        # Step 3: CrewAI Agent Analysis with Enhanced Context
        print("\n🤖 Step 3: AI Agent Integration Analysis...")
        
        # Enhanced audit agent with systematic assessment data
        audit_agent = self.get_enhanced_audit_agent()
        
        # Create comprehensive assessment task
        assessment_task = Task(
            description=dedent(f"""
                Analyze the comprehensive integration assessment results and provide strategic recommendations.
                
                Your analysis should leverage:
                - Systematic health assessment of {len(assessments)} integrations
                - Business process gap analysis across {len(process_analyses)} processes
                - Priority gaps with estimated ${gap_report['analysis_summary']['total_estimated_annual_value']:,} annual value
                
                Focus on:
                1. Critical integration health issues requiring immediate attention
                2. High-value integration gaps with business impact analysis
                3. Quick wins with high value-to-complexity ratios
                4. Risk assessment of current integration state
                5. Strategic recommendations for integration roadmap
                
                Use the Enhanced Audit State Manager to access:
                - get_integration_health: Current integration health summary
                - get_gap_analysis: Detailed gap analysis results
                - get_priority_gaps: Top priority integration opportunities
                
                Provide actionable recommendations with business justification.
            """),
            agent=audit_agent,
            expected_output="Strategic integration assessment with prioritized recommendations and business impact analysis"
        )
        
        assessment_crew = Crew(agents=[audit_agent], tasks=[assessment_task], verbose=True)
        
        try:
            assessment_result = run_crew(assessment_crew)
            assessment_text = crew_to_text(assessment_result)
            print(f"\n📊 AI Agent Integration Analysis:")
            print("-" * 50)
            print(assessment_text[:1000] + "..." if len(assessment_text) > 1000 else assessment_text)
            
            # Store analysis result
            self.stage_manager.state.__dict__['ai_assessment_analysis'] = assessment_text
            self.stage_manager.save_state()
            
        except Exception as e:
            print(f"⚠️ AI Agent assessment failed: {e}")
        
        # Step 4: Validate Stage 2 gate with enhanced criteria
        print(f"\n🚪 Validating Enhanced Stage 2 Gate...")
        
        can_advance, messages = self.stage_manager.check_stage_gate(AuditStage.OPPORTUNITIES)
        
        # Additional validation for enhanced assessment
        if can_advance:
            # Check if we have comprehensive assessment data
            if len(assessments) < 3:
                can_advance = False
                messages.append("Need at least 3 integration assessments")
            
            if gap_report['analysis_summary']['total_gaps_identified'] == 0:
                can_advance = False
                messages.append("Gap analysis found no opportunities - review process")
        
        if can_advance:
            print(f"✅ Enhanced Stage 2 Gate Passed:")
            print(f"   • {len(assessments)} integration assessments completed")
            print(f"   • {gap_report['analysis_summary']['total_gaps_identified']} gaps identified")
            print(f"   • ${gap_report['analysis_summary']['total_estimated_annual_value']:,} opportunity value quantified")
            return True
        else:
            print(f"❌ Enhanced Stage 2 Gate Failed:")
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
        
        # Get gap analysis data from previous stage
        gap_analysis = getattr(self.stage_manager.state, 'gap_analysis', {})
        if not gap_analysis:
            print("⚠️ No gap analysis data available. Re-run Stage 2.")
            return False
        
        # Enhanced integration agent with gap analysis context
        integration_agent = self.get_enhanced_integration_agent()
        
        # Create gap-driven automation analysis task
        opportunities_task = Task(
            description=dedent(f"""
                Design n8n automation workflows based on systematic integration gap analysis.
                
                Available Context:
                - {gap_analysis['analysis_summary']['total_gaps_identified']} integration gaps identified
                - {gap_analysis['analysis_summary']['high_priority_gaps']} high-priority opportunities  
                - ${gap_analysis['analysis_summary']['total_estimated_annual_value']:,} potential annual value
                - Business process analysis across 6+ workflows
                
                Your comprehensive analysis should:
                1. Review the priority gaps from gap analysis (use get_priority_gaps)
                2. Design specific n8n automation workflows for top 5-8 opportunities
                3. Focus on quick wins with high value-to-complexity ratios
                4. Create detailed workflow specifications with triggers, nodes, and data flows
                5. Estimate ROI and implementation effort for each workflow
                6. Prioritize by business impact and feasibility
                
                For each automation opportunity, provide:
                - Clear name and business value proposition
                - Specific n8n workflow design (triggers, key nodes, data transformations)
                - Priority score (1-15: capability + value + feasibility)
                - ROI estimate with time savings and cost reduction
                - Implementation effort and prerequisites
                - Risk assessment and mitigation strategies
                
                Use the Enhanced Audit State Manager to:
                - Access priority gaps: get_priority_gaps
                - Review integration health: get_integration_health
                - Add opportunities: add_opportunity action
                
                Focus on automation workflows that address the highest-value integration gaps
                identified in the systematic gap analysis.
            """),
            agent=integration_agent,
            expected_output="Comprehensive n8n automation roadmap with 5-8 prioritized workflows based on gap analysis"
        )
        
        opportunities_crew = Crew(agents=[integration_agent], tasks=[opportunities_task], verbose=True)
        
        try:
            opportunities_result = run_crew(opportunities_crew)
            opportunities_text = crew_to_text(opportunities_result)
            print(f"\n🔗 Enhanced Automation Opportunities Analysis:")
            print(opportunities_text)
            
        except Exception as e:
            print(f"⚠️ Enhanced opportunities analysis failed: {e}")
            return False
        
        # Validate Stage 3 gate
        can_advance, messages = self.stage_manager.check_stage_gate(AuditStage.DELIVERY)
        
        if can_advance:
            print(f"\n✅ Stage 3 Gate Passed: {len(self.stage_manager.state.automation_opportunities)} opportunities identified")
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
        
        # Enhanced report writer with comprehensive context
        report_writer = self.get_enhanced_report_writer()
        
        # Get gap analysis and assessment data
        gap_analysis = getattr(self.stage_manager.state, 'gap_analysis', {})
        ai_analysis = getattr(self.stage_manager.state, 'ai_assessment_analysis', 'No AI analysis available')
        
        # Generate comprehensive enhanced audit report
        report_task = Task(
            description=dedent(f"""
                Generate a comprehensive tech stack audit report with systematic integration assessment.
                
                Report Components:
                1. Executive Summary with key findings and ROI projections
                2. Tool Inventory Analysis ({len(self.stage_manager.state.tool_inventory)} tools)
                3. Integration Health Assessment ({len(self.stage_manager.state.integrations)} integrations)
                4. Business Process Gap Analysis ({gap_analysis.get('analysis_summary', {}).get('total_gaps_identified', 0)} gaps)
                5. Automation Opportunities Roadmap ({len(self.stage_manager.state.automation_opportunities)} opportunities)
                6. Implementation Plan with priorities and timelines
                7. ROI Analysis and Business Case
                
                Key Data Points to Include:
                - Total estimated annual value: ${gap_analysis.get('analysis_summary', {}).get('total_estimated_annual_value', 0):,}
                - Time savings: {gap_analysis.get('analysis_summary', {}).get('total_annual_time_savings_hours', 0):,} hours annually
                - Integration health summary with critical issues
                - Quick wins vs. strategic initiatives categorization
                - Risk assessment and mitigation strategies
                
                Use the Enhanced Audit State Manager to access:
                - Complete tool inventory and discovery details
                - Integration health assessments and gap analysis
                - Prioritized automation opportunities with ROI data
                
                Structure the report for multiple audiences:
                - C-level: Focus on business impact, ROI, and strategic recommendations
                - IT teams: Technical implementation details and integration specifications
                - Operations: Process improvements and efficiency gains
                
                Follow McKinsey MECE framework with clear recommendations and next steps.
            """),
            agent=report_writer,
            expected_output="Comprehensive audit report with systematic integration assessment and data-driven recommendations"
        )
        
        delivery_crew = Crew(agents=[report_writer], tasks=[report_task], verbose=True)
        
        try:
            report_result = run_crew(delivery_crew)
            report_text = crew_to_text(report_result)
            
            # Save enhanced report
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            report_file = output_dir / f"enhanced_audit_report_{self.stage_manager.audit_id}_{timestamp}.md"
            
            # Add executive summary with key metrics
            enhanced_report = f"""# Enhanced Tech Stack Audit Report
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

---

{report_text}

## Methodology Note

This report was generated using a systematic Stage-Gate audit methodology with:
- Automated tool discovery and API health checking
- Comprehensive integration health assessment
- Business process-driven gap analysis
- AI-assisted opportunity identification and prioritization
- Data-driven ROI estimation and business case development

For questions about this assessment, contact the audit team with reference ID: {self.stage_manager.audit_id}
"""
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(enhanced_report)
            
            print(f"\n📄 Enhanced report generated: {report_file}")
            
        except Exception as e:
            print(f"⚠️ Enhanced report generation failed: {e}")
            return False
        
        # Final validation and completion
        print(f"\n✅ Stage 4 Complete: Enhanced audit delivered")
        self.stage_manager.state.stage_completion[4] = True
        self.stage_manager.save_state()
        
        return True
    
    def get_enhanced_audit_agent(self) -> Agent:
        """Get audit agent enhanced with integration assessment capabilities"""
        return Agent(
            role="Senior Integration Assessment Analyst",
            goal="Analyze integration health and business impact using systematic assessment data",
            backstory=dedent("""
                You are a senior consultant specializing in enterprise integration analysis.
                You combine systematic health assessments, gap analysis, and business process understanding
                to provide strategic recommendations for technology integration improvements.
                You excel at translating technical integration issues into business impact and ROI.
            """),
            tools=[self.audit_tool],
            memory=True,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def get_enhanced_integration_agent(self) -> Agent:
        """Get integration agent enhanced with gap analysis context"""
        return Agent(
            role="Automation Strategy Architect",
            goal="Design data-driven n8n automation workflows based on systematic gap analysis",
            backstory=dedent("""
                You are an automation specialist who designs n8n workflows based on systematic
                integration gap analysis. You prioritize opportunities by business value and feasibility,
                focusing on workflows that address the highest-impact integration gaps identified
                through comprehensive business process analysis.
            """),
            tools=[self.audit_tool],
            memory=True,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def get_enhanced_report_writer(self) -> Agent:
        """Get report writer enhanced with comprehensive assessment context"""
        return Agent(
            role="Senior Audit Report Writer",
            goal="Generate data-driven audit reports with systematic integration assessment insights",
            backstory=dedent("""
                You are a senior consultant who creates comprehensive audit reports based on
                systematic integration assessments. Your reports combine technical analysis with
                business impact, providing clear ROI justification and actionable recommendations
                based on data-driven gap analysis and opportunity identification.
            """),
            tools=[self.audit_tool],
            memory=True,
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    async def run_complete_enhanced_audit(self, csv_path: str = None, auto_advance: bool = True) -> bool:
        """Run the complete enhanced audit pipeline with Day 2 integration assessment"""
        
        print(f"🚀 Starting Complete Enhanced Audit Pipeline (Day 2)")
        print(f"   Client: {self.stage_manager.state.client_name}")
        print(f"   Audit ID: {self.stage_manager.audit_id}")
        
        # Stage 1: Discovery (same as Day 1)
        success = await self.execute_discovery_stage(csv_path, enable_auto_discovery=True)
        if not success and not auto_advance:
            return False
        elif success:
            self.stage_manager.advance_stage(AuditStage.ASSESSMENT)
        
        # Stage 2: Enhanced Assessment with systematic integration analysis
        success = await self.execute_assessment_stage_enhanced()
        if not success and not auto_advance:
            return False
        elif success:
            self.stage_manager.advance_stage(AuditStage.OPPORTUNITIES)
        
        # Stage 3: Enhanced Opportunities with gap-driven automation
        success = await self.execute_opportunities_stage_enhanced()
        if not success and not auto_advance:
            return False
        elif success:
            self.stage_manager.advance_stage(AuditStage.DELIVERY)
        
        # Stage 4: Enhanced Delivery with comprehensive reporting
        success = await self.execute_delivery_stage_enhanced()
        
        if success:
            print("\n🎉 ENHANCED AUDIT PIPELINE COMPLETED SUCCESSFULLY!")
            
            # Get final summary with enhanced metrics
            summary = self.stage_manager.export_summary()
            gap_analysis = getattr(self.stage_manager.state, 'gap_analysis', {})
            
            print(f"\n📊 Enhanced Final Results:")
            print(f"   • Tools Analyzed: {summary['inventory_summary']['total_tools']}")
            print(f"   • Integrations Assessed: {summary['integration_summary']['total_integrations']}")
            print(f"   • Integration Gaps Identified: {gap_analysis.get('analysis_summary', {}).get('total_gaps_identified', 0)}")
            print(f"   • Automation Opportunities: {summary['automation_summary']['total_opportunities']}")
            print(f"   • Estimated Annual ROI: ${gap_analysis.get('analysis_summary', {}).get('total_estimated_annual_value', 0):,}")
            
            print(f"\n🎯 Key Differentiators:")
            print(f"   ✅ Systematic integration health assessment")
            print(f"   ✅ Business process-driven gap analysis") 
            print(f"   ✅ Data-driven automation opportunity identification")
            print(f"   ✅ Quantified ROI and business impact analysis")
            print(f"   ✅ Zero repetition through stage-gate architecture")
        
        return success

async def main():
    """Main execution function with Day 2 enhancements"""
    
    # Configuration
    client_name = "Enhanced Demo Asset Management Firm"
    client_domain = "demo-firm.com"  # Optional, enables auto-discovery
    csv_path = "data/tech_stack_list.csv"  # Your existing CSV
    
    try:
        # Create and run enhanced pipeline with Day 2 capabilities
        pipeline = EnhancedAuditPipelineDay2(
            client_name=client_name, 
            client_domain=client_domain
        )
        
        # Run complete enhanced audit
        success = await pipeline.run_complete_enhanced_audit(csv_path=csv_path, auto_advance=True)
        
        if success:
            print(f"\n✅ Enhanced audit completed successfully!")
            print(f"   Audit ID: {pipeline.stage_manager.audit_id}")
            print(f"   Enhanced report saved in: output/")
            print(f"   Integration assessment data: data/integration_cache/")
        else:
            print(f"\n❌ Enhanced audit pipeline failed at some stage")
            
    except KeyboardInterrupt:
        print("\n⚠️ Enhanced pipeline interrupted by user")
    except Exception as e:
        print(f"\n❌ Enhanced pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
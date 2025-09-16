# core/integration_gap_analyzer.py
"""
Systematic gap analysis for identifying missing but valuable integrations
Uses business process analysis and industry best practices to identify opportunities
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

class BusinessProcess(Enum):
    CLIENT_ONBOARDING = "client_onboarding"
    PORTFOLIO_MANAGEMENT = "portfolio_management" 
    RESEARCH_WORKFLOW = "research_workflow"
    CLIENT_REPORTING = "client_reporting"
    COMPLIANCE_MONITORING = "compliance_monitoring"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    TRADE_EXECUTION = "trade_execution"
    CLIENT_COMMUNICATION = "client_communication"
    DOCUMENT_MANAGEMENT = "document_management"
    BILLING_OPERATIONS = "billing_operations"

@dataclass
class IntegrationGap:
    source_tool: str
    target_tool: str
    business_process: BusinessProcess
    gap_type: str  # "missing_integration", "inefficient_process", "manual_workflow"
    current_state: str  # Description of how this is currently handled
    proposed_integration: str  # Description of proposed integration
    business_value: int  # 1-10 score
    implementation_complexity: int  # 1-10 score  
    annual_time_savings_hours: int
    estimated_annual_value: int  # Dollar value
    prerequisites: List[str]
    risks: List[str]

@dataclass 
class ProcessAnalysis:
    process: BusinessProcess
    tools_involved: List[str]
    current_efficiency_score: int  # 1-10
    pain_points: List[str]
    integration_gaps: List[IntegrationGap]
    automation_potential: int  # 1-10

class IntegrationGapAnalyzer:
    """Systematic analysis of integration gaps and automation opportunities"""
    
    def __init__(self):
        # Define business process workflows and expected tool interactions
        self.process_workflows = {
            BusinessProcess.CLIENT_ONBOARDING: {
                "typical_tools": ["wealth box", "schwab", "right capital", "365"],
                "expected_integrations": [
                    ("wealth box", "schwab"),
                    ("wealth box", "right capital"), 
                    ("wealth box", "365"),
                    ("right capital", "365")
                ],
                "key_data_flows": [
                    "client information from CRM to custodian",
                    "planning data from planning tool to CRM",
                    "documents from planning to email/storage"
                ]
            },
            
            BusinessProcess.PORTFOLIO_MANAGEMENT: {
                "typical_tools": ["advent axys", "factset", "bloomberg", "schwab"],
                "expected_integrations": [
                    ("schwab", "advent axys"),
                    ("factset", "advent axys"),
                    ("bloomberg", "advent axys")
                ],
                "key_data_flows": [
                    "positions from custodian to portfolio system",
                    "market data from research tools to portfolio system",
                    "trade orders from portfolio system to custodian"
                ]
            },
            
            BusinessProcess.RESEARCH_WORKFLOW: {
                "typical_tools": ["factset", "bloomberg", "365", "wealth box"],
                "expected_integrations": [
                    ("factset", "365"),
                    ("bloomberg", "365"),
                    ("factset", "wealth box"),
                    ("bloomberg", "wealth box")
                ],
                "key_data_flows": [
                    "research reports from data providers to email/storage",
                    "investment ideas from research to client notes",
                    "market alerts from data providers to communication tools"
                ]
            },
            
            BusinessProcess.CLIENT_REPORTING: {
                "typical_tools": ["advent axys", "wealth box", "365", "right capital"],
                "expected_integrations": [
                    ("advent axys", "365"),
                    ("advent axys", "wealth box"),
                    ("right capital", "365"),
                    ("right capital", "wealth box")
                ],
                "key_data_flows": [
                    "performance data from portfolio system to reporting",
                    "client information from CRM to reports",
                    "financial plans from planning tool to reports"
                ]
            },
            
            BusinessProcess.CLIENT_COMMUNICATION: {
                "typical_tools": ["wealth box", "365", "zoom", "right capital"],
                "expected_integrations": [
                    ("zoom", "365"),
                    ("zoom", "wealth box"),
                    ("365", "wealth box"),
                    ("right capital", "wealth box")
                ],
                "key_data_flows": [
                    "meeting summaries from video calls to CRM",
                    "calendar events from email to CRM",
                    "client communications logged in CRM"
                ]
            },
            
            BusinessProcess.COMPLIANCE_MONITORING: {
                "typical_tools": ["advent axys", "schwab", "wealth box", "365"],
                "expected_integrations": [
                    ("schwab", "advent axys"),
                    ("advent axys", "365"),
                    ("wealth box", "365")
                ],
                "key_data_flows": [
                    "trading activity from custodian to compliance monitoring",
                    "client restrictions from CRM to portfolio management",
                    "compliance reports to document management"
                ]
            }
        }
        
        # Business value scoring criteria
        self.value_criteria = {
            "time_savings": {
                "high": (100, 10),    # 100+ hours saved = 10 points
                "medium": (25, 7),    # 25+ hours saved = 7 points  
                "low": (5, 4)         # 5+ hours saved = 4 points
            },
            "error_reduction": {
                "high": 3,    # Eliminates major error risk
                "medium": 2,  # Reduces error risk
                "low": 1      # Minor error reduction
            },
            "client_satisfaction": {
                "high": 3,    # Directly improves client experience
                "medium": 2,  # Indirectly improves client experience
                "low": 1      # Minimal client impact
            },
            "compliance_value": {
                "high": 2,    # Critical for compliance
                "medium": 1,  # Helpful for compliance
                "low": 0      # No compliance impact
            }
        }
    
    def analyze_process_gaps(self, tool_inventory: Dict[str, dict], 
                           current_integrations: List[Dict]) -> Dict[BusinessProcess, ProcessAnalysis]:
        """Analyze gaps for each business process"""
        
        print("🔍 Analyzing integration gaps across business processes...")
        
        available_tools = set(self._normalize_tool_name(name) for name in tool_inventory.keys())
        existing_integrations = set()
        
        # Map existing integrations
        for integration in current_integrations:
            source = self._normalize_tool_name(integration.get("source_tool", ""))
            target = self._normalize_tool_name(integration.get("target_tool", ""))
            if source and target:
                existing_integrations.add((source, target))
                existing_integrations.add((target, source))  # Bidirectional
        
        process_analyses = {}
        
        for process, workflow_config in self.process_workflows.items():
            print(f"   📊 Analyzing {process.value}...")
            
            # Find which expected tools are available
            expected_tools = set(workflow_config["typical_tools"])
            available_process_tools = expected_tools.intersection(available_tools)
            missing_tools = expected_tools - available_tools
            
            # Analyze expected integrations
            integration_gaps = []
            
            for source, target in workflow_config["expected_integrations"]:
                # Check if both tools are available
                if source in available_process_tools and target in available_process_tools:
                    # Check if integration exists
                    if (source, target) not in existing_integrations and (target, source) not in existing_integrations:
                        # Found a gap!
                        gap = self._analyze_specific_gap(
                            source, target, process, workflow_config, tool_inventory
                        )
                        integration_gaps.append(gap)
            
            # Calculate process efficiency score
            expected_integrations = len(workflow_config["expected_integrations"])
            missing_integrations = len(integration_gaps)
            efficiency_score = max(1, 10 - int((missing_integrations / expected_integrations) * 10))
            
            # Identify pain points
            pain_points = []
            if missing_tools:
                pain_points.append(f"Missing key tools: {', '.join(missing_tools)}")
            if missing_integrations > 0:
                pain_points.append(f"{missing_integrations} integration gaps identified")
            if missing_integrations > expected_integrations * 0.5:
                pain_points.append("Highly manual process with limited automation")
            
            # Calculate automation potential
            automation_potential = min(10, len(integration_gaps) * 2)
            
            process_analyses[process] = ProcessAnalysis(
                process=process,
                tools_involved=list(available_process_tools),
                current_efficiency_score=efficiency_score,
                pain_points=pain_points,
                integration_gaps=integration_gaps,
                automation_potential=automation_potential
            )
        
        print(f"✅ Process gap analysis complete: {len(process_analyses)} processes analyzed")
        return process_analyses
    
    def _analyze_specific_gap(self, source_tool: str, target_tool: str, 
                            process: BusinessProcess, workflow_config: Dict,
                            tool_inventory: Dict[str, dict]) -> IntegrationGap:
        """Analyze a specific integration gap in detail"""
        
        # Determine gap characteristics based on process and tools
        gap_analysis = self._get_gap_template(source_tool, target_tool, process)
        
        # Calculate business value score
        business_value = self._calculate_business_value(gap_analysis)
        
        # Estimate implementation complexity
        complexity = self._estimate_complexity(source_tool, target_tool, tool_inventory)
        
        # Calculate time savings
        time_savings = gap_analysis.get("time_savings_hours", 20)
        annual_value = time_savings * 50 * 52  # $50/hour * 52 weeks
        
        return IntegrationGap(
            source_tool=source_tool,
            target_tool=target_tool,
            business_process=process,
            gap_type=gap_analysis.get("gap_type", "missing_integration"),
            current_state=gap_analysis.get("current_state", "Manual process"),
            proposed_integration=gap_analysis.get("proposed_integration", "API integration"),
            business_value=business_value,
            implementation_complexity=complexity,
            annual_time_savings_hours=time_savings * 52,  # Weekly hours * 52 weeks
            estimated_annual_value=annual_value,
            prerequisites=gap_analysis.get("prerequisites", []),
            risks=gap_analysis.get("risks", ["Integration maintenance overhead"])
        )
    
    def _get_gap_template(self, source_tool: str, target_tool: str, 
                         process: BusinessProcess) -> Dict[str, Any]:
        """Get template analysis for specific tool pair and process"""
        
        # Define specific gap analyses for common tool combinations
        gap_templates = {
            # Portfolio Management gaps
            ("advent axys", "wealth box"): {
                BusinessProcess.CLIENT_REPORTING: {
                    "gap_type": "missing_integration",
                    "current_state": "Manual export of portfolio data, manual entry into CRM client records",
                    "proposed_integration": "Automated sync of portfolio performance to client records in CRM",
                    "time_savings_hours": 4,  # per week
                    "prerequisites": ["API access to both systems", "Client data mapping"],
                    "risks": ["Data privacy considerations", "Client consent for automated data sharing"]
                }
            },
            
            ("factset", "365"): {
                BusinessProcess.RESEARCH_WORKFLOW: {
                    "gap_type": "manual_workflow",
                    "current_state": "Manual download and email of research reports",
                    "proposed_integration": "Automated delivery of research to SharePoint with email notifications",
                    "time_savings_hours": 3,
                    "prerequisites": ["FactSet API access", "SharePoint integration"],
                    "risks": ["Information overload", "Entitlements management"]
                }
            },
            
            ("zoom", "wealth box"): {
                BusinessProcess.CLIENT_COMMUNICATION: {
                    "gap_type": "missing_integration", 
                    "current_state": "Manual logging of meeting notes and follow-ups in CRM",
                    "proposed_integration": "Automated capture of meeting summaries and task creation in CRM",
                    "time_savings_hours": 2,
                    "prerequisites": ["Zoom API access", "AI transcription setup"],
                    "risks": ["Client privacy concerns", "Transcription accuracy"]
                }
            },
            
            ("right capital", "365"): {
                BusinessProcess.CLIENT_REPORTING: {
                    "gap_type": "manual_workflow",
                    "current_state": "Manual creation and email of financial plans",
                    "proposed_integration": "Automated plan generation and delivery via email/SharePoint",
                    "time_savings_hours": 2,
                    "prerequisites": ["Right Capital API", "Email template setup"],
                    "risks": ["Plan customization limitations", "Client communication standardization"]
                }
            }
        }
        
        # Get specific template or use generic
        key = (source_tool, target_tool)
        if key in gap_templates and process in gap_templates[key]:
            return gap_templates[key][process]
        
        # Generic template
        return {
            "gap_type": "missing_integration",
            "current_state": f"Manual data transfer between {source_tool} and {target_tool}",
            "proposed_integration": f"API integration to sync data between {source_tool} and {target_tool}",
            "time_savings_hours": 1,
            "prerequisites": ["API access", "Data mapping"],
            "risks": ["Integration maintenance", "Data synchronization issues"]
        }
    
    def _calculate_business_value(self, gap_analysis: Dict[str, Any]) -> int:
        """Calculate business value score (1-10) for an integration gap"""
        
        score = 0
        time_savings = gap_analysis.get("time_savings_hours", 1)
        
        # Time savings component
        if time_savings >= 4:
            score += 4
        elif time_savings >= 2:
            score += 3  
        else:
            score += 2
        
        # Error reduction (estimated based on gap type)
        if gap_analysis.get("gap_type") == "manual_workflow":
            score += 2  # Manual processes are error-prone
        else:
            score += 1
        
        # Client satisfaction (estimated based on process)
        if "client" in gap_analysis.get("current_state", "").lower():
            score += 2
        else:
            score += 1
        
        # Compliance value (estimated)
        if any(word in gap_analysis.get("current_state", "").lower() 
               for word in ["compliance", "audit", "reporting"]):
            score += 1
        
        return min(10, score)
    
    def _estimate_complexity(self, source_tool: str, target_tool: str, 
                           tool_inventory: Dict[str, dict]) -> int:
        """Estimate implementation complexity (1-10, higher = more complex)"""
        
        complexity = 3  # Base complexity
        
        # Tool-specific complexity factors
        complex_tools = ["advent axys", "factset", "bloomberg"]  # Enterprise systems
        simple_tools = ["zoom", "365", "slack"]  # Cloud-native with good APIs
        
        if source_tool in complex_tools or target_tool in complex_tools:
            complexity += 3
        
        if source_tool in simple_tools and target_tool in simple_tools:
            complexity -= 1
        
        # Data sensitivity (financial tools are more complex)
        sensitive_tools = ["advent axys", "schwab", "factset", "bloomberg"]
        if source_tool in sensitive_tools or target_tool in sensitive_tools:
            complexity += 2
        
        return min(10, max(1, complexity))
    
    def _normalize_tool_name(self, tool_name: str) -> str:
        """Normalize tool names for consistent comparison"""
        normalized = tool_name.lower().strip()
        
        # Handle common variations
        if "microsoft" in normalized or "office" in normalized:
            return "365"
        if "wealthbox" in normalized or "wealth box" in normalized:
            return "wealth box" 
        if "advent" in normalized:
            return "advent axys"
        if "right" in normalized and "capital" in normalized:
            return "right capital"
            
        return normalized
    
    def prioritize_gaps(self, process_analyses: Dict[BusinessProcess, ProcessAnalysis]) -> List[IntegrationGap]:
        """Prioritize integration gaps by business value and impact"""
        
        all_gaps = []
        for analysis in process_analyses.values():
            all_gaps.extend(analysis.integration_gaps)
        
        # Sort by business value (descending) then by complexity (ascending)
        prioritized = sorted(all_gaps, key=lambda g: (-g.business_value, g.implementation_complexity))
        
        return prioritized
    
    def generate_gap_analysis_report(self, process_analyses: Dict[BusinessProcess, ProcessAnalysis]) -> Dict[str, Any]:
        """Generate comprehensive gap analysis report"""
        
        all_gaps = self.prioritize_gaps(process_analyses)
        
        # Calculate summary metrics
        total_annual_value = sum(gap.estimated_annual_value for gap in all_gaps)
        total_time_savings = sum(gap.annual_time_savings_hours for gap in all_gaps)
        
        # Group gaps by priority
        high_priority = [g for g in all_gaps if g.business_value >= 8]
        medium_priority = [g for g in all_gaps if 5 <= g.business_value < 8]
        low_priority = [g for g in all_gaps if g.business_value < 5]
        
        # Process efficiency summary
        process_efficiency = {}
        for process, analysis in process_analyses.items():
            process_efficiency[process.value] = {
                "efficiency_score": analysis.current_efficiency_score,
                "gaps_identified": len(analysis.integration_gaps),
                "automation_potential": analysis.automation_potential,
                "pain_points": analysis.pain_points
            }
        
        return {
            "analysis_summary": {
                "total_gaps_identified": len(all_gaps),
                "high_priority_gaps": len(high_priority),
                "medium_priority_gaps": len(medium_priority),
                "low_priority_gaps": len(low_priority),
                "total_estimated_annual_value": total_annual_value,
                "total_annual_time_savings_hours": total_time_savings,
                "average_process_efficiency": round(
                    sum(a.current_efficiency_score for a in process_analyses.values()) / len(process_analyses), 1
                )
            },
            "prioritized_gaps": [
                {
                    "source_tool": gap.source_tool,
                    "target_tool": gap.target_tool,
                    "business_process": gap.business_process.value,
                    "business_value": gap.business_value,
                    "implementation_complexity": gap.implementation_complexity,
                    "estimated_annual_value": gap.estimated_annual_value,
                    "annual_time_savings_hours": gap.annual_time_savings_hours,
                    "current_state": gap.current_state,
                    "proposed_integration": gap.proposed_integration
                }
                for gap in all_gaps[:10]  # Top 10 gaps
            ],
            "process_efficiency_scores": process_efficiency,
            "quick_wins": [
                {
                    "source_tool": gap.source_tool,
                    "target_tool": gap.target_tool,
                    "business_value": gap.business_value,
                    "complexity": gap.implementation_complexity,
                    "value_complexity_ratio": round(gap.business_value / gap.implementation_complexity, 2)
                }
                for gap in all_gaps
                if gap.implementation_complexity <= 4 and gap.business_value >= 6
            ]
        }

# Convenience functions
def analyze_integration_gaps(tool_inventory: Dict[str, dict], 
                           current_integrations: List[Dict]) -> Tuple[Dict[BusinessProcess, ProcessAnalysis], Dict[str, Any]]:
    """Complete gap analysis with report generation"""
    analyzer = IntegrationGapAnalyzer()
    process_analyses = analyzer.analyze_process_gaps(tool_inventory, current_integrations)
    report = analyzer.generate_gap_analysis_report(process_analyses)
    return process_analyses, report
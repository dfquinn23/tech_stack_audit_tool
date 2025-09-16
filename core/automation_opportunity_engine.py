# core/automation_opportunity_engine.py
"""
Advanced automation opportunity identification and n8n workflow generation
Systematic approach to identifying, scoring, and designing automation workflows
"""

import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from pathlib import Path

class AutomationComplexity(Enum):
    LOW = "low"          # 1-3 weeks implementation
    MEDIUM = "medium"    # 1-2 months implementation  
    HIGH = "high"        # 3+ months implementation

class BusinessImpact(Enum):
    TRANSFORMATIONAL = "transformational"  # Fundamentally changes workflow
    SIGNIFICANT = "significant"           # Major efficiency improvement
    MODERATE = "moderate"                # Noticeable improvement
    MINIMAL = "minimal"                  # Small efficiency gain

@dataclass
class N8nWorkflowSpec:
    name: str
    description: str
    trigger_type: str  # "webhook", "schedule", "email", "file_watch", "api_call"
    trigger_config: Dict[str, Any]
    nodes: List[Dict[str, Any]]  # Detailed node specifications
    estimated_executions_per_month: int
    data_transformations: List[str]
    error_handling: Dict[str, Any]
    monitoring_requirements: List[str]

@dataclass  
class AutomationOpportunity:
    id: str
    name: str
    description: str
    source_tools: List[str]
    target_tools: List[str]
    business_process: str
    current_workflow_description: str
    proposed_automation: str
    
    # Scoring components (1-5 each)
    frequency_score: int        # How often is this process executed
    time_savings_score: int     # How much time would be saved
    error_reduction_score: int  # How much manual error would be eliminated
    strategic_value_score: int  # Strategic importance to business
    feasibility_score: int      # Technical feasibility
    
    # Calculated scores
    total_score: int           # Sum of all scoring components (max 25)
    priority_tier: str         # "high", "medium", "low"
    
    # Business metrics
    current_time_per_execution_minutes: int
    executions_per_month: int
    monthly_time_savings_hours: float
    annual_cost_savings: float
    implementation_cost_estimate: float
    roi_percentage: float
    payback_period_months: float
    
    # Technical specifications
    complexity: AutomationComplexity
    business_impact: BusinessImpact
    n8n_workflow: N8nWorkflowSpec
    prerequisites: List[str]
    risks: List[str]
    success_metrics: List[str]
    
    # Timeline
    estimated_implementation_weeks: int
    go_live_dependencies: List[str]
    
    created_at: datetime
    updated_at: datetime

class AutomationOpportunityEngine:
    """Advanced engine for identifying and designing automation opportunities"""
    
    def __init__(self):
        self.opportunity_templates = self._load_opportunity_templates()
        self.n8n_node_library = self._load_n8n_node_library()
        self.scoring_weights = {
            "frequency": 0.25,      # 25% weight for frequency
            "time_savings": 0.30,   # 30% weight for time savings
            "error_reduction": 0.20, # 20% weight for error reduction
            "strategic_value": 0.15, # 15% weight for strategic value
            "feasibility": 0.10     # 10% weight for feasibility
        }
        
        # Financial assumptions
        self.hourly_rate = 75  # Average hourly rate for financial services staff
        self.annual_hours = 2080  # Standard work year
        
    def _load_opportunity_templates(self) -> Dict[str, Dict]:
        """Load predefined opportunity templates for common business processes"""
        return {
            # Research workflow automations
            "research_to_client_reports": {
                "name": "Research Data to Client Reports",
                "description": "Automated generation of client research summaries from FactSet/Bloomberg data",
                "typical_tools": ["factset", "bloomberg", "365", "wealth box"],
                "business_process": "client_reporting",
                "frequency_score": 4,  # Daily to weekly
                "time_savings_score": 5,  # High time savings
                "error_reduction_score": 4,  # Reduces transcription errors
                "strategic_value_score": 4,  # Important for client service
                "feasibility_score": 3,  # Moderate complexity
                "current_time_minutes": 120,  # 2 hours per report
                "executions_per_month": 20,
                "complexity": AutomationComplexity.MEDIUM,
                "business_impact": BusinessImpact.SIGNIFICANT
            },
            
            "meeting_notes_to_crm": {
                "name": "Meeting Notes to CRM Integration",
                "description": "Automated capture and filing of meeting summaries in CRM",
                "typical_tools": ["zoom", "365", "wealth box"],
                "business_process": "client_communication",
                "frequency_score": 5,  # Multiple daily
                "time_savings_score": 3,  # Moderate time savings per instance
                "error_reduction_score": 5,  # Eliminates forgetting to log
                "strategic_value_score": 3,  # Good for consistency
                "feasibility_score": 4,  # API availability good
                "current_time_minutes": 15,  # 15 minutes post-meeting logging
                "executions_per_month": 100,  # Many meetings
                "complexity": AutomationComplexity.LOW,
                "business_impact": BusinessImpact.MODERATE
            },
            
            "portfolio_performance_reporting": {
                "name": "Automated Portfolio Performance Reports", 
                "description": "Generate and distribute monthly portfolio performance reports",
                "typical_tools": ["advent axys", "365", "wealth box"],
                "business_process": "client_reporting",
                "frequency_score": 3,  # Monthly
                "time_savings_score": 5,  # Very high time savings
                "error_reduction_score": 5,  # Eliminates calculation errors
                "strategic_value_score": 5,  # Critical for client retention
                "feasibility_score": 2,  # High complexity due to Advent integration
                "current_time_minutes": 300,  # 5 hours per client monthly
                "executions_per_month": 50,  # 50 clients
                "complexity": AutomationComplexity.HIGH,
                "business_impact": BusinessImpact.TRANSFORMATIONAL
            },
            
            "compliance_monitoring": {
                "name": "Automated Compliance Monitoring",
                "description": "Monitor trading activity against client restrictions and regulations",
                "typical_tools": ["schwab", "advent axys", "365"],
                "business_process": "compliance_monitoring", 
                "frequency_score": 5,  # Continuous/daily
                "time_savings_score": 4,  # High time savings
                "error_reduction_score": 5,  # Critical for compliance
                "strategic_value_score": 5,  # Regulatory requirement
                "feasibility_score": 3,  # Complex data integration
                "current_time_minutes": 60,  # 1 hour daily review
                "executions_per_month": 22,  # Daily business days
                "complexity": AutomationComplexity.MEDIUM,
                "business_impact": BusinessImpact.SIGNIFICANT
            },
            
            "client_onboarding_workflow": {
                "name": "Client Onboarding Automation",
                "description": "Streamline new client setup across all systems",
                "typical_tools": ["wealth box", "schwab", "right capital", "365"],
                "business_process": "client_onboarding",
                "frequency_score": 2,  # Weekly
                "time_savings_score": 5,  # Very high time savings
                "error_reduction_score": 4,  # Reduces setup errors
                "strategic_value_score": 4,  # Important for client experience
                "feasibility_score": 3,  # Multiple system integration
                "current_time_minutes": 240,  # 4 hours per new client
                "executions_per_month": 5,  # 5 new clients monthly
                "complexity": AutomationComplexity.MEDIUM,
                "business_impact": BusinessImpact.SIGNIFICANT
            },
            
            "document_management_workflow": {
                "name": "Document Management Automation",
                "description": "Automated filing and organization of client documents",
                "typical_tools": ["365", "wealth box", "right capital"],
                "business_process": "document_management",
                "frequency_score": 5,  # Multiple daily
                "time_savings_score": 3,  # Moderate per instance
                "error_reduction_score": 4,  # Reduces misfiling
                "strategic_value_score": 2,  # Important but not critical
                "feasibility_score": 4,  # Good SharePoint/CRM APIs
                "current_time_minutes": 10,  # 10 minutes per document
                "executions_per_month": 200,  # Many documents
                "complexity": AutomationComplexity.LOW,
                "business_impact": BusinessImpact.MODERATE
            }
        }
    
    def _load_n8n_node_library(self) -> Dict[str, Dict]:
        """Load n8n node specifications for workflow design"""
        return {
            # API nodes for common tools
            "microsoft_graph": {
                "node_type": "HTTP Request",
                "name": "Microsoft Graph API",
                "description": "Access Microsoft 365 services (Email, Calendar, SharePoint, Teams)",
                "capabilities": ["email", "calendar", "files", "contacts", "teams"],
                "auth_required": True,
                "rate_limits": "10,000 requests/hour",
                "common_operations": ["send_email", "create_calendar_event", "upload_file", "create_teams_message"]
            },
            
            "zoom_api": {
                "node_type": "HTTP Request", 
                "name": "Zoom API",
                "description": "Access Zoom meeting data and recordings",
                "capabilities": ["meetings", "recordings", "participants", "chat"],
                "auth_required": True,
                "rate_limits": "2,000 requests/day",
                "common_operations": ["get_meeting_details", "download_recording", "get_participants"]
            },
            
            "webhook_receiver": {
                "node_type": "Webhook",
                "name": "Webhook Trigger",
                "description": "Receive webhooks from external systems",
                "capabilities": ["real_time_triggers", "event_processing"],
                "auth_required": False,
                "rate_limits": "unlimited",
                "common_operations": ["receive_webhook", "validate_payload", "extract_data"]
            },
            
            "email_trigger": {
                "node_type": "Email Trigger (IMAP)",
                "name": "Email Monitor",
                "description": "Monitor email for specific patterns or attachments",
                "capabilities": ["email_monitoring", "attachment_processing"],
                "auth_required": True,
                "rate_limits": "connection_based",
                "common_operations": ["monitor_inbox", "process_attachments", "extract_email_data"]
            },
            
            "file_watcher": {
                "node_type": "Local File Trigger",
                "name": "File System Monitor",
                "description": "Watch for new files in specified directories",
                "capabilities": ["file_monitoring", "directory_watching"],
                "auth_required": False,
                "rate_limits": "file_system_based",
                "common_operations": ["watch_directory", "process_new_files", "move_files"]
            },
            
            "schedule_trigger": {
                "node_type": "Cron",
                "name": "Schedule Trigger", 
                "description": "Execute workflows on a schedule",
                "capabilities": ["scheduled_execution", "time_based_triggers"],
                "auth_required": False,
                "rate_limits": "none",
                "common_operations": ["daily_execution", "weekly_reports", "monthly_processing"]
            },
            
            # Data processing nodes
            "data_transformer": {
                "node_type": "Function",
                "name": "JavaScript Code",
                "description": "Custom data transformation and business logic",
                "capabilities": ["data_transformation", "business_logic", "calculations"],
                "auth_required": False,
                "rate_limits": "computation_based",
                "common_operations": ["transform_data", "calculate_values", "filter_records"]
            },
            
            "csv_processor": {
                "node_type": "Spreadsheet File",
                "name": "CSV/Excel Processor",
                "description": "Read and write CSV/Excel files",
                "capabilities": ["file_processing", "data_import_export"],
                "auth_required": False,
                "rate_limits": "file_size_based",
                "common_operations": ["read_csv", "write_excel", "transform_spreadsheet"]
            },
            
            "pdf_generator": {
                "node_type": "HTML/CSS to PDF",
                "name": "PDF Generator",
                "description": "Generate PDF reports from HTML templates",
                "capabilities": ["report_generation", "pdf_creation"],
                "auth_required": False,
                "rate_limits": "processing_based",
                "common_operations": ["html_to_pdf", "template_rendering", "report_generation"]
            }
        }
    
    def identify_opportunities(self, tool_inventory: Dict[str, dict], 
                             integration_gaps: List[Dict], 
                             current_integrations: List[Dict]) -> List[AutomationOpportunity]:
        """Identify automation opportunities based on tool inventory and gaps"""
        
        print("🤖 Identifying automation opportunities...")
        
        opportunities = []
        available_tools = set(self._normalize_tool_name(name) for name in tool_inventory.keys())
        
        # Step 1: Match tool inventory against opportunity templates
        for template_id, template in self.opportunity_templates.items():
            template_tools = set(template["typical_tools"])
            
            # Check if we have the required tools for this template
            if template_tools.issubset(available_tools):
                print(f"   ✅ Found opportunity match: {template['name']}")
                
                opportunity = self._create_opportunity_from_template(
                    template_id, template, tool_inventory, integration_gaps
                )
                opportunities.append(opportunity)
        
        # Step 2: Identify custom opportunities from integration gaps
        gap_opportunities = self._identify_gap_based_opportunities(
            integration_gaps, tool_inventory, available_tools
        )
        opportunities.extend(gap_opportunities)
        
        # Step 3: Score and prioritize all opportunities
        scored_opportunities = [self._score_opportunity(opp) for opp in opportunities]
        
        # Sort by total score (descending)
        scored_opportunities.sort(key=lambda x: x.total_score, reverse=True)
        
        print(f"✅ Identified {len(scored_opportunities)} automation opportunities")
        
        return scored_opportunities
    
    def _create_opportunity_from_template(self, template_id: str, template: Dict, 
                                        tool_inventory: Dict[str, dict],
                                        integration_gaps: List[Dict]) -> AutomationOpportunity:
        """Create a detailed opportunity from a template"""
        
        # Generate unique ID
        opportunity_id = f"{template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Extract tools involved
        source_tools = []
        target_tools = []
        for tool_name in template["typical_tools"]:
            if any(tool_name in inv_name.lower() for inv_name in tool_inventory.keys()):
                if not source_tools:
                    source_tools.append(tool_name)
                else:
                    target_tools.append(tool_name)
        
        # Generate n8n workflow specification
        n8n_workflow = self._generate_n8n_workflow(template, source_tools, target_tools)
        
        # Calculate financial metrics
        monthly_time_savings = (template["current_time_minutes"] * template["executions_per_month"]) / 60
        annual_cost_savings = monthly_time_savings * 12 * self.hourly_rate
        implementation_cost = self._estimate_implementation_cost(template["complexity"])
        roi_percentage = ((annual_cost_savings - implementation_cost) / implementation_cost) * 100 if implementation_cost > 0 else 0
        payback_months = (implementation_cost / (monthly_time_savings * self.hourly_rate)) if monthly_time_savings > 0 else 999
        
        return AutomationOpportunity(
            id=opportunity_id,
            name=template["name"],
            description=template["description"],
            source_tools=source_tools,
            target_tools=target_tools,
            business_process=template["business_process"],
            current_workflow_description=f"Currently manual process taking {template['current_time_minutes']} minutes per execution",
            proposed_automation=f"Automated n8n workflow reducing time to <5 minutes per execution",
            
            # Scoring from template
            frequency_score=template["frequency_score"],
            time_savings_score=template["time_savings_score"], 
            error_reduction_score=template["error_reduction_score"],
            strategic_value_score=template["strategic_value_score"],
            feasibility_score=template["feasibility_score"],
            
            # Will be calculated by _score_opportunity
            total_score=0,
            priority_tier="medium",
            
            # Financial metrics
            current_time_per_execution_minutes=template["current_time_minutes"],
            executions_per_month=template["executions_per_month"],
            monthly_time_savings_hours=monthly_time_savings,
            annual_cost_savings=annual_cost_savings,
            implementation_cost_estimate=implementation_cost,
            roi_percentage=roi_percentage,
            payback_period_months=payback_months,
            
            # Technical specs
            complexity=template["complexity"],
            business_impact=template["business_impact"],
            n8n_workflow=n8n_workflow,
            prerequisites=self._generate_prerequisites(template, source_tools, target_tools),
            risks=self._generate_risks(template, source_tools, target_tools),
            success_metrics=self._generate_success_metrics(template),
            
            # Timeline
            estimated_implementation_weeks=self._estimate_implementation_weeks(template["complexity"]),
            go_live_dependencies=self._generate_dependencies(template, source_tools, target_tools),
            
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def _generate_n8n_workflow(self, template: Dict, source_tools: List[str], target_tools: List[str]) -> N8nWorkflowSpec:
        """Generate detailed n8n workflow specification"""
        
        workflow_name = f"n8n_{template['business_process']}_{template['name'].lower().replace(' ', '_')}"
        
        # Determine trigger based on business process
        if template["business_process"] == "client_reporting":
            trigger_type = "schedule"
            trigger_config = {"cron": "0 9 * * 1", "timezone": "America/New_York"}  # Monday 9 AM
        elif template["business_process"] == "client_communication":
            trigger_type = "webhook"
            trigger_config = {"path": f"/{workflow_name}", "method": "POST"}
        elif template["business_process"] == "compliance_monitoring":
            trigger_type = "schedule"
            trigger_config = {"cron": "0 8 * * 1-5", "timezone": "America/New_York"}  # Weekdays 8 AM
        else:
            trigger_type = "schedule"
            trigger_config = {"cron": "0 10 * * *", "timezone": "America/New_York"}  # Daily 10 AM
        
        # Generate node sequence
        nodes = self._generate_workflow_nodes(template, source_tools, target_tools, trigger_type)
        
        # Estimate executions
        if trigger_type == "schedule":
            if "daily" in template.get("description", "").lower():
                monthly_executions = 22  # Business days
            elif "weekly" in template.get("description", "").lower():
                monthly_executions = 4
            else:
                monthly_executions = template.get("executions_per_month", 10)
        else:
            monthly_executions = template.get("executions_per_month", 20)
        
        return N8nWorkflowSpec(
            name=workflow_name,
            description=f"Automated workflow for {template['name']}",
            trigger_type=trigger_type,
            trigger_config=trigger_config,
            nodes=nodes,
            estimated_executions_per_month=monthly_executions,
            data_transformations=self._generate_data_transformations(template),
            error_handling={
                "retry_attempts": 3,
                "error_workflow": "error_notification",
                "timeout_seconds": 300
            },
            monitoring_requirements=[
                "execution_success_rate",
                "average_execution_time", 
                "error_notifications",
                "data_quality_checks"
            ]
        )
    
    def _generate_workflow_nodes(self, template: Dict, source_tools: List[str], 
                                target_tools: List[str], trigger_type: str) -> List[Dict[str, Any]]:
        """Generate the sequence of n8n nodes for the workflow"""
        
        nodes = []
        
        # Trigger node
        if trigger_type == "schedule":
            nodes.append({
                "name": "Schedule Trigger",
                "type": "n8n-nodes-base.cron",
                "position": [100, 100],
                "parameters": {"rule": {"interval": [{"field": "cronExpression"}]}}
            })
        elif trigger_type == "webhook":
            nodes.append({
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook", 
                "position": [100, 100],
                "parameters": {"path": template["name"].lower().replace(" ", "-")}
            })
        
        # Data source nodes (based on source tools)
        x_pos = 300
        for tool in source_tools:
            if "factset" in tool.lower():
                nodes.append({
                    "name": "FactSet Data",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [x_pos, 100],
                    "parameters": {
                        "url": "={{$env.FACTSET_API_URL}}",
                        "authentication": "predefinedCredentialType",
                        "nodeCredentialType": "factsetApi"
                    }
                })
            elif "bloomberg" in tool.lower():
                nodes.append({
                    "name": "Bloomberg Data",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [x_pos, 100],
                    "parameters": {
                        "url": "={{$env.BLOOMBERG_API_URL}}",
                        "authentication": "predefinedCredentialType"
                    }
                })
            elif "365" in tool.lower() or "microsoft" in tool.lower():
                nodes.append({
                    "name": "Microsoft Graph",
                    "type": "n8n-nodes-base.microsoftGraph",
                    "position": [x_pos, 100],
                    "parameters": {"resource": "mail", "operation": "send"}
                })
            elif "zoom" in tool.lower():
                nodes.append({
                    "name": "Zoom API",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [x_pos, 100],
                    "parameters": {
                        "url": "https://api.zoom.us/v2/meetings/{{$json.meeting_id}}/recordings",
                        "authentication": "predefinedCredentialType"
                    }
                })
            x_pos += 200
        
        # Data transformation node
        nodes.append({
            "name": "Transform Data",
            "type": "n8n-nodes-base.function",
            "position": [x_pos, 100],
            "parameters": {
                "functionCode": "// Transform data according to business requirements\nreturn items.map(item => {\n  // Add transformation logic here\n  return item;\n});"
            }
        })
        x_pos += 200
        
        # Target system nodes
        for tool in target_tools:
            if "wealth box" in tool.lower() or "crm" in tool.lower():
                nodes.append({
                    "name": "Update CRM",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [x_pos, 100],
                    "parameters": {
                        "url": "={{$env.WEALTHBOX_API_URL}}/contacts",
                        "method": "POST",
                        "authentication": "predefinedCredentialType"
                    }
                })
            elif "365" in tool.lower():
                nodes.append({
                    "name": "Send Email/Store File",
                    "type": "n8n-nodes-base.microsoftGraph",
                    "position": [x_pos, 100],
                    "parameters": {"resource": "mail", "operation": "send"}
                })
            x_pos += 200
        
        # Notification/logging node
        nodes.append({
            "name": "Success Notification",
            "type": "n8n-nodes-base.microsoftGraph",
            "position": [x_pos, 100],
            "parameters": {
                "resource": "mail",
                "operation": "send",
                "subject": "Workflow Completed: {{$node.Schedule Trigger.json.workflow_name}}",
                "toRecipients": ["operations@firm.com"]
            }
        })
        
        return nodes
    
    def _score_opportunity(self, opportunity: AutomationOpportunity) -> AutomationOpportunity:
        """Calculate total score and priority tier for an opportunity"""
        
        # Calculate weighted total score
        total_score = (
            opportunity.frequency_score * self.scoring_weights["frequency"] * 5 +
            opportunity.time_savings_score * self.scoring_weights["time_savings"] * 5 +
            opportunity.error_reduction_score * self.scoring_weights["error_reduction"] * 5 +
            opportunity.strategic_value_score * self.scoring_weights["strategic_value"] * 5 +
            opportunity.feasibility_score * self.scoring_weights["feasibility"] * 5
        )
        
        opportunity.total_score = int(total_score)
        
        # Determine priority tier
        if opportunity.total_score >= 20:
            opportunity.priority_tier = "high"
        elif opportunity.total_score >= 15:
            opportunity.priority_tier = "medium"
        else:
            opportunity.priority_tier = "low"
        
        return opportunity
    
    def _identify_gap_based_opportunities(self, integration_gaps: List[Dict], 
                                        tool_inventory: Dict[str, dict],
                                        available_tools: set) -> List[AutomationOpportunity]:
        """Identify opportunities based on integration gaps"""
        
        gap_opportunities = []
        
        for gap in integration_gaps:
            if gap.get("business_value", 0) >= 7:  # High value gaps only
                # Create custom opportunity from gap
                opportunity_id = f"gap_based_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # Basic workflow for gap-based opportunity
                n8n_workflow = N8nWorkflowSpec(
                    name=f"gap_automation_{gap.get('source_tool', '').replace(' ', '_')}_{gap.get('target_tool', '').replace(' ', '_')}",
                    description=f"Automation addressing integration gap: {gap.get('proposed_integration', '')}",
                    trigger_type="schedule",
                    trigger_config={"cron": "0 9 * * 1-5", "timezone": "America/New_York"},
                    nodes=[
                        {"name": "Data Extract", "type": "httpRequest"},
                        {"name": "Transform", "type": "function"},
                        {"name": "Load Data", "type": "httpRequest"}
                    ],
                    estimated_executions_per_month=20,
                    data_transformations=["field_mapping", "data_validation", "format_conversion"],
                    error_handling={"retry_attempts": 3, "timeout_seconds": 300},
                    monitoring_requirements=["success_rate", "data_quality"]
                )
                
                opportunity = AutomationOpportunity(
                    id=opportunity_id,
                    name=f"Integration Gap: {gap.get('source_tool')} to {gap.get('target_tool')}",
                    description=gap.get("proposed_integration", ""),
                    source_tools=[gap.get("source_tool", "")],
                    target_tools=[gap.get("target_tool", "")],
                    business_process=gap.get("business_process", "integration"),
                    current_workflow_description=gap.get("current_state", "Manual process"),
                    proposed_automation=gap.get("proposed_integration", "Automated integration"),
                    
                    # Score based on gap analysis
                    frequency_score=3,  # Default moderate frequency
                    time_savings_score=gap.get("business_value", 5) // 2,  # Scale business value
                    error_reduction_score=4,  # Integrations typically reduce errors
                    strategic_value_score=gap.get("business_value", 5) // 2,
                    feasibility_score=5 - gap.get("implementation_complexity", 3),  # Inverse complexity
                    
                    total_score=0,  # Will be calculated
                    priority_tier="medium",
                    
                    # Financial estimates based on gap data
                    current_time_per_execution_minutes=gap.get("annual_time_savings_hours", 100) * 60 // 52,  # Weekly average
                    executions_per_month=20,
                    monthly_time_savings_hours=gap.get("annual_time_savings_hours", 100) / 12,
                    annual_cost_savings=gap.get("estimated_annual_value", 10000),
                    implementation_cost_estimate=gap.get("estimated_annual_value", 10000) * 0.3,  # 30% of annual value
                    roi_percentage=200,  # Default good ROI
                    payback_period_months=4,  # Default 4 month payback
                    
                    complexity=AutomationComplexity.MEDIUM,
                    business_impact=BusinessImpact.MODERATE,
                    n8n_workflow=n8n_workflow,
                    prerequisites=gap.get("prerequisites", []),
                    risks=gap.get("risks", ["Integration complexity"]),
                    success_metrics=["Reduced manual processing time", "Improved data accuracy"],
                    
                    estimated_implementation_weeks=8,
                    go_live_dependencies=["API access", "Testing environment"],
                    
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                gap_opportunities.append(opportunity)
        
        return gap_opportunities
    
    def _normalize_tool_name(self, tool_name: str) -> str:
        """Normalize tool names for consistent comparison"""
        normalized = tool_name.lower().strip()
        if "microsoft" in normalized or "office" in normalized:
            return "365"
        if "wealthbox" in normalized:
            return "wealth box"
        return normalized
    
    def _estimate_implementation_cost(self, complexity: AutomationComplexity) -> float:
        """Estimate implementation cost based on complexity"""
        base_costs = {
            AutomationComplexity.LOW: 5000,     # 1-3 weeks @ $2500/week
            AutomationComplexity.MEDIUM: 15000, # 1-2 months @ $7500/month  
            AutomationComplexity.HIGH: 40000    # 3+ months @ $13000/month
        }
        return base_costs.get(complexity, 15000)
    
    def _estimate_implementation_weeks(self, complexity: AutomationComplexity) -> int:
        """Estimate implementation timeline"""
        timelines = {
            AutomationComplexity.LOW: 2,
            AutomationComplexity.MEDIUM: 6,
            AutomationComplexity.HIGH: 12
        }
        return timelines.get(complexity, 6)
    
    def _generate_prerequisites(self, template: Dict, source_tools: List[str], target_tools: List[str]) -> List[str]:
        """Generate prerequisites for implementation"""
        prerequisites = ["n8n instance configured", "API credentials secured"]
        
        for tool in source_tools + target_tools:
            if "factset" in tool.lower():
                prerequisites.append("FactSet API access and entitlements")
            elif "bloomberg" in tool.lower():
                prerequisites.append("Bloomberg API license")
            elif "365" in tool.lower():
                prerequisites.append("Microsoft Graph API permissions")
            elif "zoom" in tool.lower():
                prerequisites.append("Zoom API key and permissions")
        
        return prerequisites
    
    def _generate_risks(self, template: Dict, source_tools: List[str], target_tools: List[str]) -> List[str]:
        """Generate implementation and operational risks"""
        risks = ["API rate limiting", "Authentication token expiry", "Data format changes"]
        
        if template.get("complexity") == AutomationComplexity.HIGH:
            risks.extend(["Complex data transformations", "Multiple system dependencies"])
        
        if "compliance" in template.get("business_process", ""):
            risks.extend(["Regulatory compliance requirements", "Audit trail maintenance"])
        
        return risks
    
    def _generate_success_metrics(self, template: Dict) -> List[str]:
        """Generate success metrics for the automation"""
        base_metrics = [
            "Execution success rate > 95%",
            "Average execution time < 5 minutes",
            "Zero data loss incidents"
        ]
        
        if template.get("time_savings_score", 0) >= 4:
            base_metrics.append(f"Time savings of {template.get('current_time_minutes', 60)} minutes per execution")
        
        if template.get("error_reduction_score", 0) >= 4:
            base_metrics.append("Manual error rate reduced by 90%+")
        
        return base_metrics
    
    def _generate_dependencies(self, template: Dict, source_tools: List[str], target_tools: List[str]) -> List[str]:
        """Generate go-live dependencies"""
        dependencies = ["User acceptance testing completed", "Production environment setup"]
        
        if len(source_tools) + len(target_tools) > 2:
            dependencies.append("Multi-system integration testing")
        
        if "compliance" in template.get("business_process", ""):
            dependencies.append("Compliance review and approval")
        
        return dependencies
    
    def _generate_data_transformations(self, template: Dict) -> List[str]:
        """Generate data transformations required"""
        transformations = ["Input validation", "Data type conversion"]
        
        if template.get("business_process") == "client_reporting":
            transformations.extend(["Performance calculations", "Report formatting", "Client data merge"])
        elif template.get("business_process") == "compliance_monitoring":
            transformations.extend(["Risk calculations", "Threshold checks", "Alert generation"])
        
        return transformations
    
    def generate_implementation_roadmap(self, opportunities: List[AutomationOpportunity]) -> Dict[str, Any]:
        """Generate comprehensive implementation roadmap"""
        
        # Sort opportunities by priority and ROI
        high_priority = [o for o in opportunities if o.priority_tier == "high"]
        medium_priority = [o for o in opportunities if o.priority_tier == "medium"]
        low_priority = [o for o in opportunities if o.priority_tier == "low"]
        
        # Calculate aggregate metrics
        total_annual_savings = sum(o.annual_cost_savings for o in opportunities)
        total_implementation_cost = sum(o.implementation_cost_estimate for o in opportunities)
        overall_roi = ((total_annual_savings - total_implementation_cost) / total_implementation_cost * 100) if total_implementation_cost > 0 else 0
        
        # Create phased implementation plan
        phase_1 = high_priority[:3]  # Top 3 high priority
        phase_2 = high_priority[3:] + medium_priority[:2]  # Remaining high + top medium
        phase_3 = medium_priority[2:] + low_priority[:3]  # Remaining opportunities
        
        roadmap = {
            "roadmap_summary": {
                "total_opportunities": len(opportunities),
                "high_priority_count": len(high_priority),
                "medium_priority_count": len(medium_priority),
                "low_priority_count": len(low_priority),
                "total_estimated_annual_savings": total_annual_savings,
                "total_implementation_cost": total_implementation_cost,
                "overall_roi_percentage": overall_roi,
                "estimated_payback_months": (total_implementation_cost / (total_annual_savings / 12)) if total_annual_savings > 0 else 999
            },
            
            "implementation_phases": {
                "phase_1_quick_wins": {
                    "duration_weeks": 8,
                    "opportunities": [self._opportunity_summary(o) for o in phase_1],
                    "phase_cost": sum(o.implementation_cost_estimate for o in phase_1),
                    "phase_annual_savings": sum(o.annual_cost_savings for o in phase_1),
                    "description": "High-impact, lower-complexity automations for immediate ROI"
                },
                "phase_2_strategic": {
                    "duration_weeks": 16,
                    "opportunities": [self._opportunity_summary(o) for o in phase_2],
                    "phase_cost": sum(o.implementation_cost_estimate for o in phase_2),
                    "phase_annual_savings": sum(o.annual_cost_savings for o in phase_2),
                    "description": "Strategic automations requiring more integration work"
                },
                "phase_3_optimization": {
                    "duration_weeks": 24,
                    "opportunities": [self._opportunity_summary(o) for o in phase_3],
                    "phase_cost": sum(o.implementation_cost_estimate for o in phase_3),
                    "phase_annual_savings": sum(o.annual_cost_savings for o in phase_3),
                    "description": "Advanced optimizations and remaining opportunities"
                }
            },
            
            "quick_wins": [
                self._opportunity_summary(o) for o in opportunities
                if o.complexity == AutomationComplexity.LOW and o.roi_percentage > 200
            ][:5],
            
            "highest_roi_opportunities": [
                self._opportunity_summary(o) for o in 
                sorted(opportunities, key=lambda x: x.roi_percentage, reverse=True)
            ][:5],
            
            "resource_requirements": {
                "n8n_development_hours": sum(o.estimated_implementation_weeks * 20 for o in opportunities),
                "api_integrations_needed": len(set(tool for o in opportunities for tool in o.source_tools + o.target_tools)),
                "testing_environments": 3,  # Dev, staging, prod
                "training_sessions": len(opportunities) // 3  # Group training sessions
            }
        }
        
        return roadmap
    
    def _opportunity_summary(self, opportunity: AutomationOpportunity) -> Dict[str, Any]:
        """Create summary dict for an opportunity"""
        return {
            "id": opportunity.id,
            "name": opportunity.name,
            "priority_tier": opportunity.priority_tier,
            "total_score": opportunity.total_score,
            "annual_savings": opportunity.annual_cost_savings,
            "implementation_cost": opportunity.implementation_cost_estimate,
            "roi_percentage": opportunity.roi_percentage,
            "payback_months": opportunity.payback_period_months,
            "complexity": opportunity.complexity.value,
            "business_impact": opportunity.business_impact.value,
            "estimated_weeks": opportunity.estimated_implementation_weeks,
            "tools_involved": opportunity.source_tools + opportunity.target_tools
        }

# Convenience functions
def generate_automation_opportunities(tool_inventory: Dict[str, dict], 
                                    integration_gaps: List[Dict],
                                    current_integrations: List[Dict] = None) -> Tuple[List[AutomationOpportunity], Dict[str, Any]]:
    """Generate automation opportunities and implementation roadmap"""
    engine = AutomationOpportunityEngine()
    opportunities = engine.identify_opportunities(tool_inventory, integration_gaps, current_integrations or [])
    roadmap = engine.generate_implementation_roadmap(opportunities)
    return opportunities, roadmap
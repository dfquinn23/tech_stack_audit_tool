# core/stage_gate_manager.py
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import json
from pathlib import Path
from datetime import datetime
import uuid

class AuditStage(Enum):
    DISCOVERY = 1
    ASSESSMENT = 2
    OPPORTUNITIES = 3
    DELIVERY = 4

@dataclass
class AuditState:
    client_name: str
    audit_id: str
    current_stage: AuditStage
    stage_completion: Dict[int, bool]
    tool_inventory: Dict[str, dict]
    integrations: List[dict]
    automation_opportunities: List[dict]
    client_domain: Optional[str]
    stakeholder_contacts: List[dict]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self):
        """Convert to dictionary with proper serialization"""
        data = asdict(self)
        data['current_stage'] = self.current_stage.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary with proper deserialization"""
        data['current_stage'] = AuditStage(data['current_stage'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)

class StageGateManager:
    def __init__(self, client_name: str, audit_id: Optional[str] = None, client_domain: Optional[str] = None):
        self.audit_id = audit_id or f"audit_{uuid.uuid4().hex[:8]}"
        self.client_name = client_name
        self.client_domain = client_domain
        self.state_file = Path(f"data/audit_sessions/{self.audit_id}.json")
        self.state = self.load_or_create_state()
        
    def load_or_create_state(self) -> AuditState:
        """Load existing audit state or create new one"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return AuditState.from_dict(data)
            except Exception as e:
                print(f"⚠️ Error loading state file: {e}. Creating new state.")
        
        return AuditState(
            client_name=self.client_name,
            audit_id=self.audit_id,
            current_stage=AuditStage.DISCOVERY,
            stage_completion={1: False, 2: False, 3: False, 4: False},
            tool_inventory={},
            integrations=[],
            automation_opportunities=[],
            client_domain=self.client_domain,
            stakeholder_contacts=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def save_state(self):
        """Save current state to file"""
        self.state.updated_at = datetime.now()
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.state_file, 'w') as f:
            json.dump(self.state.to_dict(), f, indent=2)
        
        print(f"💾 State saved: {self.state_file}")
    
    def get_stage_summary(self) -> str:
        """Get a summary of current audit progress"""
        completed_stages = sum(self.state.stage_completion.values())
        total_tools = len(self.state.tool_inventory)
        total_integrations = len(self.state.integrations)
        total_opportunities = len(self.state.automation_opportunities)
        
        return f"""
📊 Audit Progress Summary
Client: {self.state.client_name}
Current Stage: {self.state.current_stage.name}
Completed Stages: {completed_stages}/4

📦 Discovery: {total_tools} tools catalogued
🔗 Assessment: {total_integrations} integrations analyzed  
🤖 Opportunities: {total_opportunities} automation workflows identified
⏰ Last Updated: {self.state.updated_at.strftime('%Y-%m-%d %H:%M')}
        """
    
    # Gate Validation Methods
    def validate_discovery_gate(self) -> tuple[bool, List[str]]:
        """Gate 1: Complete inventory with required metadata"""
        issues = []
        required_fields = ['category', 'users', 'discovery_method']
        
        if len(self.state.tool_inventory) == 0:
            issues.append("No tools discovered")
            return False, issues
        
        for tool_name, tool_data in self.state.tool_inventory.items():
            missing_fields = [field for field in required_fields if field not in tool_data]
            if missing_fields:
                issues.append(f"{tool_name} missing: {', '.join(missing_fields)}")
        
        if not issues:
            return True, ["✅ All tools have required metadata"]
        return False, issues
    
    def validate_assessment_gate(self) -> tuple[bool, List[str]]:
        """Gate 2: Integration analysis and gap assessment complete"""
        issues = []
        tools = list(self.state.tool_inventory.keys())
        
        if len(tools) < 2:
            issues.append("Need at least 2 tools for integration analysis")
            return False, issues
        
        # Check for integration health assessments
        if len(self.state.integrations) == 0:
            issues.append("No integrations analyzed")
        
        # Verify integration data quality
        required_integration_fields = ['source_tool', 'target_tool', 'status', 'integration_type']
        for integration in self.state.integrations:
            missing_fields = [field for field in required_integration_fields if field not in integration]
            if missing_fields:
                issues.append(f"Integration record missing: {', '.join(missing_fields)}")
        
        if not issues:
            return True, ["✅ Integration analysis complete"]
        return False, issues
    
    def validate_opportunities_gate(self) -> tuple[bool, List[str]]:
        """Gate 3: Prioritized automation roadmap with n8n workflows"""
        issues = []
        
        if len(self.state.automation_opportunities) < 3:
            issues.append("Need at least 3 automation opportunities identified")
        
        # Check opportunity data quality
        required_opp_fields = ['name', 'priority_score', 'roi_estimate', 'n8n_workflow']
        for opp in self.state.automation_opportunities:
            missing_fields = [field for field in required_opp_fields if field not in opp]
            if missing_fields:
                issues.append(f"Opportunity '{opp.get('name', 'Unknown')}' missing: {', '.join(missing_fields)}")
            
            # Check priority scoring
            if opp.get('priority_score', 0) == 0:
                issues.append(f"Opportunity '{opp.get('name', 'Unknown')}' not properly scored")
        
        if not issues:
            return True, ["✅ Automation roadmap complete"]
        return False, issues
    
    def validate_delivery_gate(self) -> tuple[bool, List[str]]:
        """Gate 4: Client-ready deliverables"""
        issues = []
        
        # Check that all previous stages are completed
        if not all(self.state.stage_completion.values()):
            incomplete_stages = [f"Stage {i}" for i, completed in self.state.stage_completion.items() if not completed]
            issues.append(f"Incomplete stages: {', '.join(incomplete_stages)}")
        
        # Verify we have deliverable components
        if not self.state.tool_inventory:
            issues.append("No tool inventory for report")
        if not self.state.automation_opportunities:
            issues.append("No automation opportunities for presentation")
        
        if not issues:
            return True, ["✅ Ready for client delivery"]
        return False, issues
    
    def check_stage_gate(self, target_stage: AuditStage) -> tuple[bool, List[str]]:
        """Check if requirements are met to advance to target stage"""
        if target_stage == AuditStage.DISCOVERY:
            return True, ["✅ Starting discovery"]
        elif target_stage == AuditStage.ASSESSMENT:
            return self.validate_discovery_gate()
        elif target_stage == AuditStage.OPPORTUNITIES:
            return self.validate_assessment_gate()
        elif target_stage == AuditStage.DELIVERY:
            return self.validate_opportunities_gate()
        else:
            return False, ["Unknown stage"]
    
    def advance_stage(self, target_stage: AuditStage, force: bool = False) -> bool:
        """Advance to target stage if gates pass (or if forced)"""
        can_advance, messages = self.check_stage_gate(target_stage)
        
        if can_advance or force:
            self.state.current_stage = target_stage
            if target_stage.value > 1:  # Mark previous stage as complete
                self.state.stage_completion[target_stage.value - 1] = True
            self.save_state()
            
            print(f"🎯 Advanced to {target_stage.name}")
            for msg in messages:
                print(f"   {msg}")
            return True
        else:
            print(f"🚫 Cannot advance to {target_stage.name}")
            for msg in messages:
                print(f"   ❌ {msg}")
            return False
    
    def add_tool(self, tool_name: str, tool_data: dict):
        """Add or update tool in inventory"""
        self.state.tool_inventory[tool_name] = tool_data
        self.save_state()
        print(f"📦 Added tool: {tool_name}")
    
    def add_integration(self, integration_data: dict):
        """Add integration analysis result"""
        self.state.integrations.append(integration_data)
        self.save_state()
        print(f"🔗 Added integration: {integration_data.get('source_tool')} → {integration_data.get('target_tool')}")
    
    def add_automation_opportunity(self, opportunity_data: dict):
        """Add automation opportunity"""
        self.state.automation_opportunities.append(opportunity_data)
        self.save_state()
        print(f"🤖 Added opportunity: {opportunity_data.get('name')}")
    
    def get_tools_for_stage(self, stage: AuditStage) -> List[str]:
        """Get list of tools relevant for current analysis stage"""
        return list(self.state.tool_inventory.keys())
    
    def export_summary(self) -> dict:
        """Export audit summary for reporting"""
        return {
            'audit_info': {
                'client_name': self.state.client_name,
                'audit_id': self.audit_id,
                'current_stage': self.state.current_stage.name,
                'completion_status': self.state.stage_completion
            },
            'inventory_summary': {
                'total_tools': len(self.state.tool_inventory),
                'tools_by_category': self._group_tools_by_category(),
                'tools_by_criticality': self._group_tools_by_criticality()
            },
            'integration_summary': {
                'total_integrations': len(self.state.integrations),
                'integration_health': self._summarize_integration_health()
            },
            'automation_summary': {
                'total_opportunities': len(self.state.automation_opportunities),
                'high_priority_count': len([o for o in self.state.automation_opportunities if o.get('priority_score', 0) >= 12]),
                'total_estimated_roi': sum(o.get('roi_estimate', 0) for o in self.state.automation_opportunities)
            }
        }
    
    def _group_tools_by_category(self) -> dict:
        """Group tools by category for summary"""
        categories = {}
        for tool_name, tool_data in self.state.tool_inventory.items():
            category = tool_data.get('category', 'Unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(tool_name)
        return categories
    
    def _group_tools_by_criticality(self) -> dict:
        """Group tools by criticality for summary"""
        criticality = {}
        for tool_name, tool_data in self.state.tool_inventory.items():
            crit = tool_data.get('criticality', 'Unknown')
            if crit not in criticality:
                criticality[crit] = []
            criticality[crit].append(tool_name)
        return criticality
    
    def _summarize_integration_health(self) -> dict:
        """Summarize integration health status"""
        health_summary = {'healthy': 0, 'degraded': 0, 'broken': 0, 'missing': 0}
        for integration in self.state.integrations:
            status = integration.get('status', 'unknown').lower()
            if status in health_summary:
                health_summary[status] += 1
            else:
                health_summary['missing'] += 1
        return health_summary

# Convenience functions for quick operations
def create_audit_session(client_name: str, client_domain: str = None) -> StageGateManager:
    """Create a new audit session"""
    manager = StageGateManager(client_name, client_domain=client_domain)
    print(f"🚀 Created new audit session: {manager.audit_id}")
    print(manager.get_stage_summary())
    return manager

def load_audit_session(audit_id: str) -> StageGateManager:
    """Load existing audit session"""
    # Extract client name from existing file for initialization
    state_file = Path(f"data/audit_sessions/{audit_id}.json")
    if not state_file.exists():
        raise FileNotFoundError(f"Audit session {audit_id} not found")
    
    with open(state_file, 'r') as f:
        data = json.load(f)
    
    manager = StageGateManager(data['client_name'], audit_id)
    print(f"📂 Loaded audit session: {audit_id}")
    print(manager.get_stage_summary())
    return manager
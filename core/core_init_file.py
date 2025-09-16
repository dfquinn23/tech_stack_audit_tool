# core/__init__.py
"""
Tech Stack Audit Tool - Core Components
"""

__version__ = "1.0.0"

from .stage_gate_manager import StageGateManager, AuditStage, create_audit_session, load_audit_session
from .discovery_engine import DiscoveryEngine, enhance_existing_inventory
from .integration_health_checker import IntegrationHealthChecker, assess_tool_stack_integrations
from .integration_gap_analyzer import IntegrationGapAnalyzer, analyze_integration_gaps
from .automation_opportunity_engine import AutomationOpportunityEngine, generate_automation_opportunities

__all__ = [
    'StageGateManager',
    'AuditStage', 
    'create_audit_session',
    'load_audit_session',
    'DiscoveryEngine',
    'enhance_existing_inventory',
    'IntegrationHealthChecker',
    'assess_tool_stack_integrations',
    'IntegrationGapAnalyzer', 
    'analyze_integration_gaps',
    'AutomationOpportunityEngine',
    'generate_automation_opportunities'
]
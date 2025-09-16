# Tech Stack Audit Tool: Rapid Implementation Plan

## Architecture Overview: Stage-Gate Pipeline with Persistent State

We'll rebuild your pipeline around a **Stage-Gate Manager** that orchestrates your existing agents while maintaining persistent audit state. This eliminates repetition and creates predictable workflows.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DISCOVERY     │───▶│   ASSESSMENT    │───▶│ OPPORTUNITIES   │───▶│    DELIVERY     │
│                 │    │                 │    │                 │    │                 │
│ • Auto Discovery│    │ • Integration   │    │ • Automation    │    │ • Report Gen    │
│ • Tool Catalog  │    │   Health Check  │    │   Scoring       │    │ • Presentation  │
│ • Version Check │    │ • Gap Analysis  │    │ • n8n Workflows │    │ • Client Review │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
        ▲                        ▲                        ▲                        ▲
        │                        │                        │                        │
     Gate 1                   Gate 2                   Gate 3                   Gate 4
  Complete Inventory     Integration Map           Prioritized Roadmap      Client-Ready
```

## Implementation Plan: 4-Day Sprint

### Day 1: Core Architecture + Discovery
- **Morning**: Build Stage-Gate Manager and persistent state
- **Afternoon**: Implement automated discovery (domains, APIs, version checking)

### Day 2: Integration Assessment
- **Morning**: Build integration health checker and gap analysis
- **Afternoon**: Create integration mapping and data flow visualization

### Day 3: Automation Opportunities  
- **Morning**: Implement opportunity scoring and n8n workflow generation
- **Afternoon**: Test against your completed audit data

### Day 4: Report Generation + Validation
- **Morning**: Build consulting-grade report templates
- **Afternoon**: End-to-end validation and refinement

## Day 1 Implementation: Core Architecture

### 1.1 New Project Structure
```
tech_stack_audit_tool/
├── core/
│   ├── stage_gate_manager.py      # Main orchestrator
│   ├── audit_state.py            # Persistent state management
│   ├── discovery_engine.py       # Automated discovery
│   └── api_clients/              # Tool-specific API clients
├── agents/                       # Your existing agents (enhanced)
├── gates/                        # Stage gate validation logic
├── tools/                        # CrewAI tools for agents
├── templates/                    # Report templates
└── data/
    ├── audit_sessions/           # Per-client audit state
    └── discovery_cache/          # API response caching
```

### 1.2 Stage-Gate Manager (Replace run_pipeline.py)

```python
# core/stage_gate_manager.py
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import json
from pathlib import Path
from datetime import datetime

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
    created_at: datetime
    updated_at: datetime

class StageGateManager:
    def __init__(self, audit_id: str, client_name: str):
        self.audit_id = audit_id
        self.client_name = client_name
        self.state_file = Path(f"data/audit_sessions/{audit_id}.json")
        self.state = self.load_or_create_state()
        
    def load_or_create_state(self) -> AuditState:
        if self.state_file.exists():
            with open(self.state_file) as f:
                data = json.load(f)
                return AuditState(**data)
        else:
            return AuditState(
                client_name=self.client_name,
                audit_id=self.audit_id,
                current_stage=AuditStage.DISCOVERY,
                stage_completion={1: False, 2: False, 3: False, 4: False},
                tool_inventory={},
                integrations=[],
                automation_opportunities=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
    
    def save_state(self):
        self.state.updated_at = datetime.now()
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(asdict(self.state), f, indent=2, default=str)
    
    def can_advance_to_stage(self, stage: AuditStage) -> bool:
        """Check if all prerequisites are met to advance to given stage"""
        if stage == AuditStage.DISCOVERY:
            return True
        elif stage == AuditStage.ASSESSMENT:
            return self.validate_discovery_gate()
        elif stage == AuditStage.OPPORTUNITIES:
            return self.validate_assessment_gate()
        elif stage == AuditStage.DELIVERY:
            return self.validate_opportunities_gate()
        return False
    
    def validate_discovery_gate(self) -> bool:
        """Gate 1: Complete inventory with metadata"""
        required_fields = ['category', 'version', 'users', 'discovery_method']
        for tool_name, tool_data in self.state.tool_inventory.items():
            if not all(field in tool_data for field in required_fields):
                print(f"❌ Gate 1 Failed: {tool_name} missing required fields")
                return False
        
        if len(self.state.tool_inventory) == 0:
            print("❌ Gate 1 Failed: No tools discovered")
            return False
            
        print(f"✅ Gate 1 Passed: {len(self.state.tool_inventory)} tools catalogued")
        return True
    
    def validate_assessment_gate(self) -> bool:
        """Gate 2: Integration map and gap analysis complete"""
        # Check integration health assessments exist
        tools = list(self.state.tool_inventory.keys())
        expected_integrations = len(tools) * (len(tools) - 1) // 2  # n choose 2
        
        if len(self.state.integrations) < expected_integrations * 0.3:  # At least 30% coverage
            print("❌ Gate 2 Failed: Insufficient integration analysis")
            return False
            
        print(f"✅ Gate 2 Passed: {len(self.state.integrations)} integrations analyzed")
        return True
    
    def validate_opportunities_gate(self) -> bool:
        """Gate 3: Prioritized automation roadmap"""
        if len(self.state.automation_opportunities) < 3:
            print("❌ Gate 3 Failed: Insufficient automation opportunities identified")
            return False
            
        # Check that opportunities are properly scored
        for opp in self.state.automation_opportunities:
            if 'priority_score' not in opp or opp['priority_score'] == 0:
                print("❌ Gate 3 Failed: Opportunities not properly scored")
                return False
                
        print(f"✅ Gate 3 Passed: {len(self.state.automation_opportunities)} opportunities prioritized")
        return True
    
    def advance_stage(self, target_stage: AuditStage):
        """Advance to target stage if gates pass"""
        if self.can_advance_to_stage(target_stage):
            self.state.current_stage = target_stage
            self.state.stage_completion[target_stage.value - 1] = True
            self.save_state()
            print(f"🎯 Advanced to {target_stage.name}")
        else:
            print(f"🚫 Cannot advance to {target_stage.name} - gate requirements not met")
```

### 1.3 Automated Discovery Engine

```python
# core/discovery_engine.py
import requests
import dns.resolver
import socket
from typing import Dict, List, Optional
import asyncio
import aiohttp
from urllib.parse import urlparse

class DiscoveryEngine:
    def __init__(self):
        self.common_saas_patterns = {
            'zoom': ['zoom.us', 'zoomgov.com'],
            'microsoft365': ['outlook.office.com', 'teams.microsoft.com', 'sharepoint.com'],
            'slack': ['slack.com'],
            'salesforce': ['salesforce.com', 'force.com'],
            'google': ['workspace.google.com', 'gmail.com'],
            'atlassian': ['atlassian.net', 'jira.com', 'confluence.com'],
            'github': ['github.com', 'github.io'],
            'aws': ['amazonaws.com', 'aws.amazon.com'],
            'azure': ['azure.com', 'azurewebsites.net']
        }
        
    async def discover_domain_footprint(self, domain: str) -> Dict[str, List[str]]:
        """Discover SaaS tools by analyzing domain DNS records and subdomain patterns"""
        discovered_tools = {}
        
        # Check for common SaaS CNAME patterns
        subdomains_to_check = [
            'mail', 'email', 'mx', 'smtp',  # Email services
            'zoom', 'meet', 'video',        # Video conferencing  
            'slack', 'teams', 'chat',       # Communication
            'jira', 'confluence', 'wiki',   # Collaboration
            'github', 'gitlab', 'git',      # Development
            'aws', 'azure', 'cloud',        # Cloud services
            'crm', 'sales', 'support'       # Business tools
        ]
        
        for subdomain in subdomains_to_check:
            full_domain = f"{subdomain}.{domain}"
            tool_info = await self.check_subdomain_cname(full_domain)
            if tool_info:
                discovered_tools[subdomain] = tool_info
                
        return discovered_tools
    
    async def check_subdomain_cname(self, subdomain: str) -> Optional[Dict]:
        """Check CNAME records to identify SaaS providers"""
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            answers = resolver.resolve(subdomain, 'CNAME')
            
            for answer in answers:
                cname = str(answer.target).lower()
                
                # Match against known SaaS patterns
                for tool, patterns in self.common_saas_patterns.items():
                    for pattern in patterns:
                        if pattern in cname:
                            return {
                                'tool': tool,
                                'cname': cname,
                                'subdomain': subdomain,
                                'discovery_method': 'dns_cname'
                            }
        except Exception:
            pass
        
        return None
    
    async def check_api_endpoints(self, tool_list: List[str]) -> Dict[str, dict]:
        """Check API endpoints for tool version and status information"""
        results = {}
        
        api_endpoints = {
            'zoom': 'https://api.zoom.us/v2/users/me',
            'github': 'https://api.github.com/user',
            'slack': 'https://slack.com/api/api.test',
            # Add more as needed
        }
        
        async with aiohttp.ClientSession() as session:
            for tool in tool_list:
                if tool.lower() in api_endpoints:
                    endpoint = api_endpoints[tool.lower()]
                    try:
                        async with session.get(endpoint, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                results[tool] = {
                                    'status': 'active',
                                    'api_version': response.headers.get('api-version', 'unknown'),
                                    'discovery_method': 'api_probe'
                                }
                            else:
                                results[tool] = {
                                    'status': 'unreachable',
                                    'discovery_method': 'api_probe'
                                }
                    except Exception as e:
                        results[tool] = {
                            'status': 'error',
                            'error': str(e),
                            'discovery_method': 'api_probe'
                        }
        
        return results
    
    async def enhance_tool_inventory(self, existing_tools: Dict[str, dict], domain: str) -> Dict[str, dict]:
        """Enhance existing tool inventory with automated discovery"""
        
        # Discover additional tools via domain analysis
        domain_discoveries = await self.discover_domain_footprint(domain)
        
        # Check API status for known tools
        tool_names = list(existing_tools.keys())
        api_results = await self.check_api_endpoints(tool_names)
        
        # Merge discoveries
        enhanced_inventory = existing_tools.copy()
        
        # Add newly discovered tools
        for subdomain, tool_info in domain_discoveries.items():
            tool_name = tool_info['tool']
            if tool_name not in enhanced_inventory:
                enhanced_inventory[tool_name] = {
                    'category': 'Auto-discovered',
                    'version': 'unknown',
                    'users': ['unknown'],
                    'discovery_method': tool_info['discovery_method'],
                    'discovery_details': tool_info
                }
        
        # Enhance existing tools with API data
        for tool_name, api_data in api_results.items():
            if tool_name in enhanced_inventory:
                enhanced_inventory[tool_name].update(api_data)
        
        return enhanced_inventory
```

### 1.4 Enhanced Agent Integration

```python
# tools/audit_state_tool.py
from crewai_tools import BaseTool
from core.stage_gate_manager import StageGateManager

class AuditStateTool(BaseTool):
    name: str = "Audit State Manager"
    description: str = "Access and update persistent audit state across stages"
    
    def __init__(self, stage_manager: StageGateManager):
        super().__init__()
        self.stage_manager = stage_manager
    
    def _run(self, action: str, data: dict = None) -> str:
        if action == "get_inventory":
            return str(self.stage_manager.state.tool_inventory)
        elif action == "update_inventory":
            self.stage_manager.state.tool_inventory.update(data)
            self.stage_manager.save_state()
            return "Inventory updated"
        elif action == "add_integration":
            self.stage_manager.state.integrations.append(data)
            self.stage_manager.save_state()
            return "Integration added"
        elif action == "add_opportunity":
            self.stage_manager.state.automation_opportunities.append(data)
            self.stage_manager.save_state()
            return "Opportunity added"
        
        return "Unknown action"

# Enhanced agents with state management
def get_enhanced_research_agent(llm, stage_manager):
    audit_tool = AuditStateTool(stage_manager)
    
    return Agent(
        role="Technology Discovery Manager",
        goal="Complete comprehensive tech stack inventory using automated discovery",
        backstory="""You orchestrate both automated discovery and manual research to build
        a complete technology inventory. You ensure no tools are missed and all metadata is captured.""",
        tools=[audit_tool],
        memory=True,
        verbose=True,
        allow_delegation=True,
        llm=llm
    )
```

## Testing Against Your Completed Audit

Create a test script that loads your existing audit data and validates the new architecture:

```python
# test_stage_gate.py
import asyncio
from core.stage_gate_manager import StageGateManager, AuditStage
from core.discovery_engine import DiscoveryEngine

async def test_with_existing_audit():
    # Create test audit session
    manager = StageGateManager("test_audit_001", "Test Client")
    
    # Load your existing tech stack data
    existing_tools = {
        "Advent Axys": {"category": "Operations", "users": ["Portfolio Management"], "criticality": "High"},
        "FactSet": {"category": "Research", "users": ["Portfolio Management"], "criticality": "High"},
        # ... rest of your tools
    }
    
    # Test Stage 1: Discovery
    discovery = DiscoveryEngine()
    enhanced_inventory = await discovery.enhance_tool_inventory(existing_tools, "testclient.com")
    
    # Update state
    manager.state.tool_inventory = enhanced_inventory
    manager.save_state()
    
    # Test gate advancement
    if manager.can_advance_to_stage(AuditStage.ASSESSMENT):
        manager.advance_stage(AuditStage.ASSESSMENT)
        print("✅ Successfully advanced to Assessment stage")
    else:
        print("❌ Failed to advance - check gate requirements")

if __name__ == "__main__":
    asyncio.run(test_with_existing_audit())
```

## Next Steps for Tomorrow

1. **Morning**: Implement the Stage-Gate Manager and Discovery Engine
2. **Afternoon**: Test against your completed audit data and validate the approach
3. **Evening**: Plan Day 2 implementation (Integration Assessment)

Would you like me to start with creating the specific implementation files, or do you want to discuss any adjustments to this architecture first?

The key advantage of this approach is that it **completely eliminates repetition** - once a stage gate passes, you never need to re-analyze that data. Your existing agents become more powerful because they now have persistent context and clear boundaries.
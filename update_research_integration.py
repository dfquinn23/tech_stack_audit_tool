# core/update_research_integration.py
"""
Integration module that connects the Software Update Researcher and Feature Analyzer 
to the existing audit pipeline
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json
import csv

from core.software_update_researcher import SoftwareUpdateResearchAgent
from core.feature_analyzer import FeatureAnalyzer


class UpdateResearchIntegration:
    """
    Integrates automated update research into the audit pipeline
    """
    
    def __init__(
        self, 
        default_research_window_years: int = 2,
        research_depth: str = "medium"
    ):
        self.research_agent = SoftwareUpdateResearchAgent()
        self.feature_analyzer = FeatureAnalyzer()
        self.default_window_years = default_research_window_years
        self.research_depth = research_depth
        
        # Will be set by set_research_window()
        self.start_date = None
        self.end_date = None
    
    def set_research_window(
        self, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> None:
        """
        Set custom research window
        
        Args:
            start_date: Start date (YYYY-MM-DD) or None for auto-calculate
            end_date: End date (YYYY-MM-DD) or None for today
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        if start_date is None:
            # Calculate based on default window
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            start_dt = end_dt - timedelta(days=365 * self.default_window_years)
            start_date = start_dt.strftime("%Y-%m-%d")
        
        self.start_date = start_date
        self.end_date = end_date
        
        print(f"📅 Research window set: {start_date} to {end_date}")
    
    def load_tools_from_csv(self, csv_path: str) -> List[Dict]:
        """
        Load tools from CSV file
        
        Expected columns:
        - Tool Name (required)
        - Tool Type (required for best results)
        - Category (optional)
        - Used By (optional)
        - Criticality (optional)
        """
        tools = []
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tool_name = row.get('Tool Name', '').strip()
                if not tool_name:
                    continue
                
                # Get tool type - critical for good research
                tool_type = row.get('Tool Type', '').strip().lower()
                
                # If no Tool Type, try to infer from Category
                if not tool_type:
                    category = row.get('Category', '').strip().lower()
                    tool_type = self._infer_tool_type_from_category(category)
                
                tools.append({
                    'name': tool_name,
                    'type': tool_type,
                    'category': row.get('Category', '').strip(),
                    'used_by': row.get('Used By', '').strip(),
                    'criticality': row.get('Criticality', '').strip()
                })
        
        print(f"📦 Loaded {len(tools)} tools from CSV")
        return tools
    
    def _infer_tool_type_from_category(self, category: str) -> str:
        """Infer tool type from category if Tool Type not provided"""
        category_lower = category.lower()
        
        if 'crm' in category_lower or 'client' in category_lower:
            return 'crm'
        elif 'portfolio' in category_lower:
            return 'portfolio_management'
        elif 'research' in category_lower:
            return 'research_platform'
        elif 'custod' in category_lower or 'trading' in category_lower:
            return 'custodial'
        elif 'planning' in category_lower:
            return 'financial_planning'
        elif 'communication' in category_lower or 'video' in category_lower:
            return 'communication'
        elif 'productivity' in category_lower or 'office' in category_lower:
            return 'productivity_suite'
        elif 'operation' in category_lower or 'accounting' in category_lower:
            return 'operations'
        elif 'compliance' in category_lower:
            return 'compliance'
        else:
            return 'unknown'
    
    async def research_and_analyze_stack(
        self, 
        tools: List[Dict],
        research_depth: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete workflow: research updates and analyze them
        
        Args:
            tools: List of tool dictionaries
            research_depth: Override default research depth
            
        Returns:
            Complete analysis with roadmap
        """
        # Set research window if not already set
        if not self.start_date or not self.end_date:
            self.set_research_window()
        
        depth = research_depth or self.research_depth
        
        print(f"\n{'='*60}")
        print(f"🚀 Starting Automated Update Research & Analysis")
        print(f"{'='*60}")
        print(f"   Tools to research: {len(tools)}")
        print(f"   Date range: {self.start_date} to {self.end_date}")
        print(f"   Research depth: {depth}")
        print(f"{'='*60}\n")
        
        # Step 1: Research all tools
        print("📚 STEP 1: Researching Software Updates")
        research_results = await self.research_agent.research_tool_stack(
            tools=tools,
            start_date=self.start_date,
            end_date=self.end_date,
            research_depth=depth
        )
        
        print(f"\n✅ Research complete!")
        print(f"   Successfully researched: {research_results['successful']}/{research_results['total_tools']} tools")
        
        # Step 2: Analyze findings
        print(f"\n📊 STEP 2: Analyzing Update Findings")
        
        analyzed_tools = []
        for tool_name, research_data in research_results['results'].items():
            if not research_data.get('success'):
                print(f"   ⚠️ Skipping {tool_name} (research failed)")
                continue
            
            updates = research_data.get('updates', [])
            tool_type = research_data.get('tool_type', 'unknown')
            
            if not updates:
                print(f"   ℹ️ {tool_name}: No updates found")
                continue
            
            analysis = self.feature_analyzer.analyze_tool_updates(
                tool_name, updates, tool_type
            )
            analyzed_tools.append(analysis)
            
            print(f"   ✅ {tool_name}: {len(updates)} updates analyzed")
            print(f"      High priority: {len(analysis['high_priority'])}")
            print(f"      Medium priority: {len(analysis['medium_priority'])}")
        
        # Step 3: Create implementation roadmap
        print(f"\n🗺️  STEP 3: Creating Implementation Roadmap")
        roadmap = self.feature_analyzer.create_implementation_roadmap(analyzed_tools)
        
        print(f"\n{'='*60}")
        print(f"📋 ROADMAP SUMMARY")
        print(f"{'='*60}")
        print(f"   Total opportunities: {roadmap['total_opportunities']}")
        print(f"   Tools with opportunities: {roadmap['tools_with_opportunities']}")
        print(f"   Quick wins (< 30 days): {roadmap['quick_wins']['count']}")
        print(f"   Medium term (30-90 days): {roadmap['medium_term']['count']}")
        print(f"   Long term (90+ days): {roadmap['long_term']['count']}")
        print(f"{'='*60}\n")
        
        # Compile complete results
        complete_results = {
            'research_metadata': {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'research_depth': depth,
                'total_tools_researched': research_results['total_tools'],
                'successful_research': research_results['successful'],
                'timestamp': datetime.now().isoformat()
            },
            'raw_research_results': research_results,
            'analyzed_tools': analyzed_tools,
            'implementation_roadmap': roadmap,
            'executive_summary': self._generate_executive_summary(
                analyzed_tools, roadmap
            )
        }
        
        return complete_results
    
    def _generate_executive_summary(
        self, 
        analyzed_tools: List[Dict], 
        roadmap: Dict
    ) -> str:
        """Generate executive summary for audit report"""
        tools_with_updates = len(analyzed_tools)
        total_opportunities = roadmap['total_opportunities']
        quick_wins = roadmap['quick_wins']['count']
        
        # Calculate total potential impact
        total_hours = sum(
            tool['total_potential_impact']['estimated_hours_saved_per_week']
            for tool in analyzed_tools
        )
        total_value = sum(
            tool['total_potential_impact']['estimated_annual_value']
            for tool in analyzed_tools
        )
        
        summary = f"""
🎯 SOFTWARE UPDATE AUDIT SUMMARY

We analyzed your technology stack and discovered {total_opportunities} automation 
opportunities across {tools_with_updates} tools - features you're already paying 
for but may not be using.

💰 POTENTIAL VALUE:
   • {total_hours} hours/week in time savings potential
   • ${total_value:,.0f} estimated annual value
   
⚡ QUICK WINS:
   • {quick_wins} features can be implemented within 30 days
   • These require minimal effort but deliver immediate impact
   
📊 KEY FINDINGS:
"""
        
        # Add top 3 tools with most opportunities
        sorted_tools = sorted(
            analyzed_tools, 
            key=lambda x: len(x['high_priority']), 
            reverse=True
        )[:3]
        
        for i, tool in enumerate(sorted_tools, 1):
            high_count = len(tool['high_priority'])
            if high_count > 0:
                summary += f"   {i}. {tool['tool_name']}: {high_count} high-priority features\n"
        
        summary += f"\n📅 RESEARCH PERIOD: {self.start_date} to {self.end_date}"
        
        return summary
    
    def save_results(self, results: Dict, output_dir: str = "output") -> str:
        """Save results to JSON file"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"update_research_results_{timestamp}.json"
        filepath = output_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Results saved to: {filepath}")
        return str(filepath)
    
    def generate_markdown_report(
        self, 
        results: Dict, 
        output_dir: str = "output"
    ) -> str:
        """Generate client-ready markdown report"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"software_update_audit_{timestamp}.md"
        filepath = output_path / filename
        
        with open(filepath, 'w') as f:
            # Write header
            f.write("# Software Update & Automation Opportunities Audit\n\n")
            f.write(f"*Generated: {datetime.now().strftime('%B %d, %Y')}*\n\n")
            f.write("---\n\n")
            
            # Executive summary
            f.write("## Executive Summary\n\n")
            f.write(results['executive_summary'])
            f.write("\n\n---\n\n")
            
            # Quick wins
            roadmap = results['implementation_roadmap']
            if roadmap['quick_wins']['count'] > 0:
                f.write("## 🎯 Quick Wins (Implement in Next 30 Days)\n\n")
                for item in roadmap['quick_wins']['items']:
                    f.write(f"### {item['tool']} - {item['feature']}\n")
                    f.write(f"- **Impact**: {item['impact']}\n")
                    f.write(f"- **Difficulty**: {item['difficulty']}\n\n")
                f.write("---\n\n")
            
            # Detailed findings by tool
            f.write("## 📊 Detailed Findings by Tool\n\n")
            for tool in results['analyzed_tools']:
                f.write(f"### {tool['tool_name']}\n\n")
                f.write(f"*Tool Type: {tool['tool_type']}*\n\n")
                f.write(f"**Summary**: {tool['summary']}\n\n")
                
                if tool['high_priority']:
                    f.write("#### High Priority Updates\n\n")
                    for update in tool['high_priority']:
                        f.write(f"**{update['feature_name']}** *(Released: {update.get('release_date', 'N/A')})*\n\n")
                        f.write(f"{update['description']}\n\n")
                        f.write(f"- **Automation Value**: {update.get('automation_value', 'N/A')}\n")
                        f.write(f"- **Business Impact**: {update.get('business_impact', 'N/A')}\n")
                        f.write(f"- **Estimated Time Savings**: {update['analysis']['estimated_time_savings']}\n\n")
                
                f.write("---\n\n")
            
            # Implementation roadmap
            f.write("## 🗺️ Implementation Roadmap\n\n")
            f.write(f"{roadmap['executive_summary']}\n\n")
            
            f.write("### Phase 1: Quick Wins (0-30 Days)\n")
            f.write(f"*{roadmap['quick_wins']['recommendation']}*\n\n")
            for item in roadmap['quick_wins']['items']:
                f.write(f"- {item['tool']}: {item['feature']}\n")
            
            f.write("\n### Phase 2: Medium-Term Projects (30-90 Days)\n")
            f.write(f"*{roadmap['medium_term']['recommendation']}*\n\n")
            for item in roadmap['medium_term']['items']:
                f.write(f"- {item['tool']}: {item['feature']}\n")
            
            if roadmap['long_term']['count'] > 0:
                f.write("\n### Phase 3: Long-Term Initiatives (90+ Days)\n")
                f.write(f"*{roadmap['long_term']['recommendation']}*\n\n")
                for item in roadmap['long_term']['items']:
                    f.write(f"- {item['tool']}: {item['feature']}\n")
        
        print(f"📄 Report saved to: {filepath}")
        return str(filepath)


# Convenience function for pipeline integration
async def run_update_research_for_audit(
    csv_path: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    research_depth: str = "medium",
    output_dir: str = "output"
) -> Dict[str, Any]:
    """
    Complete update research workflow for audit pipeline
    
    Args:
        csv_path: Path to CSV file with tools
        start_date: Optional custom start date (YYYY-MM-DD)
        end_date: Optional custom end date (YYYY-MM-DD)
        research_depth: 'quick', 'medium', or 'deep'
        output_dir: Directory to save outputs
        
    Returns:
        Complete analysis results
    """
    integration = UpdateResearchIntegration(research_depth=research_depth)
    
    # Set custom date range if provided
    if start_date or end_date:
        integration.set_research_window(start_date, end_date)
    
    # Load tools from CSV
    tools = integration.load_tools_from_csv(csv_path)
    
    # Research and analyze
    results = await integration.research_and_analyze_stack(tools)
    
    # Save results
    integration.save_results(results, output_dir)
    integration.generate_markdown_report(results, output_dir)
    
    return results
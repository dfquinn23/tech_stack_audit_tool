#!/usr/bin/env python3
"""
CSV Enhancement Script
Adds 'Tool Type' column to existing CSV files by inferring from tool names and categories
"""

import csv
from pathlib import Path
from typing import Dict, List


class CSVToolTypeEnhancer:
    """Add Tool Type column to CSV files"""
    
    def __init__(self):
        # Mapping of tool names to types
        self.known_tools = {
            # Research Platforms
            'factset': 'research_platform',
            'bloomberg': 'research_platform',
            'bloomberg terminal': 'research_platform',
            'morningstar': 'research_platform',
            'morningstar direct': 'research_platform',
            
            # Portfolio Management
            'orion': 'portfolio_management',
            'orion eclipse': 'portfolio_management',
            'addepar': 'portfolio_management',
            'schwab portfoliocenter': 'portfolio_management',
            'venn': 'portfolio_management',
            
            # CRM
            'redtail': 'crm',
            'redtail crm': 'crm',
            'salesforce': 'crm',
            'wealthbox': 'crm',
            'wealth box': 'crm',
            
            # Custodial
            'schwab': 'custodial',
            'charles schwab': 'custodial',
            'fidelity': 'custodial',
            'fidelity institutional': 'custodial',
            'pershing': 'custodial',
            'jump': 'custodial',
            
            # Financial Planning
            'rightcapital': 'financial_planning',
            'right capital': 'financial_planning',
            'moneyguidepro': 'financial_planning',
            'emoney': 'financial_planning',
            'wealthscape': 'financial_planning',
            
            # Communication
            'zoom': 'communication',
            'microsoft teams': 'communication',
            'teams': 'communication',
            'slack': 'communication',
            
            # Productivity
            'microsoft 365': 'productivity_suite',
            '365': 'productivity_suite',
            'office 365': 'productivity_suite',
            'microsoft outlook': 'productivity_suite',
            'microsoft excel': 'productivity_suite',
            'microsoft sharepoint': 'productivity_suite',
            'google workspace': 'productivity_suite',
            
            # Operations
            'docusign': 'operations',
            'quickbooks': 'operations',
            'quickbooks desktop': 'operations',
            'adp': 'operations',
            'adp workforce now': 'operations',
            'canoe': 'operations',
            'global relay': 'compliance',
            
            # Cloud/Infrastructure
            'aws': 'cloud_services',
            'aws efs': 'cloud_services',
            'citrix': 'infrastructure',
            
            # Other
            'cssi': 'operations',
            'zocks': 'productivity_suite',
        }
        
        # Category keywords for inference
        self.category_keywords = {
            'research_platform': ['research', 'data', 'analytics', 'terminal'],
            'portfolio_management': ['portfolio', 'performance', 'reporting'],
            'crm': ['crm', 'client', 'relationship'],
            'custodial': ['custodian', 'custody', 'trading', 'brokerage'],
            'financial_planning': ['planning', 'financial plan'],
            'communication': ['communication', 'video', 'meeting', 'chat'],
            'productivity_suite': ['productivity', 'office', 'email'],
            'operations': ['operations', 'accounting', 'document', 'back office'],
            'compliance': ['compliance', 'archive', 'supervision']
        }
    
    def infer_tool_type(self, tool_name: str, category: str = '') -> str:
        """Infer tool type from name and category"""
        tool_lower = tool_name.lower().strip()
        category_lower = category.lower().strip()
        
        # Check known tools first
        if tool_lower in self.known_tools:
            return self.known_tools[tool_lower]
        
        # Check for partial matches in tool name
        for known_tool, tool_type in self.known_tools.items():
            if known_tool in tool_lower or tool_lower in known_tool:
                return tool_type
        
        # Try to infer from category
        for tool_type, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in category_lower:
                    return tool_type
        
        # Default
        return 'unknown'
    
    def enhance_csv(self, input_path: str, output_path: str = None) -> None:
        """
        Add Tool Type column to CSV
        
        Args:
            input_path: Path to input CSV
            output_path: Path to output CSV (if None, creates new file with _enhanced suffix)
        """
        input_file = Path(input_path)
        
        if not input_file.exists():
            print(f"❌ File not found: {input_path}")
            return
        
        # Determine output path
        if output_path is None:
            output_file = input_file.parent / f"{input_file.stem}_enhanced{input_file.suffix}"
        else:
            output_file = Path(output_path)
        
        print(f"\n📄 Processing: {input_path}")
        
        # Read input CSV
        rows = []
        fieldnames = []
        
        with open(input_file, 'r') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
        
        # Check if Tool Type already exists
        if 'Tool Type' in fieldnames:
            print(f"⚠️ Tool Type column already exists!")
            user_input = input("   Overwrite existing Tool Type values? (y/n): ")
            if user_input.lower() != 'y':
                print("   Skipping file.")
                return
        else:
            # Add Tool Type to fieldnames
            fieldnames = list(fieldnames) + ['Tool Type']
        
        # Process rows
        enhanced_count = 0
        for row in rows:
            tool_name = row.get('Tool Name', '')
            category = row.get('Category', '')
            
            # Infer tool type
            tool_type = self.infer_tool_type(tool_name, category)
            row['Tool Type'] = tool_type
            
            if tool_type != 'unknown':
                enhanced_count += 1
        
        # Write output CSV
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✅ Enhanced CSV saved to: {output_file}")
        print(f"   Total tools: {len(rows)}")
        print(f"   Successfully typed: {enhanced_count}")
        print(f"   Unknown types: {len(rows) - enhanced_count}")
        
        # Show tools with unknown type
        unknown_tools = [row['Tool Name'] for row in rows if row.get('Tool Type') == 'unknown']
        if unknown_tools:
            print(f"\n⚠️ Tools with unknown type (manual review recommended):")
            for tool in unknown_tools[:10]:  # Show first 10
                print(f"   - {tool}")
            if len(unknown_tools) > 10:
                print(f"   ... and {len(unknown_tools) - 10} more")
    
    def process_directory(self, directory: str = "data") -> None:
        """Process all CSV files in a directory"""
        dir_path = Path(directory)
        
        if not dir_path.exists():
            print(f"❌ Directory not found: {directory}")
            return
        
        csv_files = list(dir_path.glob("*.csv"))
        csv_files = [f for f in csv_files if '_enhanced' not in f.name]
        
        if not csv_files:
            print(f"No CSV files found in {directory}")
            return
        
        print(f"\n🔍 Found {len(csv_files)} CSV files to process:")
        for i, f in enumerate(csv_files, 1):
            print(f"   {i}. {f.name}")
        
        print("\n" + "="*60)
        
        for csv_file in csv_files:
            self.enhance_csv(str(csv_file))
            print("="*60)


def main():
    """Main function"""
    print("\n" + "="*60)
    print("📊 CSV Tool Type Enhancement Script")
    print("="*60)
    print("\nThis script adds a 'Tool Type' column to your CSV files.")
    print("Tool Type is required for optimal update research results.")
    print("\n" + "="*60)
    
    enhancer = CSVToolTypeEnhancer()
    
    # Process all CSVs in data directory
    enhancer.process_directory("data")
    
    print("\n✅ Processing complete!")
    print("\nNext steps:")
    print("  1. Review the enhanced CSV files (*_enhanced.csv)")
    print("  2. Manually update any 'unknown' tool types")
    print("  3. Use the enhanced CSVs with the update research system")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()

# streamlit_app.py
"""
Tech Stack Audit Tool - Streamlit Dashboard
Professional interface for running client audits
"""

import streamlit as st
import asyncio
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import io
import zipfile

# Configure page
st.set_page_config(
    page_title="Tech Stack Audit Tool",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import your audit components
try:
    from enhanced_run_pipeline_day2 import EnhancedAuditPipelineDay2
    from core.stage_gate_manager import load_audit_session
    SYSTEM_READY = True
except ImportError as e:
    st.error(f"System not ready: {e}")
    SYSTEM_READY = False

# Custom CSS for professional appearance
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    .success-alert {
        background: #d1fae5;
        border: 1px solid #10b981;
        padding: 1rem;
        border-radius: 8px;
        color: #047857;
    }
    .warning-alert {
        background: #fef3c7;
        border: 1px solid #f59e0b;
        padding: 1rem;
        border-radius: 8px;
        color: #92400e;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔧 Tech Stack Audit Tool</h1>
        <p>Systematic, AI-powered technology audits with quantified automation opportunities</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Choose Action",
            ["🚀 New Audit", "📊 View Results", "⚙️ Settings", "📖 Help"]
        )
    
    if not SYSTEM_READY:
        st.error("System not ready. Please run setup and check your installation.")
        return
    
    if page == "🚀 New Audit":
        new_audit_page()
    elif page == "📊 View Results":
        view_results_page()
    elif page == "⚙️ Settings":
        settings_page()
    elif page == "📖 Help":
        help_page()

def new_audit_page():
    st.header("🚀 New Client Audit")
    
    # Client Information
    col1, col2 = st.columns(2)
    
    with col1:
        client_name = st.text_input(
            "Client Name",
            placeholder="ABC Wealth Management",
            help="Enter the full name of your client"
        )
        
    with col2:
        client_domain = st.text_input(
            "Client Domain (Optional)",
            placeholder="abcwealth.com",
            help="For automated discovery (optional)"
        )
    
    # Tool Inventory Upload
    st.subheader("📋 Tool Inventory")
    
    # Option 1: Upload CSV
    uploaded_file = st.file_uploader(
        "Upload Client Tool List (CSV)",
        type=['csv'],
        help="Upload a CSV with columns: Tool Name, Category, Used By, Criticality"
    )
    
    # Option 2: Manual Entry
    if st.checkbox("Or enter tools manually"):
        with st.expander("Manual Tool Entry"):
            col1, col2, col3, col4 = st.columns(4)
            
            if 'manual_tools' not in st.session_state:
                st.session_state.manual_tools = []
            
            with col1:
                tool_name = st.text_input("Tool Name")
            with col2:
                category = st.selectbox("Category", 
                    ["Operations", "Research", "CRM", "Productivity", "Custodian", "Other"])
            with col3:
                users = st.text_input("Used By", placeholder="Portfolio Management")
            with col4:
                criticality = st.selectbox("Criticality", ["High", "Medium", "Low"])
            
            if st.button("Add Tool"):
                if tool_name:
                    st.session_state.manual_tools.append({
                        "Tool Name": tool_name,
                        "Category": category,
                        "Used By": users,
                        "Criticality": criticality
                    })
                    st.success(f"Added {tool_name}")
            
            if st.session_state.manual_tools:
                st.dataframe(pd.DataFrame(st.session_state.manual_tools))
                
                if st.button("Clear All Tools"):
                    st.session_state.manual_tools = []
                    st.rerun()
    
    # Audit Configuration
    st.subheader("⚙️ Audit Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        enable_discovery = st.checkbox(
            "Enable Automated Discovery", 
            value=True,
            help="Scan client domain for additional tools"
        )
        
    with col2:
        auto_advance = st.checkbox(
            "Auto-advance Stages", 
            value=True,
            help="Automatically advance through audit stages"
        )
    
    # Run Audit Button
    st.markdown("---")
    
    if st.button("🚀 Start Complete Audit", type="primary", use_container_width=True):
        if not client_name:
            st.error("Please enter a client name")
            return
            
        if not uploaded_file and not st.session_state.get('manual_tools'):
            st.error("Please upload a CSV file or enter tools manually")
            return
        
        # Run the audit
        run_audit(client_name, client_domain, uploaded_file, enable_discovery, auto_advance)

def run_audit(client_name, client_domain, uploaded_file, enable_discovery, auto_advance):
    """Run the complete audit process"""
    
    # Create progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.empty()
    
    # Prepare CSV data
    csv_path = None
    if uploaded_file:
        # Save uploaded file
        csv_path = f"data/temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        Path("data").mkdir(exist_ok=True)
        
        with open(csv_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    
    elif st.session_state.get('manual_tools'):
        # Create CSV from manual tools
        csv_path = f"data/manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df = pd.DataFrame(st.session_state.manual_tools)
        df.to_csv(csv_path, index=False)
    
    try:
        # Run audit asynchronously
        status_text.info("🔄 Starting audit pipeline...")
        progress_bar.progress(10)
        
        # Create audit pipeline
        pipeline = EnhancedAuditPipelineDay2(
            client_name=client_name,
            client_domain=client_domain if client_domain else None
        )
        
        progress_bar.progress(20)
        status_text.info("🔍 Running discovery stage...")
        
        # Run the complete audit
        # Note: We need to run this synchronously in Streamlit
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success = loop.run_until_complete(
                pipeline.run_complete_enhanced_audit(
                    csv_path=csv_path,
                    auto_advance=auto_advance
                )
            )
            
            progress_bar.progress(100)
            
            if success:
                status_text.success("✅ Audit completed successfully!")
                
                # Display results
                display_audit_results(pipeline)
                
                # Store audit ID for later viewing
                st.session_state.last_audit_id = pipeline.stage_manager.audit_id
                
            else:
                status_text.error("❌ Audit failed - check the logs for details")
                
        finally:
            loop.close()
            
        # Cleanup temp files
        if csv_path and Path(csv_path).exists():
            Path(csv_path).unlink()
            
    except Exception as e:
        status_text.error(f"❌ Audit failed: {str(e)}")
        st.exception(e)

def display_audit_results(pipeline):
    """Display audit results in an organized way"""
    
    st.subheader("📊 Audit Results")
    
    # Get summary data
    summary = pipeline.stage_manager.export_summary()
    gap_analysis = getattr(pipeline.stage_manager.state, 'gap_analysis', {})
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Tools Analyzed", 
            summary['inventory_summary']['total_tools']
        )
    
    with col2:
        st.metric(
            "Integrations Assessed",
            summary['integration_summary']['total_integrations']
        )
    
    with col3:
        st.metric(
            "Opportunities Found",
            summary['automation_summary']['total_opportunities']
        )
    
    with col4:
        annual_value = gap_analysis.get('analysis_summary', {}).get('total_estimated_annual_value', 0)
        st.metric(
            "Annual Savings Potential",
            f"${annual_value:,}"
        )
    
    # Detailed results tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Discovery", "🔗 Integrations", "🤖 Opportunities", "📋 Report"])
    
    with tab1:
        st.subheader("Tool Inventory")
        
        # Convert tools to dataframe
        tools_data = []
        for tool_name, tool_data in pipeline.stage_manager.state.tool_inventory.items():
            tools_data.append({
                "Tool": tool_name,
                "Category": tool_data.get('category', 'Unknown'),
                "Users": ', '.join(tool_data.get('users', [])),
                "Criticality": tool_data.get('criticality', 'Unknown'),
                "Discovery Method": tool_data.get('discovery_method', 'Unknown')
            })
        
        if tools_data:
            df_tools = pd.DataFrame(tools_data)
            st.dataframe(df_tools, use_container_width=True)
    
    with tab2:
        st.subheader("Integration Health")
        
        if pipeline.stage_manager.state.integrations:
            integration_data = []
            for integration in pipeline.stage_manager.state.integrations:
                integration_data.append({
                    "Source": integration.get('source_tool', 'Unknown'),
                    "Target": integration.get('target_tool', 'Unknown'),
                    "Status": integration.get('status', 'Unknown'),
                    "Health Score": f"{integration.get('health_score', 0)}/100",
                    "Business Criticality": integration.get('business_criticality', 'Unknown')
                })
            
            df_integrations = pd.DataFrame(integration_data)
            st.dataframe(df_integrations, use_container_width=True)
        else:
            st.info("No integration assessments completed yet")
    
    with tab3:
        st.subheader("Automation Opportunities")
        
        if pipeline.stage_manager.state.automation_opportunities:
            for i, opp in enumerate(pipeline.stage_manager.state.automation_opportunities, 1):
                with st.expander(f"{i}. {opp.get('name', 'Unknown Opportunity')}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Priority Score", f"{opp.get('priority_score', 0)}/25")
                    with col2:
                        st.metric("Annual Savings", f"${opp.get('roi_estimate', 0):,}")
                    with col3:
                        st.metric("Implementation", opp.get('implementation_effort', 'Unknown'))
                    
                    if 'n8n_workflow' in opp:
                        st.write("**n8n Workflow:**", opp['n8n_workflow'].get('description', 'No description'))
        else:
            st.info("No automation opportunities identified yet")
    
    with tab4:
        st.subheader("Generated Reports")
        
        # List generated report files
        output_dir = Path("output")
        if output_dir.exists():
            report_files = list(output_dir.glob(f"*{pipeline.stage_manager.audit_id}*"))
            
            if report_files:
                for report_file in report_files:
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"📄 {report_file.name}")
                    
                    with col2:
                        with open(report_file, 'rb') as f:
                            st.download_button(
                                "Download",
                                f.read(),
                                file_name=report_file.name,
                                mime='application/octet-stream',
                                key=f"download_{report_file.name}"
                            )
            else:
                st.info("No report files found")
        else:
            st.info("Output directory not found")

def view_results_page():
    """Page for viewing previous audit results"""
    st.header("📊 Previous Audit Results")
    
    # List available audit sessions
    audit_dir = Path("data/audit_sessions")
    if not audit_dir.exists():
        st.info("No previous audits found")
        return
    
    audit_files = list(audit_dir.glob("*.json"))
    if not audit_files:
        st.info("No previous audits found")
        return
    
    # Create dropdown of audits
    audit_options = []
    for audit_file in sorted(audit_files, key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            with open(audit_file) as f:
                audit_data = json.load(f)
                client_name = audit_data.get('client_name', 'Unknown')
                created_at = audit_data.get('created_at', '')
                audit_id = audit_data.get('audit_id', audit_file.stem)
                
                display_name = f"{client_name} - {created_at[:10]} ({audit_id})"
                audit_options.append((display_name, audit_id))
        except:
            continue
    
    if not audit_options:
        st.info("No valid audit sessions found")
        return
    
    selected_audit = st.selectbox(
        "Select Audit to View",
        audit_options,
        format_func=lambda x: x[0]
    )
    
    if selected_audit and st.button("Load Audit Results"):
        try:
            # Load the audit session
            pipeline = EnhancedAuditPipelineDay2(audit_id=selected_audit[1])
            
            st.success(f"Loaded audit: {selected_audit[0]}")
            display_audit_results(pipeline)
            
        except Exception as e:
            st.error(f"Failed to load audit: {e}")

def settings_page():
    """Settings and configuration page"""
    st.header("⚙️ Settings")
    
    # System status
    st.subheader("System Status")
    
    # Check environment
    env_file = Path(".env")
    if env_file.exists():
        st.success("✅ Environment file configured")
    else:
        st.error("❌ .env file missing")
        st.code("""
Create .env file with:
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4
        """)
    
    # Check directories
    required_dirs = ["data", "output", "core"]
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            st.success(f"✅ {dir_name}/ directory exists")
        else:
            st.error(f"❌ {dir_name}/ directory missing")
    
    # Configuration options
    st.subheader("Configuration")
    
    # Default settings
    with st.expander("Default Audit Settings"):
        default_auto_discovery = st.checkbox("Enable auto-discovery by default", value=True)
        default_auto_advance = st.checkbox("Auto-advance stages by default", value=True)
        
        if st.button("Save Defaults"):
            # Could save to a config file
            st.success("Settings saved")
    
    # Clear cache
    st.subheader("Maintenance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clear Discovery Cache"):
            cache_dir = Path("data/discovery_cache")
            if cache_dir.exists():
                import shutil
                shutil.rmtree(cache_dir)
                cache_dir.mkdir()
                st.success("Discovery cache cleared")
    
    with col2:
        if st.button("Clear Integration Cache"):
            cache_dir = Path("data/integration_cache")
            if cache_dir.exists():
                import shutil
                shutil.rmtree(cache_dir)
                cache_dir.mkdir()
                st.success("Integration cache cleared")

def help_page():
    """Help and documentation page"""
    st.header("📖 Help & Documentation")
    
    # Quick start guide
    with st.expander("🚀 Quick Start Guide", expanded=True):
        st.markdown("""
        ### Running Your First Audit
        
        1. **Client Information**: Enter client name and domain
        2. **Tool Inventory**: Upload CSV or enter tools manually
        3. **Configuration**: Choose discovery and advancement options
        4. **Run Audit**: Click "Start Complete Audit"
        5. **Review Results**: Check all four tabs for comprehensive results
        
        ### CSV Format
        Your CSV should have these columns:
        - `Tool Name`: Name of the software/tool
        - `Category`: Operations, Research, CRM, etc.
        - `Used By`: Department or team names
        - `Criticality`: High, Medium, or Low
        """)
    
    # System information
    with st.expander("🔧 System Information"):
        st.markdown(f"""
        ### Current Configuration
        - **System Ready**: {SYSTEM_READY}
        - **Data Directory**: {Path('data').exists()}
        - **Output Directory**: {Path('output').exists()}
        - **Core Modules**: {Path('core').exists()}
        
        ### Audit Process
        The system follows a 4-stage process:
        1. **Discovery**: Tool inventory and automated discovery
        2. **Assessment**: Integration health and gap analysis  
        3. **Opportunities**: Automation opportunity identification
        4. **Delivery**: Report generation and client deliverables
        """)
    
    # Troubleshooting
    with st.expander("🚨 Troubleshooting"):
        st.markdown("""
        ### Common Issues
        
        **"System not ready" error**:
        - Check that all core modules are installed
        - Run: `python test_complete_system.py`
        
        **"No automation opportunities found"**:
        - Ensure you have at least 3-4 tools in inventory
        - Check that integration assessment completed successfully
        
        **Slow performance**:
        - Large tool inventories (50+ tools) take longer
        - Consider running smaller batches
        
        **Report generation fails**:
        - Check that output directory exists and is writable
        - Ensure audit completed all 4 stages successfully
        """)

if __name__ == "__main__":
    main()

# Quick Test Instructions

## 1. Setup (5 minutes)

```bash
# Install new dependencies
pip install aiohttp dnspython asyncio-throttle

# Create directory structure
mkdir -p data/audit_sessions
mkdir -p data/discovery_cache
mkdir -p output

# Your existing .env should work, but make sure you have:
# OPENAI_API_KEY=your_key
# OPENAI_MODEL=gpt-4  # or your preferred model
```

## 2. Test the Stage-Gate System (10 minutes)

```bash
# Run the test with your existing data
python test_stage_gate_system.py
```

This will:
- ✅ Load your existing tech stack from CSV
- ✅ Test automated discovery (domain scanning, API probes)
- ✅ Validate all stage gates
- ✅ Create a complete audit session
- ✅ Save persistent state you can reload later

**Expected Output:**
```
🚀 Testing Stage-Gate Architecture with Existing Audit Data
📦 Stage 1: Populating Discovery data...
🚪 Testing Stage 1 Gate...
✅ Advanced to Assessment stage
🔗 Stage 2: Simulating Integration Assessment...
...
🎉 Stage-Gate Architecture Test Completed Successfully!
✅ Test completed. Audit session saved as: audit_12345678
```

## 3. Test Enhanced Pipeline (15 minutes)

```bash
# Test the full enhanced pipeline
python enhanced_run_pipeline.py
```

This will run your existing CrewAI agents through the new Stage-Gate architecture.

**What You Should See:**
1. **Discovery Stage**: Auto-discover tools, enhance with API data
2. **Assessment Stage**: Analyze integrations using your audit agent
3. **Opportunities Stage**: Generate n8n workflows using your integration agent  
4. **Delivery Stage**: Create final report using your report writer

## 4. Validate Results

Check these files were created:
- `data/audit_sessions/audit_[id].json` - Persistent audit state
- `output/audit_report_[id]_[timestamp].md` - Final report

## 5. Next Steps Decision Point

After testing, you should see:

**✅ If Everything Works:**
- Proceed to Day 2 implementation (Integration Assessment tools)
- The stage-gate system eliminates repetition
- Your agents now have persistent context

**⚠️ If Issues Found:**
- Review error messages for missing dependencies
- Check .env configuration
- Validate CSV file format matches expected columns

## Quick Validation Commands

```bash
# Check if audit session was saved properly
ls -la data/audit_sessions/

# View the audit state
cat data/audit_sessions/audit_*.json | jq '.current_stage'

# Check discovery cache
ls -la data/discovery_cache/

# View generated report
head -50 output/audit_report_*.md
```

## Troubleshooting Common Issues

**DNS Resolution Errors:**
```bash
# If you get DNS errors during discovery:
export PYTHONPATH=$PWD:$PYTHONPATH
python -c "import socket; print(socket.gethostbyname('google.com'))"
```

**CrewAI Version Issues:**
```bash
# Check CrewAI version
pip show crewai
# Should be 0.28.0 or later for best compatibility
```

**API Key Issues:**
```bash
# Test OpenAI connection
python llm_smoke_test.py
```

Run these tests and let me know the results - then we'll continue with Day 2 implementation!
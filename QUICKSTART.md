# FinGuard IntelliAgent - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Verify Setup
```bash
python3 verify_setup.py
```

Expected output: `🎉 All checks passed!`

### 2. Create Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 5. Test Components

**Backend:**
```bash
python backend/app.py
# Open http://localhost:8000/docs
```

**Agent Orchestrator:**
```bash
python agent/orchestrator.py
```

**Tools:**
```bash
python tools/sms_parser_tool.py
python tools/insights_tool.py
python tools/invoice_collection_tool.py
```

## 📚 Documentation

- **Full README:** [README.md](README.md)
- **Architecture:** [docs/PROJECT_DOCUMENTATION.md](docs/PROJECT_DOCUMENTATION.md)
- **Milestone 1 Summary:** [docs/MILESTONE_1_SUMMARY.md](docs/MILESTONE_1_SUMMARY.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

## 📂 Key Files

| File | Purpose |
|------|---------|
| `backend/app.py` | FastAPI application |
| `agent/orchestrator.py` | ADK agent orchestrator |
| `tools/sms_parser_tool.py` | SMS transaction parser |
| `tools/insights_tool.py` | Financial insights generator |
| `tools/invoice_collection_tool.py` | Invoice tracking |

## 🎯 Current Status

**Milestone 1:** ✅ Complete (Setup & Scaffolding)  
**Milestone 2:** 🚧 Coming Soon (Full Implementation)

## 💡 Quick Examples

### Parse SMS (Placeholder)
```python
from tools import parse_transaction_sms

result = parse_transaction_sms(
    "RB12KLM Confirmed. You received Ksh5,000..."
)
```

### Generate Insights (Placeholder)
```python
from tools import analyze_transactions

report = analyze_transactions(
    transactions=[...],
    analysis_type="comprehensive"
)
```

### Track Invoice (Placeholder)
```python
from tools import create_invoice_reminder

result = create_invoice_reminder({
    "invoice_id": "INV-001",
    "customer_name": "ABC Ltd",
    "amount": 15000,
    "due_date": "2025-12-01"
})
```

## 🆘 Troubleshooting

**Import errors?**
- Make sure you're in the virtual environment
- Run `pip install -r requirements.txt`

**Script won't run?**
- Check Python version: `python3 --version` (need 3.10+)
- Verify you're in the project root directory

**API errors?**
- Milestone 1 is placeholder only
- Full implementation comes in Milestone 2

## 📞 Support

- 📖 Read the docs in `docs/`
- 🐛 Report issues on GitHub
- 💬 Check [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Built for Kenyan SMEs | Powered by Anthropic ADK** 🇰🇪

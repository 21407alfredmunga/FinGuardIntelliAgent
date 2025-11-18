# FinGuard IntelliAgent

**ADK Capstone Project | Enterprise Agents Track**

## 🎯 Project Pitch

FinGuard IntelliAgent is an AI-powered financial automation agent designed specifically for Kenyan Small and Medium Enterprises (SMEs). It transforms the chaos of SMS-based mobile money transactions into structured financial insights, automates invoice collection, and provides intelligent financial planning support—all through natural language interaction.

## 🔍 Problem Statement

Kenyan SMEs face significant financial management challenges:

- **Transaction Overload**: Business owners receive 50-200+ M-Pesa/Airtel Money SMS notifications daily, making manual tracking impossible
- **Manual Data Entry**: Entrepreneurs spend 5-10 hours weekly copying transaction data from SMS into spreadsheets
- **Lost Revenue**: Delayed or forgotten invoice follow-ups result in 15-30% revenue leakage
- **Poor Financial Visibility**: Without automated systems, SMEs lack real-time insights into cash flow, spending patterns, and profitability
- **Limited Resources**: SMEs can't afford expensive accounting software or dedicated financial staff

**The Impact**: According to Kenya's FinAccess survey, 68% of SMEs lack proper financial records, directly contributing to 40% business failure rate within the first year.

## 💡 High-Level Solution

FinGuard IntelliAgent leverages **Anthropic's Agent Development Kit (ADK)** to create an intelligent, multi-tool agent system:

### Core Capabilities (Milestone 1 Scope)

1. **SMS Transaction Parser**
   - Extracts structured data from M-Pesa/Airtel Money SMS messages
   - Identifies transaction type, amount, recipient/sender, and timestamp
   - Handles various SMS formats and edge cases

2. **Financial Insights Engine**
   - Analyzes transaction patterns
   - Provides cash flow summaries
   - Identifies spending categories and trends

3. **Invoice Collection Automation**
   - Tracks outstanding invoices
   - Generates automated follow-up messages
   - Provides payment status dashboards

### How ADK Agents + Tools Solve the Workflow

```
User Request (Natural Language)
        ↓
[ADK Agent Orchestrator]
        ↓
   (Planning & Tool Selection)
        ↓
    ┌───┴───┬─────────────┬──────────────┐
    ↓       ↓             ↓              ↓
SMS Parser  Insights   Invoice     Future Tools
   Tool      Tool     Collection    (Milestone 2+)
                        Tool
        ↓
[Structured Response + Actionable Insights]
```

**Key Innovation**: The ADK agent doesn't just parse data—it understands context, chains multiple tools intelligently, and provides conversational responses that SME owners can act on immediately.

## 🏆 Track Selection

**Enterprise Agents Track**

FinGuard IntelliAgent aligns with the Enterprise Agents track because:

- **Complex Multi-Step Workflows**: Coordinates SMS parsing → data normalization → insight generation → automated actions
- **Tool Integration**: Demonstrates sophisticated tool chaining and context management
- **Production-Ready Focus**: Built for real-world SME deployment with error handling and scalability
- **Business Value**: Directly addresses enterprise-level financial automation challenges

## 📁 Repository Structure

```
FinGuardIntelliAgent/
│
├── backend/                    # FastAPI application backend
│   ├── routers/               # API endpoint routers
│   ├── models/                # Pydantic data models
│   ├── services/              # Business logic services
│   ├── utils/                 # Helper utilities
│   └── app.py                 # Main FastAPI application
│
├── agent/                     # ADK agent core
│   ├── planning/              # Agent planning strategies
│   └── orchestrator.py        # Main agent orchestration logic
│
├── tools/                     # ADK tool implementations
│   ├── sms_parser_tool.py     # SMS transaction parser
│   ├── insights_tool.py       # Financial insights generator
│   └── invoice_collection_tool.py  # Invoice tracking & follow-up
│
├── notebooks/                 # Jupyter notebooks for testing & analysis
│
├── data/                      # Data storage
│   ├── synthetic/            # Generated test data
│   └── sample_inputs/        # Sample SMS messages & invoices
│
├── docs/                      # Documentation
│
├── requirements.txt           # Python dependencies
├── .gitignore                # Git ignore patterns
├── LICENSE                   # MIT License
└── README.md                 # This file
```

## 🚀 Getting Started (Milestone 1)

### Prerequisites

- Python 3.10+
- Virtual environment (recommended)
- Anthropic API key (for ADK agent)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/21407alfredmunga/FinGuardIntelliAgent.git
   cd FinGuardIntelliAgent
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Anthropic API key
   ```

5. **Verify installation**
   ```bash
   python backend/app.py
   ```

### Milestone 1 Scope

✅ **Completed in Milestone 1:**
- Repository structure and scaffolding
- Starter code for backend, agent, and tools
- Documentation and setup instructions
- License and contribution guidelines

❌ **Not Included (Future Milestones):**
- Full ADK agent implementation
- Production database integration
- Frontend UI
- Deployment configurations
- Advanced tool features

## 📋 Next Steps for Milestone 2

### Planned Features

1. **Full ADK Agent Implementation**
   - Complete orchestrator with Claude Sonnet 3.5 integration
   - Multi-turn conversation handling
   - Context management across tool calls

2. **Enhanced SMS Parser Tool**
   - Support for 10+ M-Pesa/Airtel Money message formats
   - Fuzzy matching for merchant names
   - Multi-language support (English/Swahili)

3. **Production Database**
   - PostgreSQL integration for transaction storage
   - SQLAlchemy ORM models
   - Migration scripts

4. **API Endpoints**
   - RESTful API for transaction ingestion
   - Webhook receivers for SMS forwarding services
   - Authentication & authorization

5. **Testing Suite**
   - Unit tests for all tools
   - Integration tests for agent workflows
   - Synthetic data generation scripts

6. **Basic Frontend**
   - Dashboard for transaction visualization
   - SMS upload interface
   - Insights display

## 🤝 Contributing

This is a capstone project, but feedback and suggestions are welcome! Please open an issue to discuss proposed changes.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Alfred Munga**  
GitHub: [@21407alfredmunga](https://github.com/21407alfredmunga)

---

**Built with ❤️ for Kenyan SMEs | Powered by Anthropic ADK**

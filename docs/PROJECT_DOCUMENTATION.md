# FinGuard IntelliAgent - Project Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Component Guide](#component-guide)
4. [Development Roadmap](#development-roadmap)
5. [API Documentation](#api-documentation)

## Introduction

FinGuard IntelliAgent is an AI-powered financial automation system built specifically for Kenyan Small and Medium Enterprises (SMEs). The system leverages Anthropic's Agent Development Kit (ADK) to provide intelligent financial management capabilities.

### Key Features

- **SMS Transaction Parsing**: Automatically extracts structured data from M-Pesa and Airtel Money SMS messages
- **Financial Insights**: Generates actionable insights from transaction data
- **Invoice Collection**: Automates invoice tracking and follow-up processes
- **Natural Language Interface**: Interact with the system through conversational queries

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                          │
│                  (Web/Mobile/SMS/API)                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                           │
│                   (backend/app.py)                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                ADK Agent Orchestrator                       │
│              (agent/orchestrator.py)                        │
└───┬───────────────────┬─────────────────┬───────────────────┘
    │                   │                 │
    ▼                   ▼                 ▼
┌─────────┐      ┌─────────────┐   ┌──────────────────┐
│   SMS   │      │  Insights   │   │     Invoice      │
│ Parser  │      │    Tool     │   │  Collection Tool │
│  Tool   │      │             │   │                  │
└─────────┘      └─────────────┘   └──────────────────┘
```

### Technology Stack

**Backend:**
- FastAPI: Modern Python web framework
- Uvicorn: ASGI server
- Pydantic: Data validation

**AI/Agent:**
- Anthropic ADK: Agent orchestration
- Claude Sonnet 3.5: LLM reasoning

**Data Processing:**
- Pandas: Data manipulation
- Regex: Pattern matching

**Future:**
- PostgreSQL: Data persistence
- Redis: Caching
- Celery: Background tasks

## Component Guide

### Backend (`backend/`)

The backend provides RESTful API endpoints for the application.

**Key Files:**
- `app.py`: Main FastAPI application
- `routers/`: API route handlers (Milestone 2+)
- `models/`: Pydantic data models (Milestone 2+)
- `services/`: Business logic (Milestone 2+)
- `utils/`: Helper functions (Milestone 2+)

### Agent (`agent/`)

The agent module contains the ADK orchestration logic.

**Key Files:**
- `orchestrator.py`: Main agent orchestrator
- `planning/`: Agent planning strategies (Milestone 2+)

### Tools (`tools/`)

Individual ADK tools that the agent can use.

**Key Files:**
- `sms_parser_tool.py`: SMS transaction parser
- `insights_tool.py`: Financial insights generator
- `invoice_collection_tool.py`: Invoice tracking and collection

## Development Roadmap

### Milestone 1 (Current) ✅
- Repository structure and scaffolding
- Placeholder implementations
- Documentation and setup instructions

### Milestone 2 (Planned)
- Full ADK agent implementation
- Complete tool implementations
- Database integration
- API endpoints
- Testing suite

### Milestone 3 (Future)
- Frontend UI
- Real-time SMS integration
- M-Pesa API integration
- Advanced analytics
- Multi-user support

### Milestone 4 (Future)
- Mobile app
- WhatsApp bot integration
- Predictive analytics
- Automated reporting
- Enterprise features

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-18T10:30:00Z",
  "version": "0.1.0 (Milestone 1)",
  "message": "FinGuard IntelliAgent API is running"
}
```

#### Root
```http
GET /
```

**Response:**
```json
{
  "message": "Welcome to FinGuard IntelliAgent API",
  "version": "0.1.0 (Milestone 1)",
  "documentation": "/docs",
  "health_check": "/health"
}
```

### Future Endpoints (Milestone 2+)

These endpoints are planned but not yet implemented:

- `POST /api/v1/transactions/parse` - Parse SMS transactions
- `GET /api/v1/insights` - Get financial insights
- `GET /api/v1/invoices` - Get invoice status
- `POST /api/v1/agent/query` - Query the ADK agent

## Development Setup

See the main [README.md](../README.md) for detailed setup instructions.

## Contributing

This is a capstone project. For feedback or suggestions, please open an issue on GitHub.

## License

MIT License - See [LICENSE](../LICENSE) for details.

---

**Last Updated:** November 18, 2025  
**Version:** 0.1.0 (Milestone 1)

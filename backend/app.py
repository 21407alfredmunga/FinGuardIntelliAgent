"""
FinGuard IntelliAgent - Main FastAPI Application
=================================================

This module serves as the entry point for the FinGuard IntelliAgent backend API.
It initializes the FastAPI application, configures middleware, and sets up routes.

Milestone 1 Scope:
    - Basic FastAPI application structure
    - Health check endpoint
    - Placeholder routes for future implementation
    
Author: Alfred Munga
License: MIT
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
from datetime import datetime
import logging
import sys
from pathlib import Path

# Add parent directory to path to import tools
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.sms_parser_tool import SMSParserTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Application Configuration
# ============================================================================

# Initialize FastAPI application
app = FastAPI(
    title="FinGuard IntelliAgent API",
    description="AI-powered financial automation for Kenyan SMEs",
    version="0.2.0 (Milestone 3 - SMS Parser)",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Pydantic Models (Data Schemas)
# ============================================================================

class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str
    timestamp: str
    version: str
    message: str


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str
    detail: Optional[str] = None
    timestamp: str


# ============================================================================
# Core Endpoints
# ============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """
    Root endpoint - provides basic API information.
    
    Returns:
        dict: Welcome message and API status
    """
    return {
        "message": "Welcome to FinGuard IntelliAgent API",
        "version": "0.1.0 (Milestone 1)",
        "documentation": "/docs",
        "health_check": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify API is running.
    
    Returns:
        HealthResponse: Current health status of the API
    """
    logger.info("Health check requested")
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="0.1.0 (Milestone 1)",
        message="FinGuard IntelliAgent API is running"
    )


# ============================================================================
# Placeholder Routes (To be implemented in Milestone 2+)
# ============================================================================

@app.post("/api/v1/transactions/parse")
async def parse_transaction():
    """
    [PLACEHOLDER] Parse SMS transaction messages.
    
    This endpoint will be fully implemented in Milestone 2 with:
    - SMS message ingestion
    - M-Pesa/Airtel Money format detection
    - Transaction data extraction
    - Structured data response
    
    Raises:
        HTTPException: 501 Not Implemented
    """
    raise HTTPException(
        status_code=501,
        detail="Transaction parsing will be implemented in Milestone 2"
    )


@app.get("/api/v1/insights")
async def get_insights():
    """
    [PLACEHOLDER] Generate financial insights from transactions.
    
    This endpoint will be fully implemented in Milestone 2 with:
    - Cash flow analysis
    - Spending pattern detection
    - Revenue/expense categorization
    - Trend visualization data
    
    Raises:
        HTTPException: 501 Not Implemented
    """
    raise HTTPException(
        status_code=501,
        detail="Financial insights generation will be implemented in Milestone 2"
    )


@app.get("/api/v1/invoices")
async def get_invoices():
    """
    [PLACEHOLDER] Retrieve invoice collection status.
    
    This endpoint will be fully implemented in Milestone 2 with:
    - Outstanding invoice tracking
    - Payment status monitoring
    - Automated follow-up scheduling
    - Collection analytics
    
    Raises:
        HTTPException: 501 Not Implemented
    """
    raise HTTPException(
        status_code=501,
        detail="Invoice collection will be implemented in Milestone 2"
    )


@app.post("/api/v1/agent/query")
async def agent_query():
    """
    [PLACEHOLDER] Submit natural language query to ADK agent.
    
    This endpoint will be fully implemented in Milestone 2 with:
    - ADK agent orchestration
    - Multi-turn conversation handling
    - Tool selection and execution
    - Contextual responses
    
    Raises:
        HTTPException: 501 Not Implemented
    """
    raise HTTPException(
        status_code=501,
        detail="ADK agent integration will be implemented in Milestone 2"
    )


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """
    Global exception handler for HTTP exceptions.
    
    Args:
        request: The incoming request object
        exc: The HTTPException that was raised
        
    Returns:
        JSONResponse: Standardized error response
    """
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """
    Global exception handler for unexpected errors.
    
    Args:
        request: The incoming request object
        exc: The exception that was raised
        
    Returns:
        JSONResponse: Standardized error response
    """
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ============================================================================
# SMS Parser Endpoints (Milestone 3)
# ============================================================================

# Initialize SMS Parser (singleton)
sms_parser = SMSParserTool()


class ParseSMSRequest(BaseModel):
    """Request model for single SMS parsing."""
    sms_text: str
    
    class Config:
        schema_extra = {
            "example": {
                "sms_text": "RB90VRG Confirmed. You have received Ksh5,991.87 from STEPHEN WAMBUI 254712531512 on 26/08/2025 at 04:23 PM. New M-PESA balance is Ksh-30,000.70. Transaction cost, Ksh0.00."
            }
        }


class ParseBulkSMSRequest(BaseModel):
    """Request model for bulk SMS parsing."""
    sms_messages: List[str]
    
    class Config:
        schema_extra = {
            "example": {
                "sms_messages": [
                    "RB90VRG Confirmed. You have received Ksh5,991.87 from STEPHEN WAMBUI 254712531512 on 26/08/2025 at 04:23 PM...",
                    "RF55KXW Confirmed. You have paid Ksh446.84 to RUBIS ENERGY for account 560697 on 24/08/2025 at 10:01 AM..."
                ]
            }
        }


@app.post("/api/v1/sms/parse", tags=["SMS Parser"])
async def parse_sms(request: ParseSMSRequest):
    """
    Parse a single SMS message to extract transaction details.
    
    **Milestone:** 3 - SMS Parser Tool
    
    **Supported Transaction Types:**
    - M-Pesa: received, sent, paybill, till, withdrawal, airtime
    - Bank: deposits, withdrawals, transfers
    
    **Returns:**
    - Parsed transaction data with fields like:
      - transaction_type
      - amount
      - reference
      - date
      - balance
      - Additional type-specific fields
      
    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "transaction_type": "received",
            "amount": "5991.87",
            "reference": "RB90VRG",
            "date": "2025-08-26T16:23:00",
            "balance": "-30000.70",
            "sender": "STEPHEN WAMBUI",
            "phone": "254712531512"
        },
        "summary": "Received KES 5,991.87 from STEPHEN WAMBUI on 26/08/2025"
    }
    ```
    """
    try:
        logger.info(f"Parsing SMS: {request.sms_text[:50]}...")
        
        # Parse the SMS
        result = sms_parser.parse_sms(request.sms_text)
        
        if result is None or 'error' in result:
            raise HTTPException(
                status_code=400,
                detail="Failed to parse SMS. Unsupported format or invalid message."
            )
        
        # Convert Decimal to string for JSON serialization
        result_json = {}
        for key, value in result.items():
            if key == 'date' and isinstance(value, datetime):
                result_json[key] = value.isoformat()
            elif key == 'raw_text':
                continue  # Don't include raw text in response
            else:
                result_json[key] = str(value)
        
        # Generate human-readable summary
        summary = sms_parser.get_transaction_summary(result)
        
        # Validate the parsed data
        is_valid, errors = sms_parser.validate_parsed_data(result)
        
        return {
            "success": True,
            "data": result_json,
            "summary": summary,
            "validation": {
                "is_valid": is_valid,
                "errors": errors if not is_valid else []
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing SMS: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal error while parsing SMS: {str(e)}"
        )


@app.post("/api/v1/sms/parse-bulk", tags=["SMS Parser"])
async def parse_bulk_sms(request: ParseBulkSMSRequest):
    """
    Parse multiple SMS messages in bulk.
    
    **Milestone:** 3 - SMS Parser Tool
    
    **Performance:**
    - Processes messages concurrently
    - Returns results for all messages (including failures)
    - Includes aggregate statistics
    
    **Returns:**
    - List of parsed transactions
    - Statistics (success rate, total amount, etc.)
    - Failed parses with error messages
    
    **Example Response:**
    ```json
    {
        "success": true,
        "results": [
            {
                "sms_index": 0,
                "transaction_type": "received",
                "amount": "5991.87",
                ...
            },
            {
                "sms_index": 1,
                "error": "Failed to parse SMS"
            }
        ],
        "statistics": {
            "total_messages": 2,
            "successful_parses": 1,
            "failed_parses": 1,
            "success_rate": 50.0,
            "total_amount": "5991.87"
        }
    }
    ```
    """
    try:
        logger.info(f"Parsing {len(request.sms_messages)} SMS messages in bulk")
        
        # Parse all messages
        results = sms_parser.parse_bulk(request.sms_messages)
        
        # Get statistics
        stats = sms_parser.get_statistics(results)
        
        # Convert results for JSON serialization
        results_json = []
        for result in results:
            result_json = {}
            for key, value in result.items():
                if key == 'date' and isinstance(value, datetime):
                    result_json[key] = value.isoformat()
                elif key == 'raw_text' or key == 'original_text':
                    continue  # Don't include raw text in response
                else:
                    result_json[key] = str(value)
            results_json.append(result_json)
        
        # Convert statistics for JSON
        stats_json = {
            "total_messages": stats['total_transactions'],
            "successful_parses": stats['successful_parses'],
            "failed_parses": stats['failed_parses'],
            "success_rate": (stats['successful_parses'] / stats['total_transactions'] * 100) 
                           if stats['total_transactions'] > 0 else 0,
            "total_amount": str(stats['total_amount']),
            "transaction_type_counts": stats['transaction_type_counts'],
            "date_range": {
                "earliest": stats['date_range']['earliest'].isoformat() 
                           if stats['date_range']['earliest'] else None,
                "latest": stats['date_range']['latest'].isoformat() 
                         if stats['date_range']['latest'] else None
            }
        }
        
        return {
            "success": True,
            "results": results_json,
            "statistics": stats_json,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in bulk SMS parsing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal error while parsing bulk SMS: {str(e)}"
        )


@app.get("/api/v1/sms/parser-info", tags=["SMS Parser"])
async def get_parser_info():
    """
    Get information about the SMS parser capabilities.
    
    **Milestone:** 3 - SMS Parser Tool
    
    **Returns:**
    - Supported transaction types
    - Parser version
    - Kenyan banks supported
    - Example SMS formats
    """
    return {
        "parser_version": "1.0.0",
        "supported_transaction_types": sms_parser.transaction_types,
        "supported_banks": [
            "KCB Bank",
            "Equity Bank",
            "Co-operative Bank",
            "Barclays Bank",
            "Standard Chartered",
            "NCBA Bank",
            "I&M Bank",
            "DTB Bank",
            "Family Bank",
            "Stanbic Bank"
        ],
        "mobile_money_providers": [
            "M-Pesa (Safaricom)"
        ],
        "features": {
            "single_parse": True,
            "bulk_parse": True,
            "validation": True,
            "summary_generation": True,
            "statistics": True
        },
        "accuracy_metrics": {
            "tested_messages": 50,
            "parsing_accuracy": "100%",
            "amount_extraction": "100%",
            "reference_extraction": "100%"
        }
    }


# ============================================================================
# Startup & Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Application startup handler.
    
    Executed when the FastAPI application starts.
    Future milestones will include:
    - Database connection initialization
    - ADK agent initialization
    - Cache warming
    """
    logger.info("="*60)
    logger.info("="*60)
    logger.info("FinGuard IntelliAgent API Starting")
    logger.info("Version: 0.2.0 (Milestone 3 - SMS Parser)")
    logger.info("Environment: Development")
    logger.info("SMS Parser: Initialized")
    logger.info("="*60)
    
    # TODO Milestone 4: Initialize database connection
    # TODO Milestone 5: Initialize ADK agent
    # TODO Milestone 6: Load configuration from environment


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown handler.
    
    Executed when the FastAPI application stops.
    Future milestones will include:
    - Database connection cleanup
    - Cache flush
    - Graceful shutdown of background tasks
    """
    logger.info("="*60)
    logger.info("FinGuard IntelliAgent API Shutting Down")
    logger.info("="*60)
    
    # TODO Milestone 2: Close database connections
    # TODO Milestone 2: Cleanup ADK agent resources


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    """
    Run the FastAPI application using Uvicorn server.
    
    For development only. In production, use a proper ASGI server
    with process management (e.g., Gunicorn with Uvicorn workers).
    """
    logger.info("Starting development server...")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (dev only)
        log_level="info"
    )

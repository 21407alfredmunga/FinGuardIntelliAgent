"""
FinGuard IntelliAgent - Backend Services
========================================

This module contains backend services for the FinGuard IntelliAgent system.

Services:
    - LLM Service: Google Gemini integration for RAG
    
Author: Alfred Munga
License: MIT
"""

from .llm_service import LLMService, generate_response

__all__ = ['LLMService', 'generate_response']

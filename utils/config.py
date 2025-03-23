"""
Configuration utilities for the Big Red Button agent system.
"""
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
AI21_API_KEY = os.environ.get("AI21_API_KEY")

# Agent configuration
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.1

# System configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
DEBUG_MODE = os.environ.get("DEBUG_MODE", "False").lower() == "true"

# Web UI configuration
WEB_HOST = os.environ.get("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.environ.get("WEB_PORT", "8000"))

# Scanning configuration
MAX_SCAN_DEPTH = int(os.environ.get("MAX_SCAN_DEPTH", "3"))
SCAN_TIMEOUT = int(os.environ.get("SCAN_TIMEOUT", "300"))  # seconds

# Security settings
SAFE_MODE = os.environ.get("SAFE_MODE", "True").lower() == "true"
EXPLOITATION_ENABLED = os.environ.get("EXPLOITATION_ENABLED", "False").lower() == "true"

def get_agent_config(agent_type: str) -> Dict[str, Any]:
    """
    Get configuration for a specific agent type.
    
    Args:
        agent_type: Type of agent (orchestration, web_security, api_testing, etc.)
        
    Returns:
        Dictionary containing agent configuration
    """
    base_config = {
        "model": DEFAULT_MODEL,
        "temperature": DEFAULT_TEMPERATURE,
    }
    
    # Agent-specific configurations
    agent_configs = {
        "orchestration": {
            "model": "gpt-4o",
            "temperature": 0.1,
            "max_tokens": 4096,
        },
        "web_security": {
            "model": "gpt-4o",
            "temperature": 0.2,
            "max_tokens": 2048,
        },
        "api_testing": {
            "model": "gpt-4o",
            "temperature": 0.2,
            "max_tokens": 2048,
        },
        "llm_vulnerability": {
            "model": "gpt-4o",
            "temperature": 0.3,
            "max_tokens": 2048,
        },
        "reporting": {
            "model": "gpt-4o",
            "temperature": 0.1,
            "max_tokens": 4096,
        }
    }
    
    # Merge base config with agent-specific config
    if agent_type in agent_configs:
        base_config.update(agent_configs[agent_type])
    
    return base_config

def validate_config() -> Optional[str]:
    """
    Validate the configuration and return an error message if invalid.
    
    Returns:
        Error message if configuration is invalid, None otherwise
    """
    if not OPENAI_API_KEY:
        return "OPENAI_API_KEY is not set in the environment variables"
    
    # Add more validation as needed
    
    return None

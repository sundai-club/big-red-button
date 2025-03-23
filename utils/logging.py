"""
Logging utilities for the Big Red Button agent system.
"""
import logging
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile
import platform

from utils.config import LOG_LEVEL, DEBUG_MODE

def get_log_directory() -> Path:
    """
    Get the appropriate log directory based on the platform.
    
    Returns:
        Path object representing the log directory
    """
    if platform.system() == "Windows":
        base_dir = os.environ.get("APPDATA", os.path.expanduser("~"))
    elif platform.system() == "Darwin":  # macOS
        base_dir = os.path.expanduser("~/Library/Logs")
    else:  # Linux and other Unix-like systems
        base_dir = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    
    log_dir = Path(base_dir) / "big-red-button" / "logs"
    
    # Create the directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    return log_dir

def get_temp_log_directory() -> Path:
    """
    Get a temporary log directory that's guaranteed to be writable.
    
    Returns:
        Path object representing the temporary log directory
    """
    temp_dir = Path(tempfile.gettempdir()) / "big-red-button" / "logs"
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

# Determine the log directory
try:
    LOG_DIR = get_log_directory()
except (IOError, PermissionError):
    # Fall back to a temporary directory if we can't create the standard log directory
    LOG_DIR = get_temp_log_directory()
    print(f"Warning: Using temporary log directory: {LOG_DIR}")

# Create structured and findings subdirectories
STRUCTURED_LOG_DIR = LOG_DIR / "structured"
FINDINGS_LOG_DIR = LOG_DIR / "findings"
os.makedirs(STRUCTURED_LOG_DIR, exist_ok=True)
os.makedirs(FINDINGS_LOG_DIR, exist_ok=True)

# Configure logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_file = LOG_DIR / f"big_red_button_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Create handlers
console_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler(log_file)

# Set formatter for both handlers
formatter = logging.Formatter(log_format)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(getattr(logging, LOG_LEVEL))
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

# Create logger
logger = logging.getLogger("big_red_button")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    
    Args:
        name: Name of the logger
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"big_red_button.{name}")

class AgentLogger:
    """
    Logger for agent activities with structured logging capabilities.
    """
    def __init__(self, agent_name: str):
        self.logger = get_logger(f"agent.{agent_name}")
        self.agent_name = agent_name
        
    def log_agent_action(self, action: str, details: Dict[str, Any], level: str = "INFO") -> None:
        """
        Log an agent action with structured details.
        
        Args:
            action: The action being performed
            details: Dictionary of action details
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        log_data = {
            "agent": self.agent_name,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        
        log_method = getattr(self.logger, level.lower())
        log_method(f"{action}: {json.dumps(log_data)}")
        
        # Also save to a structured log file for the UI to read
        self._save_structured_log(log_data)
    
    def _save_structured_log(self, log_data: Dict[str, Any]) -> None:
        """
        Save structured log data to a JSON file for the UI to read.
        
        Args:
            log_data: Log data to save
        """
        # Append to the agent's log file
        log_file = STRUCTURED_LOG_DIR / f"{self.agent_name}.jsonl"
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except (IOError, PermissionError) as e:
            self.logger.error(f"Failed to write structured log: {e}")
            
    def log_finding(self, finding_type: str, severity: str, details: Dict[str, Any]) -> None:
        """
        Log a security or bug finding.
        
        Args:
            finding_type: Type of finding (XSS, SQLi, API_ERROR, etc.)
            severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL)
            details: Dictionary of finding details
        """
        log_data = {
            "agent": self.agent_name,
            "finding_type": finding_type,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        
        self.logger.warning(f"FINDING: {finding_type} ({severity}): {json.dumps(details)}")
        
        # Generate a unique ID for the finding
        finding_id = f"{finding_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save as individual finding file
        try:
            finding_file = FINDINGS_LOG_DIR / f"{finding_id}.json"
            with open(finding_file, "w") as f:
                json.dump(log_data, f, indent=2)
        except (IOError, PermissionError) as e:
            self.logger.error(f"Failed to write finding log: {e}")

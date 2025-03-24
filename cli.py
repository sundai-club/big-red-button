#!/usr/bin/env python3
"""
Big Red Button - CLI Tool

This module implements a command-line interface for scanning websites for security issues
using the orchestration agent.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from agents import (
    Agent,
    Model,
    ModelProvider,
    OpenAIChatCompletionsModel,
    RunConfig,
    Runner,
    set_tracing_disabled,
)
from openai import AsyncOpenAI

from app.orhcestration import orchestration_agent
from utils.logging import get_logger, AgentLogger

logger = get_logger("cli")
orch_logger = AgentLogger("orchestration")

API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4")

if not API_KEY:
    logger.error("OPENAI_API_KEY environment variable must be set")
    sys.exit(1)


async def scan_website(url: str, depth: Optional[int] = None, timeout: Optional[int] = None):
    logger.info(f"Starting scan for {url}")
    orch_logger.log_agent_action("scan_started", {"url": url})
    
    set_tracing_disabled(os.getenv("DISABLE_TRACING", "false").lower() == "true")
    
    scan_params = {
        "url": url,
    }
    if depth is not None:
        scan_params["depth"] = depth
    if timeout is not None:
        scan_params["timeout"] = timeout
        
    try:
        result = await Runner.run(
            orchestration_agent,
            f"Scan the website {url} for security vulnerabilities"
        )
        
        print("\n=== Scan Results ===")
        print(result.final_output)
        
        logger.info(f"Completed scan for {url}")
        orch_logger.log_agent_action("scan_completed", {"url": url})
        
        return result.final_output
    except Exception as e:
        logger.error(f"Scan failed: {str(e)}")
        orch_logger.log_agent_action("scan_failed", {"url": url, "error": str(e)})
        print(f"Error: {str(e)}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Big Red Button CLI - Website Security Scanner")
    parser.add_argument("url", help="URL of the website to scan")
    parser.add_argument("--depth", type=int, help="Maximum crawl depth")
    parser.add_argument("--timeout", type=int, help="Maximum scan timeout in seconds")
    
    args = parser.parse_args()
    
    asyncio.run(scan_website(args.url, args.depth, args.timeout))


if __name__ == "__main__":
    main()

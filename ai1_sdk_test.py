#!/usr/bin/env python3

from __future__ import annotations

import asyncio

from agents import (
    Runner,
)

from app.ai21 import ai21_system_prompt_hack
from utils.logging import get_logger, AgentLogger

logger = get_logger("ai21")
orch_logger = AgentLogger("orchestration")

async def ai21_testing():
    try:
        await Runner.run(ai21_system_prompt_hack, "Run the AI21 agent")
        print("\n=== AI21 Results ===")
        print(result.final_output)
        return result.final_output
    except Exception as e:
        logger.error(f"AI21 agent failed: {str(e)}")
        orch_logger.log_agent_action("ai21_failed", {"error": str(e)})
        print(f"Error: {str(e)}")
        return None
    

def main():
    asyncio.run(ai21_testing())


if __name__ == "__main__":
    main()

from agents import Agent
from app.security import web_security_agent

orchestration_agent = Agent(
    name="Orchestration agent",
    instructions="You are the orchestrator of the Big Red Button agent system. You are responsible for coordinating all other agents in the system.",    
    handoffs=[web_security_agent]
)
from agents import Agent
from app.security import web_security_agent

orchestration_agent = Agent(
    name="Orchestration agent",
    instructions="""
    You are the orchestrator of the Big Red Button agent system. 
        You are responsible for coordinating all other agents in the system.
        Whenever you are given a web URL you should:
            1. Determine the appropriate agent to handle the task
            2. Handoff the task to the appropriate agent
            3. Monitor the progress of the task
            4. Coordinate the results from the task
    """,    
    model="gpt-4o-mini",
    handoffs=[web_security_agent]
)
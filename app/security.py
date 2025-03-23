from agents import Agent, WebSearchTool


web_security_agent = Agent(
    name="Web Security agent",
    instructions="You are the Web Security agent of the Big Red Button agent system. You are responsible for detecting web security vulnerabilities in target websites.",
    tools=[WebSearchTool()]
)
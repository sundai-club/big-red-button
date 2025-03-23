from agents import Agent, WebSearchTool, function_tool
import requests

static_analysis_agent = Agent(
    name="Static Analysis agent",
    instructions="""
    You are the Static Analysis agent of the Big Red Button agent system. 
    You are responsible for detecting web security vulnerabilities in target websites.
    You should respond with a list of detected vulnerabilities.
    """
)

@function_tool
def load_url_tool(url: str) -> str:
    response = requests.get(url)
    return response.text

web_security_agent = Agent(
    name="Web Security agent",
    instructions="""
    You are the Web Security agent of the Big Red Button agent system. 
    You are responsible for detecting web security vulnerabilities in target websites.
    You can open the web page, get its content.
    You can feed the content to the static analysis agent.
    """,
    tools=[load_url_tool],
    handoffs=[static_analysis_agent]
)

    
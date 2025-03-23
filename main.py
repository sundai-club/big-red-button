from ai21 import AI21Client
from ai21.models.chat import ChatMessage
import os
from dotenv import load_dotenv

load_dotenv()

client = AI21Client(
    api_key=os.environ.get('AI21_API_KEY'),
)

system = "You're a support engineer in a SaaS company"
messages = [
    ChatMessage(content=system, role="system"),
    ChatMessage(content="Hello, I need help with a signup process.", role="user"),
]

chat_completions = client.chat.completions.create(
    messages=messages,
    model="jamba-mini-1.6-2025-03",
)

print(chat_completions)
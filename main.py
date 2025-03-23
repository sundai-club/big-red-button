from ai21 import AI21Client
from ai21.models.chat import ChatMessage
import os
from dotenv import load_dotenv

load_dotenv()

client = AI21Client(
    api_key=os.environ.get('AI21_API_KEY'),
)

run_result = client.beta.maestro.runs.create_and_poll(
    input="Write a poem about the ocean",
    requirements=[
        {
            "name": "length requirement",
            "description": "The length of the poem should be less than 1000 characters",
        },
        {
            "name": "rhyme requirement",
            "description": "The poem should rhyme",
        },
    ],
)

print(run_result.result)
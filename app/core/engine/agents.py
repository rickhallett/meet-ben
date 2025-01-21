from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from openai import AsyncOpenAI, OpenAI
import os
from dataclasses import dataclass

load_dotenv()


model = OpenAIModel(
    model_name=os.getenv("LLM_MODEL", "openai/gpt-4o-mini"),
    api_key=os.getenv("OPEN_ROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


@dataclass
class AgentDeps():
    openai_client: OpenAI

# response = openai_client.chat.completions.create(
#     model=llm,
#     messages=[{"role": "user", "content": "Hello, world!"}],
# )

# print(response.choices[0].message.content)

orchestration_agent = Agent(
    model=model,
    name="orchestration_agent",
    system_prompt="You are an agent that orchestrates the execution of other agents.",
    deps_type=AgentDeps,
    tools=[],
    retries=2
)

@orchestration_agent.tool
def pass_to_agent(agent_name: str, message: str):
    pass

request = "Hello, world!"

response = orchestration_agent.run(request)

print(response)


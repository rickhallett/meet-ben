# Multi-agent Applications

There are roughly four levels of complexity when building applications with PydanticAI:

1. **Single agent workflows** — what most of the `pydantic_ai` documentation covers
2. **[Agent delegation](#agent-delegation)** — agents using another agent via tools
3. **[Programmatic agent hand-off](#programmatic-agent-hand-off)** — one agent runs, then application code calls another agent
4. **[Graph based control flow](../graph/)** — for the most complex cases, a graph-based state machine can be used to control the execution of multiple agents

Of course, you can combine multiple strategies in a single application.

## Agent delegation

"Agent delegation" refers to the scenario where an agent delegates work to another agent, then takes back control when the delegate agent finishes. Since agents are stateless and designed to be global, you do not need to include the agent itself in agent [dependencies](../dependencies/).

You'll generally want to pass **`ctx.usage`** to the **`usage`** keyword argument of the delegate agent run so usage within that run counts towards the total usage of the parent agent run.

> **Note:** Agent delegation doesn't need to use the same model for each agent. If you choose to use different models within a run, calculating the monetary cost from the final [`result.usage()`](../api/result/#pydantic_ai.result.RunResult.usage) of the run will not be possible, but you can still use [`UsageLimits`](../api/usage/#pydantic_ai.usage.UsageLimits) to avoid unexpected costs.

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai.usage import UsageLimits

joke_selection_agent = Agent(  # "Parent" or controlling agent.
    'openai:gpt-4o',
    system_prompt=(
        'Use the `joke_factory` to generate some jokes, then choose the best. '
        'You must return just a single joke.'
    ),
)
joke_generation_agent = Agent('gemini-1.5-flash', result_type=list[str])  # "Delegate" agent

@joke_selection_agent.tool
async def joke_factory(ctx: RunContext[None], count: int) -> list[str]:
    r = await joke_generation_agent.run(  # Call the delegate agent from within a tool
        f'Please generate {count} jokes.',
        usage=ctx.usage,  # Pass the usage from the parent agent to the delegate agent
    )
    return r.data  # Return r.data, as function returns list[str], and result_type is also list[str]

result = joke_selection_agent.run_sync(
    'Tell me a joke.',
    usage_limits=UsageLimits(request_limit=5, total_tokens_limit=300),
)
print(result.data)
# Output: Did you hear about the toothpaste scandal? They called it Colgate.
print(result.usage())
# Output:
# Usage(
#    requests=3, request_tokens=204, response_tokens=24, total_tokens=228, details=None
# )
```

### Agent delegation and dependencies

Generally, the delegate agent needs to either have the same [dependencies](../dependencies/) as the calling agent or dependencies which are a subset of the calling agent’s dependencies.

```python
from dataclasses import dataclass
import httpx
from pydantic_ai import Agent, RunContext

@dataclass
class ClientAndKey:  # Dataclass to hold client and API key dependencies.
    http_client: httpx.AsyncClient
    api_key: str

joke_selection_agent = Agent(
    'openai:gpt-4o',
    deps_type=ClientAndKey,  # Set deps_type of calling agent
    system_prompt=(
        'Use the `joke_factory` tool to generate some jokes..'
    ),
)
joke_generation_agent = Agent(
    'gemini-1.5-flash',
    deps_type=ClientAndKey,  # Also set deps_type of the delegate agent
    result_type=list[str],
    system_prompt=(
        'Use the "get_jokes" tool to get some jokes..'
    ),
)

@joke_selection_agent.tool
async def joke_factory(ctx: RunContext[ClientAndKey], count: int) -> list[str]:
    r = await joke_generation_agent.run(
        f'Please generate {count} jokes.',
        deps=ctx.deps,  # Pass dependencies to delegate agent's run
        usage=ctx.usage,
    )
    return r.data

@joke_generation_agent.tool  # Define a tool on the delegate agent that uses dependencies
async def get_jokes(ctx: RunContext[ClientAndKey], count: int) -> str:
    response = await ctx.deps.http_client.get(
        'https://example.com',
        params={'count': count},
        headers={'Authorization': f'Bearer {ctx.deps.api_key}'},
    )
    response.raise_for_status()
    return response.text

async def main():
    async with httpx.AsyncClient() as client:
        deps = ClientAndKey(client, 'foobar')
        result = await joke_selection_agent.run('Tell me a joke.', deps=deps)
        print(result.data)
        print(result.usage())  # Usage includes requests from both agents

# Add asyncio.run(main()) to run main
```

## Programmatic agent hand-off

"Programmatic agent hand-off" refers to the scenario where multiple agents are called in succession, with application code and/or a human in the loop responsible for deciding which agent to call next. Here agents don’t need to use the same deps.

```python
from typing import Literal, Union
from pydantic import BaseModel, Field
from rich.prompt import Prompt
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage
from pydantic_ai.usage import Usage, UsageLimits

class FlightDetails(BaseModel):
    flight_number: str

class Failed(BaseModel):  # Unable to find a satisfactory choice.
    """Unavailable."""

flight_search_agent = Agent[None, Union[FlightDetails, Failed]](  # Agent to find a flight
    'openai:gpt-4o',
    result_type=Union[FlightDetails, Failed],  # Use a union to convey failure
    system_prompt=(
        'Use the "flight_search" tool to find a flight ..'
    ),
)

@flight_search_agent.tool  # Define a tool to find a flight
async def flight_search(ctx: RunContext[None], origin: str, destination: str) -> Union[FlightDetails, None]:
    return FlightDetails(flight_number='AK456')

usage_limits = UsageLimits(request_limit=15)  # Define usage limits

async def find_flight(usage: Usage) -> Union[FlightDetails, None]:
    message_history: Union[list[ModelMessage], None] = None
    for _ in range(3):
        prompt = Prompt.ask('Where would you like to fly from and to?')
        result = await flight_search_agent.run(
            prompt,
            message_history=message_history,
            usage=usage,
            usage_limits=usage_limits,
        )
        if isinstance(result.data, FlightDetails):
            return result.data
        else:
            message_history = result.all_messages(result_tool_return_content='Please try again.')

class SeatPreference(BaseModel):
    row: int = Field(ge=1, le=30)
    seat: Literal['A', 'B', 'C', 'D', 'E', 'F']

seat_preference_agent = Agent[None, Union[SeatPreference, Failed]](  # Agent to extract seat selection
    'openai:gpt-4o',
    result_type=Union[SeatPreference, Failed],
    system_prompt=(
        "Extract user's seat preference.."
    ),
)

async def find_seat(usage: Usage) -> SeatPreference:
    while True:
        answer = Prompt.ask('What seat would you like?')
        result = await seat_preference_agent.run(
            answer,
            usage=usage,
            usage_limits=usage_limits,
        )
        if isinstance(result.data, SeatPreference):
            return result.data
        else:
            print('Could not understand seat preference. Please try again.')

async def main():  # Main app logic is simple
    usage: Usage = Usage()
    opt_flight_details = await find_flight(usage)
    if opt_flight_details:
        print(f'Flight found: {opt_flight_details.flight_number}')
        seat_preference = await find_seat(usage)
        print(f'Seat preference: {seat_preference}')

# Add asyncio.run(main()) to run main
```

## Pydantic Graphs

See the [graph](../graph/) documentation on when and how to use graphs.

## Examples

The following examples demonstrate how to use dependencies in PydanticAI:

- [Flight booking](../examples/flight-booking/)
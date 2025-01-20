# Agents Documentation

## Introduction

Agents are PydanticAI's primary interface for interacting with LLMs. In some use cases, a single Agent will control an entire application or component, but multiple agents can also interact to embody more complex workflows.

The [Agent](../api/agent/#pydantic_ai.agent.Agent) class has full API documentation, but conceptually you can think of an agent as a container for:

| **Component**                        | **Description**                                                                 |
|--------------------------------------|---------------------------------------------------------------------------------|
| [System prompt(s)](#system-prompts)  | A set of instructions for the LLM written by the developer.                     |
| [Function tool(s)](../tools/)        | Functions that the LLM may call to get information while generating a response. |
| [Structured result type](../results/) | The structured datatype the LLM must return at the end of a run, if specified.  |
| [Dependency type constraint](../dependencies/) | System prompt functions, tools, and result validators may all use dependencies when they're run. |
| [LLM model](../api/models/base/)     | Optional default LLM model associated with the agent. Can also be specified when running the agent. |
| [Model Settings](#additional-configuration) | Optional default model settings to help fine-tune requests. Can also be specified when running the agent. |

In typing terms, agents are generic in their dependency and result types. Here's a toy example of an agent that simulates a roulette wheel:

```python
from pydantic_ai import Agent, RunContext

roulette_agent = Agent(  # Create an agent, which expects an integer dependency and returns a boolean result.
    'openai:gpt-4o',
    deps_type=int,
    result_type=bool,
    system_prompt=(
        'Use the `roulette_wheel` function to see if the '
        'customer has won based on the number they provide.'
    ),
)


@roulette_agent.tool
async def roulette_wheel(ctx: RunContext[int], square: int) -> str:  # Define a tool that checks if the square is a winner.
    """check if the square is a winner"""
    return 'winner' if square == ctx.deps else 'loser'


# Run the agent
success_number = 18  # In reality, you might want to use a random number here e.g. random.randint(0, 36).
result = roulette_agent.run_sync('Put my money on square eighteen', deps=success_number)
print(result.data)  # > True

result = roulette_agent.run_sync('I bet five is the winner', deps=success_number)
print(result.data)
# > False
```

> **Tip:** Agents are designed for reuse, like FastAPI Apps.

## Running Agents

There are three ways to run an agent:

1. [`agent.run()`](../api/agent/#pydantic_ai.agent.Agent.run) — a coroutine which returns a [`RunResult`](../api/result/#pydantic_ai.result.RunResult) containing a completed response
2. [`agent.run_sync()`](../api/agent/#pydantic_ai.agent.Agent.run_sync) — a plain, synchronous function which returns a `RunResult` (internally, this just calls `loop.run_until_complete(self.run())`)
3. [`agent.run_stream()`](../api/agent/#pydantic_ai.agent.Agent.run_stream) — a coroutine which returns a [`StreamedRunResult`](../api/result/#pydantic_ai.result.StreamedRunResult), which contains methods to stream a response as an async iterable

Here's a simple example demonstrating all three:

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o')

result_sync = agent.run_sync('What is the capital of Italy?')
print(result_sync.data)
# > Rome

async def main():
    result = await agent.run('What is the capital of France?')
    print(result.data)
    # > Paris

    async with agent.run_stream('What is the capital of the UK?') as response:
        print(await response.get_data())
        # > London
```

(This example is complete, you would need to add `asyncio.run(main())` to run `main`.)

### Additional Configuration

#### Usage Limits

PydanticAI offers a [`UsageLimits`](../api/usage/#pydantic_ai.usage.UsageLimits) structure to help you limit your usage (tokens and/or requests) on model runs.

Example where we limit the number of response tokens:

```python
from pydantic_ai import Agent
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.usage import UsageLimits

agent = Agent('claude-3-5-sonnet-latest')

result_sync = agent.run_sync(
    'What is the capital of Italy? Answer with just the city.',
    usage_limits=UsageLimits(response_tokens_limit=10),
)
print(result_sync.data)
# > Rome

try:
    result_sync = agent.run_sync(
        'What is the capital of Italy? Answer with a paragraph.',
        usage_limits=UsageLimits(response_tokens_limit=10),
    )
except UsageLimitExceeded as e:
    print(e)
    # > Exceeded the response_tokens_limit of 10 (response_tokens=32)
```

Restricting requests to prevent infinite loops:

```python
from typing_extensions import TypedDict
from pydantic_ai import Agent, ModelRetry
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.usage import UsageLimits

class NeverResultType(TypedDict):
    never_use_this: str

agent = Agent(
    'claude-3-5-sonnet-latest',
    result_type=NeverResultType,
    system_prompt='Any time you get a response, call the `infinite_retry_tool` to produce another response.',
)

@agent.tool_plain(retries=5)
def infinite_retry_tool() -> int:
    raise ModelRetry('Please try again.')

try:
    result_sync = agent.run_sync(
        'Begin infinite retry loop!', usage_limits=UsageLimits(request_limit=3)
    )
except UsageLimitExceeded as e:
    print(e)
    # > The next request would exceed the request_limit of 3
```

> **Note:** This prevents the model from making excessive tool calls.

#### Model (Run) Settings

To fine-tune your requests, use [`settings.ModelSettings`](../api/settings/#pydantic_ai.settings.ModelSettings).

Example:

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o')

result_sync = agent.run_sync(
    'What is the capital of Italy?', model_settings={'temperature': 0.0}
)
print(result_sync.data)
# > Rome
```

## Runs vs. Conversations

A run might represent an entire conversation with multiple messages or be part of a larger conversation composed of multiple runs.

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o')

# First run
result1 = agent.run_sync('Who was Albert Einstein?')
print(result1.data)
# > Albert Einstein was a German-born theoretical physicist.

# Second run, passing previous messages
result2 = agent.run_sync(
    'What was his most famous equation?',
    message_history=result1.new_messages(),  # Continue the conversation
)
print(result2.data)
# > Albert Einstein's most famous equation is (E = mc^2).
```

## Type Safe by Design

PydanticAI is designed to work well with static type checkers like mypy and pyright. Agents are generic in both the type of their dependencies and the type of results they return.

Example with type mistakes:

```python
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

@dataclass
class User:
    name: str

agent = Agent(
    'test',
    deps_type=User,   # Expected User instance.
    result_type=bool,
)

@agent.system_prompt
def add_user_name(ctx: RunContext[str]) -> str:  # Mistake: expecting User, not str.
    return f"The user's name is {ctx.deps}"

def foobar(x: bytes) -> None:
    pass

result = agent.run_sync('Does their name start with "A"?', deps=User('Anne'))
foobar(result.data)  # Raises type error, expected bytes.
```

Running `mypy` will highlight the errors.

## System Prompts

Crafting the right system prompt is key to getting the model to behave as you want. Prompts can be static or dynamic, appended in order at runtime.

Example with both static and dynamic prompts:

```python
from datetime import date
from pydantic_ai import Agent, RunContext

agent = Agent(
    'openai:gpt-4o',
    deps_type=str,  # Expects string dependency.
    system_prompt="Use the customer's name while replying to them.",
)

@agent.system_prompt
def add_the_users_name(ctx: RunContext[str]) -> str:
    return f"The user's name is {ctx.deps}"

@agent.system_prompt
def add_the_date() -> str:
    return f'The date is {date.today()}.'

result = agent.run_sync('What is the date?', deps='Frank')
print(result.data)
# > Hello Frank, the date today is 2032-01-02.
```

## Reflection and Self-Correction

Validation errors from function tools or result validation can trigger retries by raising [`ModelRetry`](../api/exceptions/#pydantic_ai.exceptions.ModelRetry).

Example:

```python
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext, ModelRetry
from fake_database import DatabaseConn

class ChatResult(BaseModel):
    user_id: int
    message: str

agent = Agent(
    'openai:gpt-4o',
    deps_type=DatabaseConn,
    result_type=ChatResult,
)

@agent.tool(retries=2)
def get_user_by_name(ctx: RunContext[DatabaseConn], name: str) -> int:
    """Get a user's ID from their full name."""
    user_id = ctx.deps.users.get(name=name)
    if user_id is None:
        raise ModelRetry(f'No user found with name {name!r}, provide their full name')
    return user_id

result = agent.run_sync(
    'Send a message to John Doe asking for coffee next week', deps=DatabaseConn()
)
print(result.data)
# user_id=123 message='Hello John, would you be free for coffee sometime next week?'
```

## Model Errors

If models behave unexpectedly, agent runs will raise [`UnexpectedModelBehavior`](../api/exceptions/#pydantic_ai.exceptions.UnexpectedModelBehavior).

Example with capturing messages:

```python
from pydantic_ai import Agent, ModelRetry, UnexpectedModelBehavior, capture_run_messages

agent = Agent('openai:gpt-4o')

@agent.tool_plain
def calc_volume(size: int) -> int:
    if size == 42:
        return size**3
    else:
        raise ModelRetry('Please try again.')

with capture_run_messages() as messages:
    try:
        result = agent.run_sync('Please get me the volume of a box with size 6.')
    except UnexpectedModelBehavior as e:
        print('An error occurred:', e)
        print('cause:', repr(e.__cause__))
        print('messages:', messages)
```

> **Note:** Using `capture_run_messages` captures the messages for the first run within its context.
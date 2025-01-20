# Function Tools - PydanticAI

Function tools provide a mechanism for models to retrieve extra information to help them generate a response. They're useful when it is impractical or impossible to put all the context an agent might need into the system prompt or when you want to make agents' behavior more deterministic or reliable by deferring some of the logic required to generate a response to another (not necessarily AI-powered) tool.

> 📘 **Function tools vs. RAG**
> 
> - Function tools are basically the "R" of RAG (Retrieval-Augmented Generation) — they augment what the model can do by letting it request extra information.
> - The main semantic difference between PydanticAI Tools and RAG is RAG is synonymous with vector search, while PydanticAI tools are more general-purpose.
> - PydanticAI may add support for vector search functionality in the future, particularly an API for generating embeddings.

## Options to register tools with an agent:

- Via the `@agent.tool` decorator — for tools that need access to the agent context.
- Via the `@agent.tool_plain` decorator — for tools that do not need access to the agent context.
- Via the `tools` keyword argument to `Agent` which can take either plain functions or instances of `Tool`.

`@agent.tool` is considered the default decorator since, in the majority of cases, tools will need access to the agent context.

### Example Code: Using Both Decorators

```python
import random
from pydantic_ai import Agent, RunContext

agent = Agent(
    'gemini-1.5-flash',  
    deps_type=str,
    system_prompt=(
        "You're a dice game, you should roll the die and see if the number "
        "you get back matches the user's guess. If so, tell them they're a winner. "
        "Use the player's name in the response."
    ),
)

@agent.tool_plain
def roll_die() -> str:
    """Roll a six-sided die and return the result."""
    return str(random.randint(1, 6))

@agent.tool
def get_player_name(ctx: RunContext[str]) -> str:
    """Get the player's name."""
    return ctx.deps

dice_result = agent.run_sync('My guess is 4', deps='Anne')
print(dice_result.data)
#> Congratulations Anne, you guessed correctly! You're a winner!
```

_This example can be run "as is"._

## Inspecting Game Messages

To print the messages from the game:

```python
from dice_game import dice_result

print(dice_result.all_messages())
```

## Diagram of Message Flow

```plaintext
sequenceDiagram
    participant Agent
    participant LLM

    Note over Agent: Send prompts
    Agent ->> LLM: System: "You're a dice game..."<br>User: "My guess is 4"
    activate LLM
    Note over LLM: LLM decides to use<br>a tool

    LLM ->> Agent: Call tool<br>roll_die()
    deactivate LLM
    activate Agent
    Note over Agent: Rolls a six-sided die

    Agent -->> LLM: ToolReturn<br>"4"
    deactivate Agent
    activate LLM
    Note over LLM: LLM decides to use<br>another tool

    LLM ->> Agent: Call tool<br>get_player_name()
    deactivate LLM
    activate Agent
    Note over Agent: Retrieves player name
    Agent -->> LLM: ToolReturn<br>"Anne"
    deactivate Agent
    activate LLM
    Note over LLM: LLM constructs final response

    LLM ->> Agent: ModelResponse<br>"Congratulations Anne, ..."
    deactivate LLM
    Note over Agent: Game session complete
```

## Registering Function Tools via Keyword Argument

Apart from decorators, tools can also be registered via the `tools` argument to the `Agent` constructor. This method is useful for reusing tools and allows more fine-grained control over the tools.

```python
import random
from pydantic_ai import Agent, RunContext, Tool

def roll_die() -> str:
    """Roll a six-sided die and return the result."""
    return str(random.randint(1, 6))

def get_player_name(ctx: RunContext[str]) -> str:
    """Get the player's name."""
    return ctx.deps

agent_a = Agent(
    'gemini-1.5-flash',
    deps_type=str,
    tools=[roll_die, get_player_name],
)

agent_b = Agent(
    'gemini-1.5-flash',
    deps_type=str,
    tools=[
        Tool(roll_die, takes_ctx=False),
        Tool(get_player_name, takes_ctx=True),
    ],
)
dice_result = agent_b.run_sync('My guess is 4', deps='Anne')
print(dice_result.data)
#> Congratulations Anne, you guessed correctly! You're a winner!
```

_This example can be run "as is"._

## Function Tools vs. Structured Results

Tools are used to define the schema(s) for structured responses, thus a model might have access to many tools, some of which call function tools while others end the run and return a result.

## Function Tools and Schema

Function parameters are extracted from the function signature, except `RunContext`. Documentation strings enhance schema clarity as well.

### Example: Tool Schema Display

```python
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, ModelResponse
from pydantic_ai.models.function import AgentInfo, FunctionModel

agent = Agent()

@agent.tool_plain
def foobar(a: int, b: str, c: dict[str, list[float]]) -> str:
    """Get me foobar.

    Args:
        a: apple pie
        b: banana cake
        c: carrot smoothie
    """
    return f'{a} {b} {c}'

def print_schema(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    tool = info.function_tools[0]
    print(tool.description)
    #> Get me foobar.
    print(tool.parameters_json_schema)
    return ModelResponse.from_text(content='foobar')

agent.run_sync('hello', model=FunctionModel(print_schema))
```

_This example can be run "as is"._

## Dynamic Function Tools

Tools can be configured dynamically using a `prepare` function. This allows for customization of tool definitions per step.

### Example: Conditional Tool Inclusion

```python
from typing import Union

from pydantic_ai import Agent, RunContext
from pydantic_ai.tools import ToolDefinition

agent = Agent('test')

async def only_if_42(ctx: RunContext[int], tool_def: ToolDefinition) -> Union[ToolDefinition, None]:
    if ctx.deps == 42:
        return tool_def

@agent.tool(prepare=only_if_42)
def hitchhiker(ctx: RunContext[int], answer: str) -> str:
    return f'{ctx.deps} {answer}'

result = agent.run_sync('testing...', deps=41)
print(result.data)
#> success (no tool calls)
result = agent.run_sync('testing...', deps=42)
print(result.data)
#> {"hitchhiker":"42 a"}
```

_This example can be run "as is"._

### Example: Customizing Tool Parameters

```python
from __future__ import annotations

from typing import Literal

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.test import TestModel
from pydantic_ai.tools import Tool, ToolDefinition

async def prepare_greet(ctx: RunContext[Literal['human', 'machine']], tool_def: ToolDefinition) -> ToolDefinition | None:
    d = f'Name of the {ctx.deps} to greet.'
    tool_def.parameters_json_schema['properties']['name']['description'] = d
    return tool_def

greet_tool = Tool(greet, prepare=prepare_greet)
test_model = TestModel()
agent = Agent(test_model, tools=[greet_tool], deps_type=Literal['human', 'machine'])

result = agent.run_sync('testing...', deps='human')
print(result.data)
#> {"greet":"hello a"}
print(test_model.agent_model_function_tools)
```

_This example can be run "as is"._
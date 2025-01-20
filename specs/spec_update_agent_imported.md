# Specification Template
> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

- Create a new pydantic-ai agent "OchestratorAgent" that orchestrates the other agents, keeps track of which agent is currently running, and passes messages between agents.
- Create a new pydantic-ai agent "SetupAgent" responsible for capturing the users name, whether they are building a formulation for a new client or one setup previously. SetupAgent modifies user-specific configuration options that have a large impact on the behavior of the other agents. One of the configurations is "assistance_level", which determines the level of assistance provided by the other agents (i.e. higher rate of follow-up questions, more detailed responses, etc.)
- Create a new pydantic-ai agent "ChatAgent" that captures the users input before passing it to the IntentIdentifier agent. ChatAgent is also responsible for formatting any responses from the other agents into a user-friendly format as specified by its personality configuration ("friendly", "formal", "clinical", "technical"). Any of the other agents are able to immediately make calls to the ChatAgent if they need more information before proceeding with their task. Inputs and outputs of the ChatAgent are added to the message history database, the contents of which drives the chat UI
- Create a new pydantic-ai agent "DatabaseAgent" that is responsible for storing and retrieving data from the graph database. To prevent excessive calls to the database, the graph is cached and modified in DatabaseAgent instance memory until the user explicitly saves the graph, terminates the session, times out or at a periodic backup interval.
- Create a new pydantic-ai agent "IntentIdentifier" that will identify the user's intent based on the user's input. If more than one intent is identified, the task will be divided into subtasks and processes will be run sequentially or in parallel depending on the types of tasks identified
- Create a new pydantic-ai agent "NoteTaker" that will update the graph based on the user's input. NoteTaker communicates with the QuestionAgent to generate further follow-up questions for the user to optionally answer, a queue of which can be sent to the ChatAgent to be displayed to the user as needed
- Each agent has a predefined system prompt that is sent to LLMs

## Mid-Level Objective

- [List of mid-level objectives - what are the steps to achieve the high-level objective?]
- [Each objective should be concrete and measurable]
- [But not too detailed - save details for implementation notes]

- Provide an interface to the graph_construtor.py api by creating wrappers around the necessary functions responsible for graph manipulation
- Each wrapper is registered as a tool for the agent
- Transform user queries into one or more requests to update the data graph
- Identify the data graph nodes that need to be updated
- Update the data graph nodes
- Confirm with user what has been updated with a summary of the changes

## Implementation Notes
- [Important technical details - what are the important technical details?]
- [Dependencies and requirements - what are the dependencies and requirements?]
- [Coding standards to follow - what are the coding standards to follow?]
- [Other technical guidance - what are other technical guidance?]

- Confirm strictly to pydantic-ai api

### Examples of pydantic-ai api

```xml
<import-files>
[docs/pydantic-ai/models.md](docs/pydantic-ai/models.md)
[docs/pydantic-ai/agents.md](docs/pydantic-ai/agents.md)
[docs/pydantic-ai/tools.md](docs/pydantic-ai/tools.md)
[docs/pydantic-ai/results.md](docs/pydantic-ai/results.md)
[docs/pydantic-ai/message-history.md](docs/pydantic-ai/message-history.md)
[docs/pydantic-ai/testing-evals.md](docs/pydantic-ai/testing-evals.md)
[docs/pydantic-ai/logfire.md](docs/pydantic-ai/logfire.md)
[docs/pydantic-ai/multi-agent-applications.md](docs/pydantic-ai/multi-agent-applications.md)
[docs/pydantic-ai/chat-app.md](docs/pydantic-ai/chat-app.md)
</import-files>

<example-code>
# Models - PydanticAI

PydanticAI is Model-agnostic and has built-in support for the following model providers:

- [OpenAI](#openai)
- [Anthropic](#anthropic)
- Gemini via two different APIs: [Generative Language API](#gemini) and [VertexAI API](#gemini-via-vertexai)
- [Ollama](#ollama)
- [Groq](#groq)
- [Mistral](#mistral)

See [OpenAI-compatible models](#openai-compatible-models) for more examples on how to use models such as [OpenRouter](#openrouter), [Grok (xAI)](#grok-xai), and [DeepSeek](#deepseek) that support the OpenAI SDK.

You can also [add support for other models](#implementing-custom-models).

PydanticAI also comes with [`TestModel`](../api/models/test/) and [`FunctionModel`](../api/models/function/) for testing and development.

To use each model provider, you need to configure your local environment and make sure you have the right packages installed.

## OpenAI

### Install

To use OpenAI models, you need to either install [`pydantic-ai`](../install/) or install [`pydantic-ai-slim`](../install/#slim-install) with the `openai` optional group:

<details>
<summary>pip</summary>

```bash
pip install 'pydantic-ai-slim[openai]'
```

</details>

<details>
<summary>uv</summary>

```bash
uv add 'pydantic-ai-slim[openai]'
```

</details>

### Configuration

To use [`OpenAIModel`](../api/models/openai/#pydantic_ai.models.openai.OpenAIModel) through their main API, go to [platform.openai.com](https://platform.openai.com/) and generate an API key.

### Environment variable

Once you have the API key, you can set it as an environment variable:

```bash
export OPENAI_API_KEY='your-api-key'
```

You can then use [`OpenAIModel`](../api/models/openai/#pydantic_ai.models.openai.OpenAIModel) by name:

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o')
...
```

Or initialize the model directly with just the model name:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel('gpt-4o')
agent = Agent(model)
...
```

### `api_key` argument

If you don't want to set the environment variable, you can pass it at runtime via the [`api_key` argument](../api/models/openai/#pydantic_ai.models.openai.OpenAIModel.__init__):

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel('gpt-4o', api_key='your-api-key')
agent = Agent(model)
...
```

### Custom OpenAI Client

`OpenAIModel` also accepts a custom `AsyncOpenAI` client via the [`openai_client` parameter](../api/models/openai/#pydantic_ai.models.openai.OpenAIModel.__init__), so you can customize the `organization`, `project`, `base_url`, etc. You could also use the [`AsyncAzureOpenAI`](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/switching-endpoints) client to use the Azure OpenAI API.

```python
from openai import AsyncAzureOpenAI

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

client = AsyncAzureOpenAI(
    azure_endpoint='...',
    api_version='2024-07-01-preview',
    api_key='your-api-key',
)

model = OpenAIModel('gpt-4o', openai_client=client)
agent = Agent(model)
...
```

## Anthropic

### Install

To use [`AnthropicModel`](../api/models/anthropic/#pydantic_ai.models.anthropic.AnthropicModel) models, you need to either install [`pydantic-ai`](../install/) or install [`pydantic-ai-slim`](../install/#slim-install) with the `anthropic` optional group:

<details>
<summary>pip</summary>

```bash
pip install 'pydantic-ai-slim[anthropic]'
```

</details>

<details>
<summary>uv</summary>

```bash
uv add 'pydantic-ai-slim[anthropic]'
```

</details>

### Configuration

To use [Anthropic](https://anthropic.com) through their API, generate an API key from [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys).

[`AnthropicModelName`](../api/models/anthropic/#pydantic_ai.models.anthropic.AnthropicModelName) contains a list of available Anthropic models.

### Environment variable

Set the API key as an environment variable:

```bash
export ANTHROPIC_API_KEY='your-api-key'
```

Use [`AnthropicModel`](../api/models/anthropic/#pydantic_ai.models.anthropic.AnthropicModel) by name:

```python
from pydantic_ai import Agent

agent = Agent('claude-3-5-sonnet-latest')
...
```

Or initialize the model directly with just the model name:

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

model = AnthropicModel('claude-3-5-sonnet-latest')
agent = Agent(model)
...
```

### `api_key` argument

Pass the API key at runtime via the [`api_key` argument](../api/models/anthropic/#pydantic_ai.models.anthropic.AnthropicModel.__init__):

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

model = AnthropicModel('claude-3-5-sonnet-latest', api_key='your-api-key')
agent = Agent(model)
...
```

## Gemini

### For prototyping only

> **Warning:** Google refers to this API as the "hobby" API, and it may not be reliable for production use. For production, use the [VertexAI API](#gemini-via-vertexai).

### Install

To use [`GeminiModel`](../api/models/gemini/#pydantic_ai.models.gemini.GeminiModel), just install [`pydantic-ai`](../install/) or [`pydantic-ai-slim`](../install/#slim-install), no extra dependencies are required.

### Configuration

[`GeminiModel`](../api/models/gemini/#pydantic_ai.models.gemini.GeminiModel) allows you to use Google's Gemini models through the [Generative Language API](https://ai.google.dev/api/all-methods).

[`GeminiModelName`](../api/models/gemini/#pydantic_ai.models.gemini.GeminiModelName) contains a list of available Gemini models available through this interface.

Generate an API key from [aistudio.google.com](https://aistudio.google.com/).

### Environment variable

Set the API key as an environment variable:

```bash
export GEMINI_API_KEY=your-api-key
```

Use [`GeminiModel`](../api/models/gemini/#pydantic_ai.models.gemini.GeminiModel) by name:

```python
from pydantic_ai import Agent

agent = Agent('google-gla:gemini-1.5-flash')
...
```

> **Note:** The `google-gla` prefix represents the Google Generative Language API. `google-vertex` is used with Vertex AI.

Or initialize the model directly with just the model name:

```python
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

model = GeminiModel('gemini-1.5-flash')
agent = Agent(model)
...
```

### `api_key` argument

Pass the API key at runtime via the [`api_key` argument](../api/models/gemini/#pydantic_ai.models.gemini.GeminiModel.__init__):

```python
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

model = GeminiModel('gemini-1.5-flash', api_key='your-api-key')
agent = Agent(model)
...
```

## Gemini via VertexAI

To run Gemini models in production, use [`VertexAIModel`](../api/models/vertexai/#pydantic_ai.models.vertexai.VertexAIModel).

[`GeminiModelName`](../api/models/gemini/#pydantic_ai.models.gemini.GeminiModelName) contains a list of available models.

### Install

Install with the `vertexai` optional group:

<details>
<summary>pip</summary>

```bash
pip install 'pydantic-ai-slim[vertexai]'
```

</details>

<details>
<summary>uv</summary>

```bash
uv add 'pydantic-ai-slim[vertexai]'
```

</details>

### Configuration

This interface has various advantages over the `generativelanguage.googleapis.com` API:

1. More reliable with marginally lower latency.
2. Allows purchasing provisioned throughput.
3. No authentication setup needed in a GCP environment.
4. Customizable region settings.

Disadvantage: Service account setup for local development can be complex.

### Application default credentials

If running inside GCP or with a configured `gcloud` CLI, use [`VertexAIModel`](../api/models/vertexai/#pydantic_ai.models.vertexai.VertexAIModel) with default credentials:

```python
from pydantic_ai import Agent
from pydantic_ai.models.vertexai import VertexAIModel

model = VertexAIModel('gemini-1.5-flash')
agent = Agent(model)
...
```

> **Note:** Network requests for `google.auth.default()` won't run until `agent.run()`. Call [`await model.ainit()`](../api/models/vertexai/#pydantic_ai.models.vertexai.VertexAIModel.ainit) to pre-empt errors.

### Service account

For service account authentication, download the JSON file and use:

```python
from pydantic_ai import Agent
from pydantic_ai.models.vertexai import VertexAIModel

model = VertexAIModel(
    'gemini-1.5-flash',
    service_account_file='path/to/service-account.json',
)
agent = Agent(model)
...
```

### Customising region

Set the region for requests via the [`region` argument](../api/models/vertexai/#pydantic_ai.models.vertexai.VertexAIModel.__init__):

```python
from pydantic_ai import Agent
from pydantic_ai.models.vertexai import VertexAIModel

model = VertexAIModel('gemini-1.5-flash', region='asia-east1')
agent = Agent(model)
...
```

[`VertexAiRegion`](../api/models/vertexai/#pydantic_ai.models.vertexai.VertexAiRegion) contains available regions.

## Ollama

### Install

Install with the `openai` optional group:

<details>
<summary>pip</summary>

```bash
pip install 'pydantic-ai-slim[openai]'
```

</details>

<details>
<summary>uv</summary>

```bash
uv add 'pydantic-ai-slim[openai]'
```

</details>

> **This is because internally, `OllamaModel` uses the OpenAI API.**

### Configuration

To use [Ollama](https://ollama.com/), download the client and a model from the [Ollama model library](https://ollama.com/library). Ensure the server is running. See the [Ollama documentation](https://github.com/ollama/ollama/tree/main/docs) for details.

Refer to the [Ollama setup documentation](https://github.com/pydantic/pydantic-ai/blob/main/docs/api/models/ollama.md) for a detailed setup guide.

## Groq

### Install

Install with the `groq` optional group:

<details>
<summary>pip</summary>

```bash
pip install 'pydantic-ai-slim[groq]'
```

</details>

<details>
<summary>uv</summary>

```bash
uv add 'pydantic-ai-slim[groq]'
```

</details>

### Configuration

Generate an API key from [console.groq.com/keys](https://console.groq.com/keys).

[`GroqModelName`](../api/models/groq/#pydantic_ai.models.groq.GroqModelName) contains available models.

### Environment variable

Set the API key as an environment variable:

```bash
export GROQ_API_KEY='your-api-key'
```

Use [`GroqModel`](../api/models/groq/#pydantic_ai.models.groq.GroqModel) by name:

```python
from pydantic_ai import Agent

agent = Agent('groq:llama-3.1-70b-versatile')
...
```

Or initialize the model directly with just the model name:

```python
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel

model = GroqModel('llama-3.1-70b-versatile')
agent = Agent(model)
...
```

### `api_key` argument

Pass the API key at runtime via the [`api_key` argument](../api/models/groq/#pydantic_ai.models.groq.GroqModel.__init__):

```python
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel

model = GroqModel('llama-3.1-70b-versatile', api_key='your-api-key')
agent = Agent(model)
...
```

## Mistral

### Install

Install with the `mistral` optional group:

<details>
<summary>pip</summary>

```bash
pip install 'pydantic-ai-slim[mistral]'
```

</details>

<details>
<summary>uv</summary>

```bash
uv add 'pydantic-ai-slim[mistral]'
```

</details>

### Configuration

Generate an API key from [console.mistral.ai/api-keys/](https://console.mistral.ai/api-keys/).

[`NamedMistralModels`](../api/models/mistral/#pydantic_ai.models.mistral.NamedMistralModels) contains popular models.

### Environment variable

Set the API key as an environment variable:

```bash
export MISTRAL_API_KEY='your-api-key'
```

Use [`MistralModel`](../api/models/mistral/#pydantic_ai.models.mistral.MistralModel) by name:

```python
from pydantic_ai import Agent

agent = Agent('mistral:mistral-large-latest')
...
```

Or initialize the model directly with just the model name:

```python
from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel

model = MistralModel('mistral-small-latest')
agent = Agent(model)
...
```

### `api_key` argument

Pass the API key at runtime via the [`api_key` argument](../api/models/mistral/#pydantic_ai.models.mistral.MistralModel.__init__):

```python
from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel

model = MistralModel('mistral-small-latest', api_key='your-api-key')
agent = Agent(model)
...
```

## OpenAI-compatible Models

Many models are compatible with the OpenAI API and can be used with the [`OpenAIModel`](../api/models/openai/#pydantic_ai.models.openai.OpenAIModel) in PydanticAI. To use another OpenAI-compatible API, use the [`base_url`](../api/models/openai/#pydantic_ai.models.openai.OpenAIModel.__init__) and [`api_key`](../api/models/openai/#pydantic_ai.models.openai.OpenAIModel.__init__) arguments:

```python
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel(
    'model_name',
    base_url='https://<openai-compatible-api-endpoint>.com',
    api_key='your-api-key',
)
...
```

### OpenRouter

Create an API key at [openrouter.ai/keys](https://openrouter.ai/keys). Pass it to `OpenAIModel` as the `api_key` argument:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel(
    'anthropic/claude-3.5-sonnet',
    base_url='https://openrouter.ai/api/v1',
    api_key='your-openrouter-api-key',
)
agent = Agent(model)
...
```

### Grok (xAI)

Create an API key in the [xAI API Console](https://console.x.ai/). Follow the [xAI API Documentation](https://docs.x.ai/docs/overview), setting the `base_url` and `api_key`:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel(
    'grok-2-1212',
    base_url='https://api.x.ai/v1',
    api_key='your-xai-api-key',
)
agent = Agent(model)
...
```

### DeepSeek

Create an API key at [DeepSeek API Platform](https://platform.deepseek.com/api_keys). Follow the [DeepSeek API Documentation](https://platform.deepseek.com/docs/api/overview), setting the `base_url` and `api_key`:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel(
    'deepseek-chat',
    base_url='https://api.deepseek.com',
    api_key='your-deepseek-api-key',
)
agent = Agent(model)
...
```

## Implementing Custom Models

Subclass the [`Model`](../api/models/base/#pydantic_ai.models.Model) abstract base class to support new models.

Implement the following abstract base classes:

- [`AgentModel`](../api/models/base/#pydantic_ai.models.AgentModel)
- [`StreamedResponse`](../api/models/base/#pydantic_ai.models.StreamedResponse)

Review existing implementations like [`OpenAIModel`](https://github.com/pydantic/pydantic-ai/blob/main/pydantic_ai_slim/pydantic_ai/models/openai.py) for guidance.

Refer to the [contributing guidelines](../contributing/#new-model-rules) for more information.# Agents Documentation

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

> **Note:** Using `capture_run_messages` captures the messages for the first run within its context.# Function Tools - PydanticAI

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

_This example can be run "as is"._# Results - PydanticAI

Results are the final values returned from [running an agent](../agents/#running-agents). The result values are wrapped in [`RunResult`](../api/result/#pydantic_ai.result.RunResult) and [`StreamedRunResult`](../api/result/#pydantic_ai.result.StreamedRunResult) so you can access other data like [usage](../api/usage/#pydantic_ai.usage.Usage) of the run and [message history](../message-history/#accessing-messages-from-results).

Both `RunResult` and `StreamedRunResult` are generic in the data they wrap, so typing information about the data returned by the agent is preserved.

```python
# olympics.py

from pydantic import BaseModel
from pydantic_ai import Agent

class CityLocation(BaseModel):
    city: str
    country: str

agent = Agent('gemini-1.5-flash', result_type=CityLocation)
result = agent.run_sync('Where were the olympics held in 2012?')
print(result.data)
#> city='London' country='United Kingdom'
print(result.usage())
"""
Usage(requests=1, request_tokens=57, response_tokens=8, total_tokens=65, details=None)
"""
```

_(This example is complete, it can be run "as is")_

Runs end when either a plain text response is received or the model calls a tool associated with one of the structured result types. We will add limits to make sure a run doesn't go on indefinitely, see [#70](https://github.com/pydantic/pydantic-ai/issues/70).

## Result data

When the result type is `str`, or a union including `str`, plain text responses are enabled on the model, and the raw text response from the model is used as the response data.

If the result type is a union with multiple members (after remove `str` from the members), each member is registered as a separate tool with the model in order to reduce the complexity of the tool schemas and maximize the chances a model will respond correctly.

If the result type schema is not of type `"object"`, the result type is wrapped in a single element object, so the schema of all tools registered with the model are object schemas.

Structured results (like tools) use Pydantic to build the JSON schema used for the tool, and to validate the data returned by the model.

> **Note:** Bring on PEP-747  
> Until [PEP-747](https://peps.python.org/pep-0747/) "Annotating Type Forms" lands, unions are not valid as `type`s in Python.

Here's an example of returning either text or a structured value:

```python
# box_or_error.py

from typing import Union
from pydantic import BaseModel
from pydantic_ai import Agent

class Box(BaseModel):
    width: int
    height: int
    depth: int
    units: str

agent: Agent[None, Union[Box, str]] = Agent(
    'openai:gpt-4o-mini',
    result_type=Union[Box, str],  # type: ignore
    system_prompt=(
        "Extract me the dimensions of a box, "
        "if you can't extract all data, ask the user to try again."
    ),
)

result = agent.run_sync('The box is 10x20x30')
print(result.data)
#> Please provide the units for the dimensions (e.g., cm, in, m).

result = agent.run_sync('The box is 10x20x30 cm')
print(result.data)
#> width=10 height=20 depth=30 units='cm'
```

_(This example is complete, it can be run "as is")_

Here's an example of using a union return type which registered multiple tools and wraps non-object schemas in an object:

```python
# colors_or_sizes.py

from typing import Union
from pydantic_ai import Agent

agent: Agent[None, Union[list[str], list[int]]] = Agent(
    'openai:gpt-4o-mini',
    result_type=Union[list[str], list[int]],  # type: ignore
    system_prompt='Extract either colors or sizes from the shapes provided.',
)

result = agent.run_sync('red square, blue circle, green triangle')
print(result.data)
#> ['red', 'blue', 'green']

result = agent.run_sync('square size 10, circle size 20, triangle size 30')
print(result.data)
#> [10, 20, 30]
```

_(This example is complete, it can be run "as is")_

### Result validators functions

Some validation is inconvenient or impossible to do in Pydantic validators, particularly when the validation requires IO and is asynchronous. PydanticAI provides a way to add validation functions via the [`agent.result_validator`](../api/agent/#pydantic_ai.agent.Agent.result_validator) decorator.

Here's a simplified variant of the [SQL Generation example](../examples/sql-gen/):

```python
# sql_gen.py

from typing import Union
from fake_database import DatabaseConn, QueryError
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext, ModelRetry

class Success(BaseModel):
    sql_query: str

class InvalidRequest(BaseModel):
    error_message: str

Response = Union[Success, InvalidRequest]
agent: Agent[DatabaseConn, Response] = Agent(
    'gemini-1.5-flash',
    result_type=Response,  # type: ignore
    deps_type=DatabaseConn,
    system_prompt='Generate PostgreSQL flavored SQL queries based on user input.',
)

@agent.result_validator
async def validate_result(ctx: RunContext[DatabaseConn], result: Response) -> Response:
    if isinstance(result, InvalidRequest):
        return result
    try:
        await ctx.deps.execute(f'EXPLAIN {result.sql_query}')
    except QueryError as e:
        raise ModelRetry(f'Invalid query: {e}') from e
    else:
        return result

result = agent.run_sync(
    'get me users who were last active yesterday.', deps=DatabaseConn()
)
print(result.data)
#> sql_query='SELECT * FROM users WHERE last_active::date = today() - interval 1 day'
```

_(This example is complete, it can be run "as is")_

## Streamed Results

There are two main challenges with streamed results:

1. Validating structured responses before they're complete, achieved by "partial validation" recently added to Pydantic in [pydantic/pydantic#10748](https://github.com/pydantic/pydantic/pull/10748).
2. When receiving a response, determining if it's the final response without starting to stream it and inspecting the content. PydanticAI streams enough of the response to detect tool calls or results, then streams the entire response fully before calling tools or returning the stream as a [`StreamedRunResult`](../api/result/#pydantic_ai.result.StreamedRunResult).

### Streaming Text

Example of streaming text result:

```python
# streamed_hello_world.py

from pydantic_ai import Agent

agent = Agent('gemini-1.5-flash')  # Streaming works with the standard Agent class, and doesn't require any special setup, just a model that supports streaming (currently all models support streaming).

async def main():
    async with agent.run_stream('Where does "hello world" come from?') as result:  # The Agent.run_stream() method is used to start a streamed run, this method returns a context manager so the connection can be closed when the stream completes.
        async for message in result.stream_text():  # Each item yield by StreamedRunResult.stream_text() is the complete text response, extended as new data is received.
            print(message)
            #> The first known
            #> The first known use of "hello,
            #> The first known use of "hello, world" was in
            #> The first known use of "hello, world" was in a 1974 textbook
            #> The first known use of "hello, world" was in a 1974 textbook about the C
            #> The first known use of "hello, world" was in a 1974 textbook about the C programming language.
```

_(This example is complete, it can be run "as is" — you'll need to add `asyncio.run(main())` to run `main`)_

You can also stream text as deltas rather than complete text each time:

```python
# streamed_delta_hello_world.py

from pydantic_ai import Agent

agent = Agent('gemini-1.5-flash')

async def main():
    async with agent.run_stream('Where does "hello world" come from?') as result:
        async for message in result.stream_text(delta=True):  # stream_text will error if the response is not text
            print(message)
            #> The first known
            #> use of "hello,
            #> world" was in
            #> a 1974 textbook
            #> about the C
            #> programming language.
```

_(This example is complete, it can be run "as is" — you'll need to add `asyncio.run(main())` to run `main`)_

> **Warning:** Result message not included in `messages`
> 
> The final result message will **NOT** be added to result messages if you use `.stream_text(delta=True)`, see [Messages and chat history](../message-history/) for more information.

### Streaming Structured Responses

Not all types are supported with partial validation in Pydantic, see [pydantic/pydantic#10748](https://github.com/pydantic/pydantic/pull/10748). For model-like structures, it's currently best to use `TypeDict`.

Here's an example of streaming a user profile as it's built:

```python
# streamed_user_profile.py

from datetime import date
from typing_extensions import TypedDict
from pydantic_ai import Agent

class UserProfile(TypedDict, total=False):
    name: str
    dob: date
    bio: str

agent = Agent(
    'openai:gpt-4o',
    result_type=UserProfile,
    system_prompt='Extract a user profile from the input',
)

async def main():
    user_input = 'My name is Ben, I was born on January 28th 1990, I like the chain the dog and the pyramid.'
    async with agent.run_stream(user_input) as result:
        async for profile in result.stream():
            print(profile)
            #> {'name': 'Ben'}
            #> {'name': 'Ben'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the '}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyr'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyramid'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyramid'}
```

_(This example is complete, it can be run "as is" — you'll need to add `asyncio.run(main())` to run `main`)_

If you want fine-grained control of validation, particularly catching validation errors, you can use the following pattern:

```python
# streamed_user_profile.py

from datetime import date
from pydantic import ValidationError
from typing_extensions import TypedDict
from pydantic_ai import Agent

class UserProfile(TypedDict, total=False):
    name: str
    dob: date
    bio: str

agent = Agent('openai:gpt-4o', result_type=UserProfile)

async def main():
    user_input = 'My name is Ben, I was born on January 28th 1990, I like the chain the dog and the pyramid.'
    async with agent.run_stream(user_input) as result:
        async for message, last in result.stream_structured(debounce_by=0.01):  # `stream_structured` streams the data as `ModelResponse` objects, thus iteration can't fail with a `ValidationError`.
            try:
                profile = await result.validate_structured_result(  # `validate_structured_result` validates the data, `allow_partial=True` enables pydantic's `experimental_allow_partial` flag on `TypeAdapter`.
                    message,
                    allow_partial=not last,
                )
            except ValidationError:
                continue
            print(profile)
            #> {'name': 'Ben'}
            #> {'name': 'Ben'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the '}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyr'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyramid'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyramid'}
```

_(This example is complete, it can be run "as is" — you'll need to add `asyncio.run(main())` to run `main`)_

## Examples

The following examples demonstrate how to use streamed responses in PydanticAI:

- [Stream markdown](../examples/stream-markdown/)
- [Stream Whales](../examples/stream-whales/)```markdown

# Messages and chat history

PydanticAI provides access to messages exchanged during an agent run. These messages can be used both to continue a coherent conversation and to understand how an agent performed.

### Accessing Messages from Results

After running an agent, you can access the messages exchanged during that run from the `result` object.

Both [`RunResult`](../api/result/#pydantic_ai.result.RunResult) (returned by [`Agent.run`](../api/agent/#pydantic_ai.agent.Agent.run), [`Agent.run_sync`](../api/agent/#pydantic_ai.agent.Agent.run_sync)) and [`StreamedRunResult`](../api/result/#pydantic_ai.result.StreamedRunResult) (returned by [`Agent.run_stream`](../api/agent/#pydantic_ai.agent.Agent.run_stream)) have the following methods:

- [`all_messages()`](../api/result/#pydantic_ai.result.RunResult.all_messages): returns all messages, including messages from prior runs. There's also a variant that returns JSON bytes, [`all_messages_json()`](../api/result/#pydantic_ai.result.RunResult.all_messages_json).
- [`new_messages()`](../api/result/#pydantic_ai.result.RunResult.new_messages): returns only the messages from the current run. There's also a variant that returns JSON bytes, [`new_messages_json()`](../api/result/#pydantic_ai.result.RunResult.new_messages_json).

> **Info: StreamedRunResult and complete messages**
> 
> On [`StreamedRunResult`](../api/result/#pydantic_ai.result.StreamedRunResult), the messages returned from these methods will only include the final result message once the stream has finished.
> 
> E.g. you've awaited one of the following coroutines:
> 
> - [`StreamedRunResult.stream()`](../api/result/#pydantic_ai.result.StreamedRunResult.stream)
> - [`StreamedRunResult.stream_text()`](../api/result/#pydantic_ai.result.StreamedRunResult.stream_text)
> - [`StreamedRunResult.stream_structured()`](../api/result/#pydantic_ai.result.StreamedRunResult.stream_structured)
> - [`StreamedRunResult.get_data()`](../api/result/#pydantic_ai.result.StreamedRunResult.get_data)
> 
> **Note:** The final result message will NOT be added to result messages if you use [`.stream_text(delta=True)`](../api/result/#pydantic_ai.result.StreamedRunResult.stream_text) since in this case the result content is never built as one string.

Example of accessing methods on a [`RunResult`](../api/result/#pydantic_ai.result.RunResult):

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', system_prompt='Be a helpful assistant.')

result = agent.run_sync('Tell me a joke.')
print(result.data)
#> Did you hear about the toothpaste scandal? They called it Colgate.

# all messages from the run
print(result.all_messages())
"""
[
    ModelRequest(
        parts=[
            SystemPromptPart(
                content='Be a helpful assistant.',
                dynamic_ref=None,
                part_kind='system-prompt',
            ),
            UserPromptPart(
                content='Tell me a joke.',
                timestamp=datetime.datetime(...),
                part_kind='user-prompt',
            ),
        ],
        kind='request',
    ),
    ModelResponse(
        parts=[
            TextPart(
                content='Did you hear about the toothpaste scandal? They called it Colgate.',
                part_kind='text',
            )
        ],
        timestamp=datetime.datetime(...),
        kind='response',
    ),
]
"""
```

*(This example is complete, it can be run "as is")*

Example of accessing methods on a [`StreamedRunResult`](../api/result/#pydantic_ai.result.StreamedRunResult):

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', system_prompt='Be a helpful assistant.')


async def main():
    async with agent.run_stream('Tell me a joke.') as result:
        # incomplete messages before the stream finishes
        print(result.all_messages())
        """
        [
            ModelRequest(
                parts=[
                    SystemPromptPart(
                        content='Be a helpful assistant.',
                        dynamic_ref=None,
                        part_kind='system-prompt',
                    ),
                    UserPromptPart(
                        content='Tell me a joke.',
                        timestamp=datetime.datetime(...),
                        part_kind='user-prompt',
                    ),
                ],
                kind='request',
            )
        ]
        """

        async for text in result.stream_text():
            print(text)
            #> Did you hear
            #> Did you hear about the toothpaste
            #> Did you hear about the toothpaste scandal? They called
            #> Did you hear about the toothpaste scandal? They called it Colgate.

        # complete messages once the stream finishes
        print(result.all_messages())
        """
        [
            ModelRequest(
                parts=[
                    SystemPromptPart(
                        content='Be a helpful assistant.',
                        dynamic_ref=None,
                        part_kind='system-prompt',
                    ),
                    UserPromptPart(
                        content='Tell me a joke.',
                        timestamp=datetime.datetime(...),
                        part_kind='user-prompt',
                    ),
                ],
                kind='request',
            ),
            ModelResponse(
                parts=[
                    TextPart(
                        content='Did you hear about the toothpaste scandal? They called it Colgate.',
                        part_kind='text',
                    )
                ],
                timestamp=datetime.datetime(...),
                kind='response',
            ),
        ]
        """
```

*(This example is complete, it can be run "as is" — you'll need to add `asyncio.run(main())` to run `main`)*

### Using Messages as Input for Further Agent Runs

The primary use of message histories in PydanticAI is to maintain context across multiple agent runs.

To use existing messages in a run, pass them to the `message_history` parameter of
[`Agent.run`](../api/agent/#pydantic_ai.agent.Agent.run), [`Agent.run_sync`](../api/agent/#pydantic_ai.agent.Agent.run_sync) or
[`Agent.run_stream`](../api/agent/#pydantic_ai.agent.Agent.run_stream).

If `message_history` is set and not empty, a new system prompt is not generated — we assume the existing message history includes a system prompt.

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', system_prompt='Be a helpful assistant.')

result1 = agent.run_sync('Tell me a joke.')
print(result1.data)
#> Did you hear about the toothpaste scandal? They called it Colgate.

result2 = agent.run_sync('Explain?', message_history=result1.new_messages())
print(result2.data)
#> This is an excellent joke invent by Samuel Colvin, it needs no explanation.

print(result2.all_messages())
"""
[
    ModelRequest(
        parts=[
            SystemPromptPart(
                content='Be a helpful assistant.',
                dynamic_ref=None,
                part_kind='system-prompt',
            ),
            UserPromptPart(
                content='Tell me a joke.',
                timestamp=datetime.datetime(...),
                part_kind='user-prompt',
            ),
        ],
        kind='request',
    ),
    ModelResponse(
        parts=[
            TextPart(
                content='Did you hear about the toothpaste scandal? They called it Colgate.',
                part_kind='text',
            )
        ],
        timestamp=datetime.datetime(...),
        kind='response',
    ),
    ModelRequest(
        parts=[
            UserPromptPart(
                content='Explain?',
                timestamp=datetime.datetime(...),
                part_kind='user-prompt',
            )
        ],
        kind='request',
    ),
    ModelResponse(
        parts=[
            TextPart(
                content='This is an excellent joke invent by Samuel Colvin, it needs no explanation.',
                part_kind='text',
            )
        ],
        timestamp=datetime.datetime(...),
        kind='response',
    ),
]
"""
```

*(This example is complete, it can be run "as is")*

## Other ways of using messages

Since messages are defined by simple dataclasses, you can manually create and manipulate, e.g. for testing.

The message format is independent of the model used, so you can use messages in different agents, or the same agent with different models.

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', system_prompt='Be a helpful assistant.')

result1 = agent.run_sync('Tell me a joke.')
print(result1.data)
#> Did you hear about the toothpaste scandal? They called it Colgate.

result2 = agent.run_sync(
    'Explain?', model='gemini-1.5-pro', message_history=result1.new_messages()
)
print(result2.data)
#> This is an excellent joke invent by Samuel Colvin, it needs no explanation.

print(result2.all_messages())
"""
[
    ModelRequest(
        parts=[
            SystemPromptPart(
                content='Be a helpful assistant.',
                dynamic_ref=None,
                part_kind='system-prompt',
            ),
            UserPromptPart(
                content='Tell me a joke.',
                timestamp=datetime.datetime(...),
                part_kind='user-prompt',
            ),
        ],
        kind='request',
    ),
    ModelResponse(
        parts=[
            TextPart(
                content='Did you hear about the toothpaste scandal? They called it Colgate.',
                part_kind='text',
            )
        ],
        timestamp=datetime.datetime(...),
        kind='response',
    ),
    ModelRequest(
        parts=[
            UserPromptPart(
                content='Explain?',
                timestamp=datetime.datetime(...),
                part_kind='user-prompt',
            )
        ],
        kind='request',
    ),
    ModelResponse(
        parts=[
            TextPart(
                content='This is an excellent joke invent by Samuel Colvin, it needs no explanation.',
                part_kind='text',
            )
        ],
        timestamp=datetime.datetime(...),
        kind='response',
    ),
]
"""
```

## Examples

For a more complete example of using messages in conversations, see the [chat app](../examples/chat-app/) example.
```
# Testing and Evals - PydanticAI

With PydanticAI and LLM integrations in general, there are two distinct kinds of test:

1. **Unit tests** — tests of your application code, and whether it's behaving correctly.
2. **Evals** — tests of the LLM, and how good or bad its responses are.

For the most part, these two kinds of tests have pretty separate goals and considerations.

## Unit tests

Unit tests for PydanticAI code are just like unit tests for any other Python code. Because for the most part they're nothing new, we have pretty well-established tools and patterns for writing and running these kinds of tests.

Unless you're really sure you know better, you'll probably want to follow roughly this strategy:
- Use [`pytest`](https://docs.pytest.org/en/stable/) as your test harness.
- If you find yourself typing out long assertions, use [inline-snapshot](https://15r10nk.github.io/inline-snapshot/latest/).
- Similarly, [dirty-equals](https://dirty-equals.helpmanual.io/latest/) can be useful for comparing large data structures.
- Use [`TestModel`](../api/models/test/#pydantic_ai.models.test.TestModel) or [`FunctionModel`](../api/models/function/#pydantic_ai.models.function.FunctionModel) in place of your actual model to avoid the usage, latency, and variability of real LLM calls.
- Use [`Agent.override`](../api/agent/#pydantic_ai.agent.Agent.override) to replace your model inside your application logic.
- Set [`ALLOW_MODEL_REQUESTS=False`](../api/models/base/#pydantic_ai.models.ALLOW_MODEL_REQUESTS) globally to block any requests from being made to non-test models accidentally.

### Unit testing with `TestModel`

The simplest and fastest way to exercise most of your application code is using [`TestModel`](../api/models/test/#pydantic_ai.models.test.TestModel). By default, it calls all tools in the agent, then returns either plain text or a structured response depending on the return type of the agent.

#### Code Example

Here's an example of writing unit tests using `TestModel` for a weather application:

```python
# weather_app.py
import asyncio
from datetime import date

from pydantic_ai import Agent, RunContext
from fake_database import DatabaseConn  # DatabaseConn is a class that holds a database connection
from weather_service import WeatherService  # WeatherService has methods to get weather forecasts and historic data about the weather

weather_agent = Agent(
    'openai:gpt-4o',
    deps_type=WeatherService,
    system_prompt='Providing a weather forecast at the locations the user provides.',
)


@weather_agent.tool
def weather_forecast(
    ctx: RunContext[WeatherService], location: str, forecast_date: date
) -> str:
    if forecast_date < date.today():  # We need to call a different endpoint depending on whether the date is in the past or the future, you'll see why this nuance is important below
        return ctx.deps.get_historic_weather(location, forecast_date)
    else:
        return ctx.deps.get_forecast(location, forecast_date)


async def run_weather_forecast(  # This function is the code we want to test, together with the agent it uses
    user_prompts: list[tuple[str, int]], conn: DatabaseConn
):
    """Run weather forecast for a list of user prompts and save."""
    async with WeatherService() as weather_service:

        async def run_forecast(prompt: str, user_id: int):
            result = await weather_agent.run(prompt, deps=weather_service)
            await conn.store_forecast(user_id, result.data)

        # Run all prompts in parallel
        await asyncio.gather(
            *(run_forecast(prompt, user_id) for (prompt, user_id) in user_prompts)
        )
```

```python
# test_weather_app.py
from datetime import timezone
import pytest

from dirty_equals import IsNow
from pydantic_ai import models, capture_run_messages
from pydantic_ai.models.test import TestModel
from pydantic_ai.messages import (
    ArgsDict,
    ModelResponse,
    SystemPromptPart,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
    ModelRequest,
)

from fake_database import DatabaseConn
from weather_app import run_weather_forecast, weather_agent

pytestmark = pytest.mark.anyio  # We're using anyio to run async tests.
models.ALLOW_MODEL_REQUESTS = False  # This is a safety measure to make sure we don't accidentally make real requests to the LLM while testing, see ALLOW_MODEL_REQUESTS for more details.


async def test_forecast():
    conn = DatabaseConn()
    user_id = 1
    with capture_run_messages() as messages:
        with weather_agent.override(model=TestModel()):  # We're using Agent.override to replace the agent's model with TestModel
            prompt = 'What will the weather be like in London on 2024-11-28?'
            await run_weather_forecast([(prompt, user_id)], conn)  # Now we call the function we want to test inside the override context manager.

    forecast = await conn.get_forecast(user_id)
    assert forecast == '{"weather_forecast":"Sunny with a chance of rain"}'  # But default, TestModel will return a JSON string summarising the tools calls made, and what was returned.

    assert messages == [  # So far we don't actually know which tools were called and with which values, we can use capture_run_messages to inspect messages from the most recent run and assert the exchange between the agent and the model occurred as expected.
        ModelRequest(
            parts=[
                SystemPromptPart(
                    content='Providing a weather forecast at the locations the user provides.',
                ),
                UserPromptPart(
                    content='What will the weather be like in London on 2024-11-28?',
                    timestamp=IsNow(tz=timezone.utc),  # The IsNow helper allows us to use declarative asserts even with data which will contain timestamps that change over time.
                ),
            ]
        ),
        ModelResponse(
            parts=[
                ToolCallPart(
                    tool_name='weather_forecast',
                    args=ArgsDict(
                        args_dict={
                            'location': 'a',
                            'forecast_date': '2024-01-01',
                        }
                    ),
                    tool_call_id=None,
                )
            ],
            timestamp=IsNow(tz=timezone.utc),
        ),
        ModelRequest(
            parts=[
                ToolReturnPart(
                    tool_name='weather_forecast',
                    content='Sunny with a chance of rain',
                    tool_call_id=None,
                    timestamp=IsNow(tz=timezone.utc),
                ),
            ],
        ),
        ModelResponse(
            parts=[
                TextPart(
                    content='{"weather_forecast":"Sunny with a chance of rain"}',
                )
            ],
            timestamp=IsNow(tz=timezone.utc),
        ),
    ]
```

### Unit testing with `FunctionModel`

To fully exercise `weather_forecast`, we can use [`FunctionModel`](../api/models/function/#pydantic_ai.models.function.FunctionModel) to customize how the tool is called.

Here's an example of using `FunctionModel` to test the `weather_forecast` tool with custom inputs:

```python
# test_weather_app2.py
import re

import pytest

from pydantic_ai import models
from pydantic_ai.messages import (
    ModelMessage,
    ModelResponse,
    ToolCallPart,
)
from pydantic_ai.models.function import AgentInfo, FunctionModel

from fake_database import DatabaseConn
from weather_app import run_weather_forecast, weather_agent

pytestmark = pytest.mark.anyio
models.ALLOW_MODEL_REQUESTS = False


def call_weather_forecast(  # We define a function call_weather_forecast that will be called by FunctionModel in place of the LLM
    messages: list[ModelMessage], info: AgentInfo
) -> ModelResponse:
    if len(messages) == 1:
        # First call, call the weather forecast tool
        user_prompt = messages[0].parts[-1]
        m = re.search(r'\d{4}-\d{2}-\d{2}', user_prompt.content)
        assert m is not None
        args = {'location': 'London', 'forecast_date': m.group()}  # Our function is slightly intelligent in that it tries to extract a date from the prompt.
        return ModelResponse(
            parts=[ToolCallPart.from_raw_args('weather_forecast', args)]
        )
    else:
        # Second call, return the forecast
        msg = messages[-1].parts[0]
        assert msg.part_kind == 'tool-return'
        return ModelResponse.from_text(f'The forecast is: {msg.content}')


async def test_forecast_future():
    conn = DatabaseConn()
    user_id = 1
    with weather_agent.override(model=FunctionModel(call_weather_forecast)):  # We use FunctionModel to replace the agent's model with our custom function.
        prompt = 'What will the weather be like in London on 2032-01-01?'
        await run_weather_forecast([(prompt, user_id)], conn)

    forecast = await conn.get_forecast(user_id)
    assert forecast == 'The forecast is: Rainy with a chance of sun'
```

### Overriding model via pytest fixtures

If you're writing lots of tests that all require the model to be overridden, you can use [pytest fixtures](https://docs.pytest.org/en/6.2.x/fixture.html) to override the model with `TestModel` or `FunctionModel` in a reusable way.

```python
# tests.py
import pytest
from weather_app import weather_agent

from pydantic_ai.models.test import TestModel


@pytest.fixture
def override_weather_agent():
    with weather_agent.override(model=TestModel()):
        yield


async def test_forecast(override_weather_agent: None):
    ...
    # Test code here
```

## Evals

"Evals" refers to evaluating a model's performance for a specific application. 

> **Warning**: Unlike unit tests, evals are an emerging art/science; anyone who claims to know for sure exactly how your evals should be defined can safely be ignored.

- Evals are generally more like benchmarks than unit tests; they never "pass" although they do "fail" — you care mostly about how they change over time.
- Since evals need to be run against the real model, they can be slow and expensive to run; you generally won't want to run them in CI for every commit.

### Measuring performance

The hardest part of evals is measuring how well the model has performed.

- **End to end, self-contained tests** — like the SQL example, we can test the final result of the agent near-instantly.
- **Synthetic self-contained tests** — writing unit test style checks that the output is as expected, checks like `'chewing gum' in response`, while these checks might seem simplistic can be helpful.
- **LLMs evaluating LLMs** — using another models, or even the same model with a different prompt to evaluate the performance of the agent.
- **Evals in prod** — measuring the end results of the agent in production, then creating a quantitative measure of performance.

### System prompt customization

The system prompt is the developer's primary tool in controlling an agent's behavior, so it’s often useful to customize the system prompt and see how performance changes.

Here's an SQL generation application which textures on creating evals to quantify SQL query generation success rates.

#### Code Example

```python
# sql_app.py
import json
from pathlib import Path
from typing import Union

from pydantic_ai import Agent, RunContext
from fake_database import DatabaseConn


class SqlSystemPrompt:
    def __init__(
        self, examples: Union[list[dict[str, str]], None] = None, db: str = 'PostgreSQL'
    ):
        if examples is None:
            # If examples aren't provided, load them from file, this is the default
            with Path('examples.json').open('rb') as f:
                self.examples = json.load(f)
        else:
            self.examples = examples
        self.db = db

    def build_prompt(self) -> str:  # The build_prompt method constructs the system prompt from the examples and the database type.
        return f"""
Given the following {self.db} table of records, your job is to
write a SQL query that suits the user's request.

Database schema:
CREATE TABLE records (
  ...
);

{''.join(self.format_example(example) for example in self.examples)}
"""

    @staticmethod
    def format_example(example: dict[str, str]) -> str:
        return f"""
<example>
  <request>{example['request']}</request>
  <sql>{example['sql']}</sql>
</example>
"""


sql_agent = Agent(
    'gemini-1.5-flash',
    deps_type=SqlSystemPrompt,
)


@sql_agent.system_prompt
async def system_prompt(ctx: RunContext[SqlSystemPrompt]) -> str:
    return ctx.deps.build_prompt()


async def user_search(user_prompt: str) -> list[dict[str, str]]:
    """Search the database based on the user's prompts."""
    ...
    result = await sql_agent.run(user_prompt, deps=SqlSystemPrompt())
    conn = DatabaseConn()
    return await conn.execute(result.data)
```

```json
// examples.json
{
  "examples": [
    {
      "request": "Show me all records",
      "sql": "SELECT * FROM records;"
    },
    {
      "request": "Show me all records from 2021",
      "sql": "SELECT * FROM records WHERE date_trunc('year', date) = '2021-01-01';"
    },
    {
      "request": "show me error records with the tag 'foobar'",
      "sql": "SELECT * FROM records WHERE level = 'error' and 'foobar' = ANY(tags);"
    }
    ...
  ]
}
```

Evals use classes to test the system prompt against various examples, quantifying success rates through scoring.

```python
# sql_app_evals.py
import json
import statistics
from pathlib import Path
from itertools import chain

from fake_database import DatabaseConn, QueryError
from sql_app import sql_agent, SqlSystemPrompt, user_search


async def main():
    with Path('examples.json').open('rb') as f:
        examples = json.load(f)

    # Split examples into 5 folds
    fold_size = len(examples) // 5
    folds = [examples[i : i + fold_size] for i in range(0, len(examples), fold_size)]
    conn = DatabaseConn()
    scores = []

    for i, fold in enumerate(folds, start=1):
        fold_score = 0
        # Build all other folds into a list of examples
        other_folds = list(chain(*(f for j, f in enumerate(folds) if j != i)))
        # Create a new system prompt with the other fold examples
        system_prompt = SqlSystemPrompt(examples=other_folds)

        # Override the system prompt with the new one
        with sql_agent.override(deps=system_prompt):
            for case in fold:
                try:
                    agent_results = await user_search(case['request'])
                except QueryError as e:
                    print(f'Fold {i} {case}: {e}')
                    fold_score -= 100
                else:
                    # Get the expected results using the SQL from this case
                    expected_results = await conn.execute(case['sql'])

                agent_ids = [r['id'] for r in agent_results]
                # Each returned value has a score of -1
                fold_score -= len(agent_ids)
                expected_ids = {r['id'] for r in expected_results}

                # Each return value that matches the expected value has a score of 5
                fold_score += 5 * len(set(agent_ids) & expected_ids)

        scores.append(fold_score)

    overall_score = statistics.mean(scores)
    print(f'Overall score: {overall_score:0.2f}')
    #> Overall score: 12.00
```

We learn how system prompt customization and eval strategies can quantify a model's performance succinctly, enhancing app development and optimization continuity.# Debugging and Monitoring - PydanticAI

Applications that use LLMs have some challenges that are well known and understood: LLMs are **slow**, **unreliable**, and **expensive**.

These applications also have some challenges that most developers have encountered much less often: LLMs are **fickle** and **non-deterministic**. Subtle changes in a prompt can completely change a model's performance, and there's no `EXPLAIN` query you can run to understand why.

> **Warning**
> 
> From a software engineer's point of view, you can think of LLMs as the worst database you've ever heard of, but worse. If LLMs weren't so bloody useful, we'd never touch them.

To build successful applications with LLMs, we need new tools to understand both model performance and the behavior of applications that rely on them. LLM observability tools that just let you understand how your model is performing are useless: making API calls to an LLM is easy, it's building that into an application that's hard.

## Pydantic Logfire

[Pydantic Logfire](https://pydantic.dev/logfire) is an observability platform developed by the team who created and maintain Pydantic and PydanticAI. Logfire aims to let you understand your entire application: Gen AI, classic predictive AI, HTTP traffic, database queries, and everything else a modern application needs.

> **Tip**
> 
> Pydantic Logfire is a commercial product. Logfire is a commercially supported, hosted platform with an extremely generous and perpetual [free tier](https://pydantic.dev/pricing/). You can sign up and start using Logfire in a couple of minutes.

PydanticAI has built-in (but optional) support for Logfire via the [`logfire-api`](https://github.com/pydantic/logfire/tree/main/logfire-api) no-op package. That means if the `logfire` package is installed and configured, detailed information about agent runs is sent to Logfire. But if the `logfire` package is not installed, there's virtually no overhead and nothing is sent.

Here's an example showing details of running the [Weather Agent](../examples/weather-agent/) in Logfire:

![Weather Agent Logfire](../img/logfire-weather-agent.png)

## Using Logfire

To use logfire, you'll need a logfire [account](https://logfire.pydantic.dev), and logfire installed:

### pip

```bash
pip install 'pydantic-ai[logfire]'
```

### uv

```bash
uv add 'pydantic-ai[logfire]'
```

Then authenticate your local environment with logfire:

### pip

```bash
logfire auth
```

### uv

```bash
uv run logfire auth
```

And configure a project to send data to:

### pip

```bash
logfire projects new
```

### uv

```bash
uv run logfire projects new
```

(Or use an existing project with `logfire projects use`)

The last step is to add logfire to your code:

```python
import logfire

logfire.configure()
```

The [logfire documentation](https://logfire.pydantic.dev/docs/) has more details on how to use logfire, including how to instrument other libraries like Pydantic, HTTPX, and FastAPI.

Since Logfire is built on [OpenTelemetry](https://opentelemetry.io/), you can use the Logfire Python SDK to send data to any OpenTelemetry collector.

Once you have logfire set up, there are two primary ways it can help you understand your application:

- **Debugging** — Using the live view to see what's happening in your application in real-time.
- **Monitoring** — Using SQL and dashboards to observe the behavior of your application. Logfire is effectively a SQL database that stores information about how your application is running.

### Debugging

To demonstrate how Logfire can let you visualize the flow of a PydanticAI run, here's the view you get from Logfire while running the [chat app examples](../examples/chat-app/):

<iframe src="https://customer-nmegqx24430okhaq.cloudflarestream.com/a764aff5840534dc77eba7d028707bfa/iframe?poster=https%3A%2F%2Fcustomer-nmegqx24430okhaq.cloudflarestream.com%2Fa764aff5840534dc77eba7d028707bfa%2Fthumbnails%2Fthumbnail.jpg%3Ftime%3D25s%26height%3D600" loading="lazy" style="border: none; position: absolute; top: 0; left: 0; height: 100%; width: 100%;" allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;" allowfullscreen="true"></iframe>

### Monitoring Performance

We can also query data with SQL in Logfire to monitor the performance of an application. Here's a real-world example of using Logfire to monitor PydanticAI runs inside Logfire itself:

![Logfire monitoring PydanticAI](../img/logfire-monitoring-pydanticai.png)# Multi-agent Applications

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

- [Flight booking](../examples/flight-booking/)# Chat App with FastAPI - PydanticAI

A simple chat app example built with FastAPI.

## Demonstrates:
- [Reusing chat history](../../message-history/)
- [Serializing messages](../../message-history/#accessing-messages-from-results)
- [Streaming responses](../../results/#streamed-results)

This demonstrates storing chat history between requests and using it to give the model context for new responses. Most of the complex logic here is between `chat_app.py` which streams the response to the browser, and `chat_app.ts` which renders messages in the browser.

## Running the Example

With [dependencies installed and environment variables set](../#usage), run:

### Using pip

```bash
python -m pydantic_ai_examples.chat_app
```

### Using uv

```bash
uv run -m pydantic_ai_examples.chat_app
```

Then open the app at [localhost:8000](http://localhost:8000).

![Example conversation](../../img/chat-app-example.png)

## Example Code

### Python Code (`chat_app.py`)

```python
from __future__ import annotations as _annotations

import asyncio
import json
import sqlite3
from collections.abc import AsyncIterator
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from typing import Annotated, Any, Callable, Literal, TypeVar

import fastapi
import logfire
from fastapi import Depends, Request
from fastapi.responses import FileResponse, Response, StreamingResponse
from typing_extensions import LiteralString, ParamSpec, TypedDict

from pydantic_ai import Agent
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)

# Logfire configuration
logfire.configure(send_to_logfire='if-token-present')

agent = Agent('openai:gpt-4o')
THIS_DIR = Path(__file__).parent

@asynccontextmanager
async def lifespan(_app: fastapi.FastAPI):
    async with Database.connect() as db:
        yield {'db': db}

app = fastapi.FastAPI(lifespan=lifespan)
logfire.instrument_fastapi(app)

@app.get('/')
async def index() -> FileResponse:
    return FileResponse((THIS_DIR / 'chat_app.html'), media_type='text/html')

@app.get('/chat_app.ts')
async def main_ts() -> FileResponse:
    """Get the raw typescript code, it's compiled in the browser, forgive me."""
    return FileResponse((THIS_DIR / 'chat_app.ts'), media_type='text/plain')

async def get_db(request: Request) -> Database:
    return request.state.db

@app.get('/chat/')
async def get_chat(database: Database = Depends(get_db)) -> Response:
    msgs = await database.get_messages()
    return Response(
        b'\n'.join(json.dumps(to_chat_message(m)).encode('utf-8') for m in msgs),
        media_type='text/plain',
    )

class ChatMessage(TypedDict):
    """Format of messages sent to the browser."""
    role: Literal['user', 'model']
    timestamp: str
    content: str

def to_chat_message(m: ModelMessage) -> ChatMessage:
    first_part = m.parts[0]
    if isinstance(m, ModelRequest):
        if isinstance(first_part, UserPromptPart):
            return {
                'role': 'user',
                'timestamp': first_part.timestamp.isoformat(),
                'content': first_part.content,
            }
    elif isinstance(m, ModelResponse):
        if isinstance(first_part, TextPart):
            return {
                'role': 'model',
                'timestamp': m.timestamp.isoformat(),
                'content': first_part.content,
            }
    raise UnexpectedModelBehavior(f'Unexpected message type for chat app: {m}')

@app.post('/chat/')
async def post_chat(
    prompt: Annotated[str, fastapi.Form()], database: Database = Depends(get_db)
) -> StreamingResponse:
    async def stream_messages():
        """Streams new line delimited JSON `Message`s to the client."""
        # Stream the user prompt so that can be displayed straight away
        yield (
            json.dumps({
                'role': 'user',
                'timestamp': datetime.now(tz=timezone.utc).isoformat(),
                'content': prompt,
            }).encode('utf-8')
            + b'\n'
        )
        # Get the chat history so far to pass as context to the agent
        messages = await database.get_messages()
        # Run the agent with the user prompt and the chat history
        async with agent.run_stream(prompt, message_history=messages) as result:
            async for text in result.stream(debounce_by=0.01):
                m = ModelResponse.from_text(content=text, timestamp=result.timestamp())
                yield json.dumps(to_chat_message(m)).encode('utf-8') + b'\n'
        # Add new messages (e.g. the user prompt and the agent response in this case) to the database
        await database.add_messages(result.new_messages_json())

    return StreamingResponse(stream_messages(), media_type='text/plain')

P = ParamSpec('P')
R = TypeVar('R')

@dataclass
class Database:
    """Rudimentary database to store chat messages in SQLite."""

    con: sqlite3.Connection
    _loop: asyncio.AbstractEventLoop
    _executor: ThreadPoolExecutor

    @classmethod
    @asynccontextmanager
    async def connect(cls, file: Path = THIS_DIR / '.chat_app_messages.sqlite') -> AsyncIterator[Database]:
        with logfire.span('connect to DB'):
            loop = asyncio.get_event_loop()
            executor = ThreadPoolExecutor(max_workers=1)
            con = await loop.run_in_executor(executor, cls._connect, file)
            slf = cls(con, loop, executor)
        try:
            yield slf
        finally:
            await slf._asyncify(con.close)

    @staticmethod
    def _connect(file: Path) -> sqlite3.Connection:
        con = sqlite3.connect(str(file))
        con = logfire.instrument_sqlite3(con)
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS messages (id INT PRIMARY KEY, message_list TEXT);')
        con.commit()
        return con

    async def add_messages(self, messages: bytes):
        await self._asyncify(
            self._execute,
            'INSERT INTO messages (message_list) VALUES (?);',
            messages,
            commit=True,
        )
        await self._asyncify(self.con.commit)

    async def get_messages(self) -> list[ModelMessage]:
        c = await self._asyncify(
            self._execute, 'SELECT message_list FROM messages order by id'
        )
        rows = await self._asyncify(c.fetchall)
        messages: list[ModelMessage] = []
        for row in rows:
            messages.extend(ModelMessagesTypeAdapter.validate_json(row[0]))
        return messages

    def _execute(self, sql: LiteralString, *args: Any, commit: bool = False) -> sqlite3.Cursor:
        cur = self.con.cursor()
        cur.execute(sql, args)
        if commit:
            self.con.commit()
        return cur

    async def _asyncify(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        return await self._loop.run_in_executor(
            self._executor,
            partial(func, **kwargs),
            *args,
        )

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        'pydantic_ai_examples.chat_app:app', reload=True, reload_dirs=[str(THIS_DIR)]
    )
```

### HTML Page (`chat_app.html`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chat App</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    main {
      max-width: 700px;
    }
    #conversation .user::before {
      content: 'You asked: ';
      font-weight: bold;
      display: block;
    }
    #conversation .model::before {
      content: 'AI Response: ';
      font-weight: bold;
      display: block;
    }
    #spinner {
      opacity: 0;
      transition: opacity 500ms ease-in;
      width: 30px;
      height: 30px;
      border: 3px solid #222;
      border-bottom-color: transparent;
      border-radius: 50%;
      animation: rotation 1s linear infinite;
    }
    @keyframes rotation {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    #spinner.active {
      opacity: 1;
    }
  </style>
</head>
<body>
  <main class="border rounded mx-auto my-5 p-4">
    <h1>Chat App</h1>
    <p>Ask me anything...</p>
    <div id="conversation" class="px-2"></div>
    <div class="d-flex justify-content-center mb-3">
      <div id="spinner"></div>
    </div>
    <form method="post">
      <input id="prompt-input" name="prompt" class="form-control"/>
      <div class="d-flex justify-content-end">
        <button class="btn btn-primary mt-2">Send</button>
      </div>
    </form>
    <div id="error" class="d-none text-danger">
      Error occurred, check the browser developer console for more information.
    </div>
  </main>
</body>
</html>
<script src="https://cdnjs.cloudflare.com/ajax/libs/typescript/5.6.3/typescript.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script type="module">
  // To let me write TypeScript, without adding the burden of npm we do a dirty, non-production-ready hack
  // and transpile the TypeScript code in the browser
  // This is (arguably) a neat demo trick, but not suitable for production!
  async function loadTs() {
    const response = await fetch('/chat_app.ts');
    const tsCode = await response.text();
    const jsCode = window.ts.transpile(tsCode, { target: "es2015" });
    let script = document.createElement('script');
    script.type = 'module';
    script.text = jsCode;
    document.body.appendChild(script);
  }

  loadTs().catch((e) => {
    console.error(e);
    document.getElementById('error').classList.remove('d-none');
    document.getElementById('spinner').classList.remove('active');
  });
</script>
```

### TypeScript File (`chat_app.ts`)

```typescript
// BIG FAT WARNING: To avoid the complexity of npm, this typescript is compiled in the browser
// there's currently no static type checking

import { marked } from 'https://cdnjs.cloudflare.com/ajax/libs/marked/15.0.0/lib/marked.esm.js'
const convElement = document.getElementById('conversation')

const promptInput = document.getElementById('prompt-input') as HTMLInputElement
const spinner = document.getElementById('spinner')

// Stream the response and render messages as each chunk is received
// Data is sent as newline-delimited JSON
async function onFetchResponse(response: Response): Promise<void> {
  let text = ''
  let decoder = new TextDecoder()
  if (response.ok) {
    const reader = response.body.getReader()
    while (true) {
      const {done, value} = await reader.read()
      if (done) {
        break
      }
      text += decoder.decode(value)
      addMessages(text)
      spinner.classList.remove('active')
    }
    addMessages(text)
    promptInput.disabled = false
    promptInput.focus()
  } else {
    const text = await response.text()
    console.error(`Unexpected response: ${response.status}`, {response, text})
    throw new Error(`Unexpected response: ${response.status}`)
  }
}

// The format of messages, this matches pydantic-ai both for brevity and understanding
// In production, you might not want to keep this format all the way to the frontend
interface Message {
  role: string
  content: string
  timestamp: string
}

// Take raw response text and render messages into the `#conversation` element
// Message timestamp is assumed to be a unique identifier of a message, and is used to deduplicate
// Hence you can send data about the same message multiple times, and it will be updated
// instead of creating a new message elements
function addMessages(responseText: string) {
  const lines = responseText.split('\n')
  const messages: Message[] = lines.filter(line => line.length > 1).map(j => JSON.parse(j))
  for (const message of messages) {
    // We use the timestamp as a crude element id
    const {timestamp, role, content} = message
    const id = `msg-${timestamp}`
    let msgDiv = document.getElementById(id)
    if (!msgDiv) {
      msgDiv = document.createElement('div')
      msgDiv.id = id
      msgDiv.title = `${role} at ${timestamp}`
      msgDiv.classList.add('border-top', 'pt-2', role)
      convElement.appendChild(msgDiv)
    }
    msgDiv.innerHTML = marked.parse(content)
  }
  window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
}

function onError(error: any) {
  console.error(error)
  document.getElementById('error').classList.remove('d-none')
  document.getElementById('spinner').classList.remove('active')
}

async function onSubmit(e: SubmitEvent): Promise<void> {
  e.preventDefault()
  spinner.classList.add('active')
  const body = new FormData(e.target as HTMLFormElement)

  promptInput.value = ''
  promptInput.disabled = true

  const response = await fetch('/chat/', {method: 'POST', body})
  await onFetchResponse(response)
}

// Call onSubmit when the form is submitted (e.g. user clicks the send button or hits Enter)
document.querySelector('form').addEventListener('submit', (e) => onSubmit(e).catch(onError))

// Load messages on page load
fetch('/chat/').then(onFetchResponse).catch(onError)
```
</example-code>
```

```md
# Agents

Agents are PydanticAI's primary interface for interacting with LLMs.

In some use cases a single Agent will control an entire application or component, but multiple agents can also interact to embody more complex workflows.

The Agent class has full API documentation, but conceptually you can think of an agent as a container for:

## Component	Description
- System prompt(s)	A set of instructions for the LLM written by the developer.
- Function tool(s)	Functions that the LLM may call to get information while generating a response.
- Structured result type	The structured datatype the LLM must return at the end of a run, if specified.
- Dependency type constraint	System prompt functions, tools, and result validators may all use dependencies when they're run.
- LLM model	Optional default LLM model associated with the agent. Can also be specified when running the agent.
- Model Settings	Optional default model settings to help fine tune requests. Can also be specified when running the agent.

In typing terms, agents are generic in their dependency and result types, e.g., an agent which required dependencies of type Foobar and returned results of type list[str] would have type Agent[Foobar, list[str]]. In practice, you shouldn't need to care about this, it should just mean your IDE can tell you when you have the right type, and if you choose to use static type checking it should work well with PydanticAI.

Agents are designed for reuse, like FastAPI Apps

Agents are intended to be instantiated once (frequently as module globals) and reused throughout your application, similar to a small FastAPI app or an APIRouter.
```

```python
"""Here's a toy example of an agent that simulates a roulette wheel:"""

from pydantic_ai import Agent, RunContext

roulette_agent = Agent(  
    'openai:gpt-4o',
    deps_type=int,
    result_type=bool,
    system_prompt=(
        'Use the `roulette_wheel` function to see if the '
        'customer has won based on the number they provide.'
    ),
)


@roulette_agent.tool
async def roulette_wheel(ctx: RunContext[int], square: int) -> str:  
    """check if the square is a winner"""
    return 'winner' if square == ctx.deps else 'loser'


# Run the agent
success_number = 18  
result = roulette_agent.run_sync('Put my money on square eighteen', deps=success_number)
print(result.data)  
#> True

result = roulette_agent.run_sync('I bet five is the winner', deps=success_number)
print(result.data)
#> False

```md
### Running Agents
There are three ways to run an agent:

- `agent.run()` — a coroutine which returns a RunResult containing a completed response
- `agent.run_sync()` — a plain, synchronous function which returns a RunResult containing a completed response (internally, this just calls loop.run_until_complete(self.run()))
- `agent.run_stream()` — a coroutine which returns a StreamedRunResult, which contains methods to stream a response as an async iterable
```

```python
"""Here's a simple example demonstrating all three:"""
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o')

result_sync = agent.run_sync('What is the capital of Italy?')
print(result_sync.data)
#> Rome


async def main():
    result = await agent.run('What is the capital of France?')
    print(result.data)
    #> Paris

    async with agent.run_stream('What is the capital of the UK?') as response:
        print(await response.get_data())
        #> London

"""
(This example is complete, it can be run "as is" — you'll need to add asyncio.run(main()) to run main)
You can also pass messages from previous runs to continue a conversation or provide context, as described in Messages and Chat History.
"""
```

```python
"""
Additional Configuration
Usage Limits
PydanticAI offers a UsageLimits structure to help you limit your usage (tokens and/or requests) on model runs.

You can apply these settings by passing the usage_limits argument to the run{_sync,_stream} functions.

Consider the following example, where we limit the number of response tokens:
"""
from pydantic_ai import Agent
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.usage import UsageLimits

agent = Agent('claude-3-5-sonnet-latest')

result_sync = agent.run_sync(
    'What is the capital of Italy? Answer with just the city.',
    usage_limits=UsageLimits(response_tokens_limit=10),
)
print(result_sync.data)
#> Rome
print(result_sync.usage())
"""
Usage(requests=1, request_tokens=62, response_tokens=1, total_tokens=63, details=None)
"""

try:
    result_sync = agent.run_sync(
        'What is the capital of Italy? Answer with a paragraph.',
        usage_limits=UsageLimits(response_tokens_limit=10),
    )
except UsageLimitExceeded as e:
    print(e)
    #> Exceeded the response_tokens_limit of 10 (response_tokens=32)

```

```python
"""
Restricting the number of requests can be useful in preventing infinite loops or excessive tool calling:
"""
from typing_extensions import TypedDict

from pydantic_ai import Agent, ModelRetry
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.usage import UsageLimits


class NeverResultType(TypedDict):
    """
    Never ever coerce data to this type.
    """

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
    #> The next request would exceed the request_limit of 3
```

```python
"""Model (Run) Settings
PydanticAI offers a settings.ModelSettings structure to help you fine tune your requests. This structure allows you to configure common parameters that influence the model's behavior, such as temperature, max_tokens, timeout, and more.

There are two ways to apply these settings: 1. Passing to run{_sync,_stream} functions via the model_settings argument. This allows for fine-tuning on a per-request basis. 2. Setting during Agent initialization via the model_settings argument. These settings will be applied by default to all subsequent run calls using said agent. However, model_settings provided during a specific run call will override the agent's default settings.

For example, if you'd like to set the temperature setting to 0.0 to ensure less random behavior, you can do the following:
"""

from pydantic_ai import Agent

agent = Agent('openai:gpt-4o')

result_sync = agent.run_sync(
    'What is the capital of Italy?', model_settings={'temperature': 0.0}
)
print(result_sync.data)
#> Rome

```

```python
"""Runs vs. Conversations
An agent run might represent an entire conversation — there's no limit to how many messages can be exchanged in a single run. However, a conversation might also be composed of multiple runs, especially if you need to maintain state between separate interactions or API calls.

Here's an example of a conversation comprised of multiple runs:
"""

from pydantic_ai import Agent

agent = Agent('openai:gpt-4o')

# First run
result1 = agent.run_sync('Who was Albert Einstein?')
print(result1.data)
#> Albert Einstein was a German-born theoretical physicist.

# Second run, passing previous messages
result2 = agent.run_sync(
    'What was his most famous equation?',
    message_history=result1.new_messages(),  
)
print(result2.data)
#> Albert Einstein's most famous equation is (E = mc^2).

```

```python
"""Type safe by design
PydanticAI is designed to work well with static type checkers, like mypy and pyright.

In particular, agents are generic in both the type of their dependencies and the type of results they return, so you can use the type hints to ensure you're using the right types.

Consider the following script with type mistakes:
"""
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext


@dataclass
class User:
    name: str


agent = Agent(
    'test',
    deps_type=User,  
    result_type=bool,
)


@agent.system_prompt
def add_user_name(ctx: RunContext[str]) -> str:  
    return f"The user's name is {ctx.deps}."


def foobar(x: bytes) -> None:
    pass


result = agent.run_sync('Does their name start with "A"?', deps=User('Anne'))
foobar(result.data)

"""
Running mypy on this will give the following output: (Running pyright would identify the same issues.)
"""
```

```bash
➤ uv run mypy type_mistakes.py
type_mistakes.py:18: error: Argument 1 to "system_prompt" of "Agent" has incompatible type "Callable[[RunContext[str]], str]"; expected "Callable[[RunContext[User]], str]"  [arg-type]
type_mistakes.py:28: error: Argument 1 to "foobar" has incompatible type "bool"; expected "bytes"  [arg-type]
Found 2 errors in 1 file (checked 1 source file)
```


```python
"""
System Prompts
System prompts might seem simple at first glance since they're just strings (or sequences of strings that are concatenated), but crafting the right system prompt is key to getting the model to behave as you want.

Generally, system prompts fall into two categories:

Static system prompts: These are known when writing the code and can be defined via the system_prompt parameter of the Agent constructor.
Dynamic system prompts: These depend in some way on context that isn't known until runtime, and should be defined via functions decorated with @agent.system_prompt.
You can add both to a single agent; they're appended in the order they're defined at runtime.

Here's an example using both types of system prompts:
"""
from datetime import date

from pydantic_ai import Agent, RunContext

agent = Agent(
    'openai:gpt-4o',
    deps_type=str,  
    system_prompt="Use the customer's name while replying to them.",  
)


@agent.system_prompt  
def add_the_users_name(ctx: RunContext[str]) -> str:
    return f"The user's name is {ctx.deps}."


@agent.system_prompt
def add_the_date() -> str:  
    return f'The date is {date.today()}.'


result = agent.run_sync('What is the date?', deps='Frank')
print(result.data)
#> Hello Frank, the date today is 2032-01-02.

```

```python
"""
Reflection and self-correction
Validation errors from both function tool parameter validation and structured result validation can be passed back to the model with a request to retry.

You can also raise ModelRetry from within a tool or result validator function to tell the model it should retry generating a response.

The default retry count is 1 but can be altered for the entire agent, a specific tool, or a result validator.
You can access the current retry count from within a tool or result validator via ctx.retry.
Here's an example:
"""

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
    print(name)
    #> John
    #> John Doe
    user_id = ctx.deps.users.get(name=name)
    if user_id is None:
        raise ModelRetry(
            f'No user found with name {name!r}, remember to provide their full name'
        )
    return user_id


result = agent.run_sync(
    'Send a message to John Doe asking for coffee next week', deps=DatabaseConn()
)
print(result.data)
"""
user_id=123 message='Hello John, would you be free for coffee sometime next week? Let me know what works for you!'
"""

```

```python
"""
Model errors
If models behave unexpectedly (e.g., the retry limit is exceeded, or their API returns 503), agent runs will raise UnexpectedModelBehavior.

In these cases, capture_run_messages can be used to access the messages exchanged during the run to help diagnose the issue.
"""

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
        #> An error occurred: Tool exceeded max retries count of 1
        print('cause:', repr(e.__cause__))
        #> cause: ModelRetry('Please try again.')
        print('messages:', messages)
        """
        messages:
        [
            ModelRequest(
                parts=[
                    UserPromptPart(
                        content='Please get me the volume of a box with size 6.',
                        timestamp=datetime.datetime(...),
                        part_kind='user-prompt',
                    )
                ],
                kind='request',
            ),
            ModelResponse(
                parts=[
                    ToolCallPart(
                        tool_name='calc_volume',
                        args=ArgsDict(args_dict={'size': 6}),
                        tool_call_id=None,
                        part_kind='tool-call',
                    )
                ],
                timestamp=datetime.datetime(...),
                kind='response',
            ),
            ModelRequest(
                parts=[
                    RetryPromptPart(
                        content='Please try again.',
                        tool_name='calc_volume',
                        tool_call_id=None,
                        timestamp=datetime.datetime(...),
                        part_kind='retry-prompt',
                    )
                ],
                kind='request',
            ),
            ModelResponse(
                parts=[
                    ToolCallPart(
                        tool_name='calc_volume',
                        args=ArgsDict(args_dict={'size': 6}),
                        tool_call_id=None,
                        part_kind='tool-call',
                    )
                ],
                timestamp=datetime.datetime(...),
                kind='response',
            ),
        ]
        """
    else:
        print(result.data)
```

```python

```

## Context

### Beginning context
- [List of files that exist at start - what files exist at start?]

### Ending context  
- [List of files that will exist at end - what files will exist at end?]

## Low-Level Tasks
> Ordered from start to finish

1. [First task - what is the first task?]
```aider
What prompt would you run to complete this task?
What file do you want to CREATE or UPDATE?
What function do you want to CREATE or UPDATE?
What are details you want to add to drive the code changes?
```
2. [Second task - what is the second task?]
```aider
What prompt would you run to complete this task?
What file do you want to CREATE or UPDATE?
What function do you want to CREATE or UPDATE?
What are details you want to add to drive the code changes?
```
3. [Third task - what is the third task?]
```aider
What prompt would you run to complete this task?
What file do you want to CREATE or UPDATE?
What function do you want to CREATE or UPDATE?
What are details you want to add to drive the code changes?
```

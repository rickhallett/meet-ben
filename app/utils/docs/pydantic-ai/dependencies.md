# Dependencies - PydanticAI

PydanticAI uses a dependency injection system to provide data and services to your agent’s [system prompts](../agents/#system-prompts), [tools](../tools/), and [result validators](../results/#result-validators-functions).

Matching PydanticAI's design philosophy, our dependency system tries to use existing best practices in Python development rather than inventing esoteric "magic." This should make dependencies type-safe, easier to test, and easier to deploy in production.

## Defining Dependencies

Dependencies can be any Python type. While in simple cases you might be able to pass a single object as a dependency (e.g., an HTTP connection), [dataclasses](https://docs.python.org/3/library/dataclasses.html#module-dataclasses) are generally a convenient container when your dependencies include multiple objects.

Here’s an example of defining an agent that requires dependencies. (Note: dependencies aren't actually used in this example, see [Accessing Dependencies](#accessing-dependencies) below)

```python
from dataclasses import dataclass
import httpx
from pydantic_ai import Agent

@dataclass
class MyDeps:  # Define a dataclass to hold dependencies.
    api_key: str
    http_client: httpx.AsyncClient

agent = Agent(
    'openai:gpt-4o',
    deps_type=MyDeps,  # Pass the dataclass type to the `deps_type` argument of the `Agent` constructor.
)

async def main():
    async with httpx.AsyncClient() as client:
        deps = MyDeps('foobar', client)
        result = await agent.run(
            'Tell me a joke.',
            deps=deps,  # When running the agent, pass an instance of the dataclass to the `deps` parameter.
        )
        print(result.data)
        # > Did you hear about the toothpaste scandal? They called it Colgate.
```

*This example is complete, it can be run "as is" — you'll need to add `asyncio.run(main())` to run `main`.*

## Accessing Dependencies

Dependencies are accessed through the [RunContext](../api/tools/#pydantic_ai.tools.RunContext) type, this should be the first parameter of system prompt functions, etc.

```python
from dataclasses import dataclass
import httpx
from pydantic_ai import Agent, RunContext

@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.AsyncClient

agent = Agent(
    'openai:gpt-4o',
    deps_type=MyDeps,
)

@agent.system_prompt  # RunContext may optionally be passed to a system_prompt function as the only argument.
async def get_system_prompt(ctx: RunContext[MyDeps]) -> str:  # RunContext is parameterized with the type of the dependencies.
    response = await ctx.deps.http_client.get(  # Access dependencies through the .deps attribute.
        'https://example.com',
        headers={'Authorization': f'Bearer {ctx.deps.api_key}'},  # Access dependencies through the .deps attribute.
    )
    response.raise_for_status()
    return f'Prompt: {response.text}'

async def main():
    async with httpx.AsyncClient() as client:
        deps = MyDeps('foobar', client)
        result = await agent.run('Tell me a joke.', deps=deps)
        print(result.data)
        # > Did you hear about the toothpaste scandal? They called it Colgate.
```

*This example is complete, it can be run "as is" — you'll need to add `asyncio.run(main())` to run `main`.*

### Asynchronous vs. Synchronous dependencies

System prompt functions, [function tools](../tools/), and [result validators](../results/#result-validators-functions) are all run in the async context of an agent run.

If these functions are not coroutines (e.g., `async def`), they are called with [run_in_executor](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor) in a thread pool. It’s therefore marginally preferable to use `async` methods where dependencies perform IO, although synchronous dependencies should work fine, too.

> **Note**: Whether you use synchronous or asynchronous dependencies, is completely independent of whether you use `run` or `run_sync` — `run_sync` is just a wrapper around `run`, and agents are always run in an async context.

Here’s the same example as above, but with a synchronous dependency:

```python
from dataclasses import dataclass
import httpx
from pydantic_ai import Agent, RunContext

@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.Client  # Here we use a synchronous httpx.Client.

agent = Agent(
    'openai:gpt-4o',
    deps_type=MyDeps,
)

@agent.system_prompt
def get_system_prompt(ctx: RunContext[MyDeps]) -> str:  # The system prompt function is now a plain function.
    response = ctx.deps.http_client.get(
        'https://example.com', headers={'Authorization': f'Bearer {ctx.deps.api_key}'}
    )
    response.raise_for_status()
    return f'Prompt: {response.text}'

async def main():
    deps = MyDeps('foobar', httpx.Client())
    result = await agent.run(
        'Tell me a joke.',
        deps=deps,
    )
    print(result.data)
    # > Did you hear about the toothpaste scandal? They called it Colgate.
```

*This example is complete, it can be run "as is" — you'll need to add `asyncio.run(main())` to run `main`.*

## Full Example

As well as system prompts, dependencies can be used in [tools](../tools/) and [result validators](../results/#result-validators-functions).

```python
from dataclasses import dataclass
import httpx
from pydantic_ai import Agent, ModelRetry, RunContext

@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.AsyncClient

agent = Agent(
    'openai:gpt-4o',
    deps_type=MyDeps,
)

@agent.system_prompt
async def get_system_prompt(ctx: RunContext[MyDeps]) -> str:
    response = await ctx.deps.http_client.get('https://example.com')
    response.raise_for_status()
    return f'Prompt: {response.text}'

@agent.tool  # To pass RunContext to a tool, use the tool decorator.
async def get_joke_material(ctx: RunContext[MyDeps], subject: str) -> str:
    response = await ctx.deps.http_client.get(
        'https://example.com#jokes',
        params={'subject': subject},
        headers={'Authorization': f'Bearer {ctx.deps.api_key}'},
    )
    response.raise_for_status()
    return response.text

@agent.result_validator  # RunContext may optionally be passed to a result_validator function.
async def validate_result(ctx: RunContext[MyDeps], final_response: str) -> str:
    response = await ctx.deps.http_client.post(
        'https://example.com#validate',
        headers={'Authorization': f'Bearer {ctx.deps.api_key}'},
        params={'query': final_response},
    )
    if response.status_code == 400:
        raise ModelRetry(f'invalid response: {response.text}')
    response.raise_for_status()
    return final_response

async def main():
    async with httpx.AsyncClient() as client:
        deps = MyDeps('foobar', client)
        result = await agent.run('Tell me a joke.', deps=deps)
        print(result.data)
        # > Did you hear about the toothpaste scandal? They called it Colgate.
```

*This example is complete, it can be run "as is" — you'll need to add `asyncio.run(main())` to run `main`.*

## Overriding Dependencies

When testing agents, it's useful to be able to customize dependencies. While this can sometimes be done by calling the agent directly within unit tests, we can also override dependencies while calling application code which in turn calls the agent.

This is done via the [override](../api/agent/#pydantic_ai.agent.Agent.override) method on the agent.

```python
from dataclasses import dataclass
import httpx
from pydantic_ai import Agent, RunContext

@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.AsyncClient

    async def system_prompt_factory(self) -> str:  # Define a method on the dependency to make the system prompt easier to customize.
        response = await self.http_client.get('https://example.com')
        response.raise_for_status()
        return f'Prompt: {response.text}'

joke_agent = Agent('openai:gpt-4o', deps_type=MyDeps)

@joke_agent.system_prompt
async def get_system_prompt(ctx: RunContext[MyDeps]) -> str:
    return await ctx.deps.system_prompt_factory()  # Call the system prompt factory from within the system prompt function.

async def application_code(prompt: str) -> str:  # Application code that calls the agent, in a real application this might be an API endpoint.
    ...
    ...
    # Now deep within application code we call our agent
    async with httpx.AsyncClient() as client:
        app_deps = MyDeps('foobar', client)
        result = await joke_agent.run(prompt, deps=app_deps)  # Call the agent from within the application code.
    return result.data
```

*This example is complete, it can be run "as is".*

```python
from joke_app import MyDeps, application_code, joke_agent

class TestMyDeps(MyDeps):  # Define a subclass of MyDeps in tests.
    async def system_prompt_factory(self) -> str:
        return 'test prompt'

async def test_application_code():
    test_deps = TestMyDeps('test_key', None)  # Create an instance of the test dependency.
    with joke_agent.override(deps=test_deps):  # Override the dependencies of the agent for the duration of the "with" block.
        joke = await application_code('Tell me a joke.')  # Call application code, the agent will use the overridden dependencies.
    assert joke.startswith('Did you hear about the toothpaste scandal?')
```

## Examples

The following examples demonstrate how to use dependencies in PydanticAI:

- [Weather Agent](../examples/weather-agent/)
- [SQL Generation](../examples/sql-gen/)
- [RAG](../examples/rag/)
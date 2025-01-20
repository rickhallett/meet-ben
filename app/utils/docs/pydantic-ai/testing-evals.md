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

We learn how system prompt customization and eval strategies can quantify a model's performance succinctly, enhancing app development and optimization continuity.
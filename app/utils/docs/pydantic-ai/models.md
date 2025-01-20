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

Refer to the [contributing guidelines](../contributing/#new-model-rules) for more information.
# Development Workflow

The GenAI Launchpad is designed to provide a structured path from initial setup to a fully functional AI application. This guide will walk you through the process of transforming the boilerplate into your custom application, with detailed explanations of each step and best practices to follow.

## Getting Started with the Boilerplate

Begin by cloning the boilerplate branch, which provides a clean foundation for your project:

```bash
git clone -b boilerplate https://github.com/datalumina/genai-launchpad.git
cd genai-launchpad
```

The boilerplate branch contains the core infrastructure without any specific business logic, allowing you to build your application from a clean slate while benefiting from the robust architectural foundation.

## Environment Configuration

The first step in customizing your application is setting up the environment configuration. This involves creating and configuring two essential .env files:

```bash
cp app/.env.example app/.env
cp docker/.env.example docker/.env
```

In your `app/.env` file, you'll need to add your AI provider credentials. At minimum, you should configure:

- OPENAI_API_KEY for OpenAI integration
- ANTHROPIC_API_KEY if you plan to use Claude
- Any other provider-specific keys your application requires

The `docker/.env` file contains infrastructure configurations. While the defaults work well for development, you should update:

- Database credentials for security
- Domain settings if deploying to production
- Any service-specific configurations

## Defining Your Application's Events

Events are the core building blocks of your application's functionality. Start by defining your events in the requests/events directory. Each event should be a JSON file that represents a specific interaction or process in your system. For example:

```json
{
    "type": "document_analysis",
    "data": {
        "content": "Document text here...",
        "analysis_type": "sentiment",
        "metadata": {
            "source": "email",
            "priority": "high"
        }
    }
}
```

These event definitions serve as both documentation and test fixtures for your application.

## Schema Definition

Once you've defined your events, create corresponding schemas in `app/api/event_schema.py`. These Pydantic models will validate incoming requests and provide type safety throughout your application:

```python
class DocumentAnalysisEvent(BaseModel):
    content: str
    analysis_type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

The schema definitions are crucial as they form the contract between your API and its clients, ensuring data consistency and providing automatic API documentation.

## Building Your AI Pipelines

With your events and schemas defined, you can begin creating the pipelines that will process these events. In `app/pipelines/`, create a new directory for each major functionality area. Each pipeline should be composed of focused, reusable nodes that handle specific aspects of processing.

For example, a document analysis pipeline might include:

- Text extraction node
- Classification node
- Sentiment analysis node
- Response formatting node

## Vector Store Integration (Optional)

If your application requires semantic search or similarity matching capabilities, you'll need to populate your vector store. The `app/utils/insert_vectors.py` utility helps you add embeddings to the PostgreSQL database:

```python
python app/utils/insert_vectors.py
```

This step is particularly important for applications implementing RAG (Retrieval-Augmented Generation) patterns or semantic search functionality.

## Experimentation and Refinement

The playground directory is your laboratory for testing and refining your AI interactions. Use these scripts to:

- Test different prompt strategies
- Experiment with various LLM parameters
- Validate pipeline behaviors
- Measure performance and costs

The playground provides a fast feedback loop for developing and testing your AI components before integrating them into your main application flow.

## Testing and Validation

As you develop your application, maintain a comprehensive suite of test events in `requests/events/`. Use the testing utilities to validate your pipelines:

```python
from utils.event_factory import EventFactory
from pipelines.your_pipeline import YourPipeline

def test_pipeline():
    event = EventFactory.create_event("your_test_event")
    pipeline = YourPipeline()
    result = pipeline.run(event)
    assert result.nodes["AnalysisNode"]["status"] == "success"
```

## Iterative Development

Development with the GenAI Launchpad is an iterative process. Start with a minimal viable pipeline and gradually enhance it based on:

- Performance metrics
- User feedback
- Error patterns
- Cost considerations

The modular architecture allows you to refine individual components without affecting the rest of the system.

## Next Steps

Once you've completed the initial development:

- Set up monitoring and logging (we use LangFuse)
- Implement error handling strategies
- Configure production deployment
- Document your custom components

Remember that the GenAI Launchpad is designed to grow with your needs. Start simple and expand your implementation as your requirements evolve.

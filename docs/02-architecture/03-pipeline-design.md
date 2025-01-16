# Pipeline Design and Implementation

The pipeline system in GenAI Launchpad provides a structured way to implement AI workflows. This guide explains how to design, implement, and register pipelines for processing through the Celery worker system.

## Pipeline Architecture

### Registry System (registry.py)

The PipelineRegistry acts as a central hub for managing different pipeline implementations:

```python
class PipelineRegistry:
    pipelines: Dict[str, Type[Pipeline]] = {
        "support": CustomerSupportPipeline,
        "content": ContentAnalysisPipeline,
    }

    @staticmethod
    def get_pipeline_type(event: EventSchema) -> str:
        # Implement your routing logic
        if "support" in event.data.get("type"):
            return "support"
        return "content"
```

This registry:

- Maps event types to specific pipeline implementations
- Provides dynamic pipeline selection based on event attributes
- Enables easy addition of new pipeline types

## Creating Pipelines

### Basic Pipeline Structure

A typical pipeline consists of multiple nodes arranged in a DAG:

```python
class ContentAnalysisPipeline(Pipeline):
    pipeline_schema = PipelineSchema(
        description="Analyzes content using AI",
        start=ExtractNode,
        nodes=[
            NodeConfig(node=ExtractNode, connections=[AnalyzeNode]),
            NodeConfig(node=AnalyzeNode, connections=[RouterNode]),
            NodeConfig(
                node=RouterNode, 
                connections=[SummarizeNode, TranslateNode],
                is_router=True
            ),
            NodeConfig(node=SummarizeNode, connections=[FormatNode]),
            NodeConfig(node=TranslateNode, connections=[FormatNode]),
            NodeConfig(node=FormatNode, connections=[])
        ]
    )
```

### Node Types and Implementation

1. **Basic Processing Node**:
```python
class ExtractNode(Node):
    def process(self, context: TaskContext) -> TaskContext:
        # Extract text from input
        text = context.event.data.get("content")
        context.nodes[self.node_name] = {"extracted_text": text}
        return context
```

2. **LLM Node**:
```python
class AnalyzeNode(LLMNode):
    class ContextModel(BaseModel):
        text: str
        analysis_type: str

    class ResponseModel(BaseModel):
        sentiment: str
        key_points: List[str]

    def get_context(self, task_context: TaskContext) -> ContextModel:
        return self.ContextModel(
            text=task_context.nodes["ExtractNode"]["extracted_text"],
            analysis_type=task_context.event.data.get("analysis_type")
        )

    def create_completion(self, context: ContextModel) -> ResponseModel:
        llm = LLMFactory("openai")
        prompt = PromptManager.get_prompt(
            "extract",
            pipeline="support",
        )
        return llm.create_completion(
            response_model=self.ResponseModel,
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": f"# New data:\n{context.model_dump()}",
                },
            ],
        )

    def process(self, task_context: TaskContext) -> TaskContext:
        context = self.get_context(task_context)
        response = self.create_completion(context)
        task_context.nodes[self.node_name] = response
        return task_context
```

3. **Router Node**:
```python
class ContentRouter(BaseRouter):
    def __init__(self):
        self.routes = [
            SummaryRoute(),
            TranslationRoute()
        ]
        self.fallback = SummaryRoute()

class SummaryRoute(RouterNode):
    def determine_next_node(self, context: TaskContext) -> Optional[Node]:
        if context.event.data.get("action") == "summarize":
            return SummarizeNode()
        return None
```

## Worker Integration

The Celery worker (tasks.py) handles pipeline execution:

```python
@celery_app.task(name="process_incoming_event")
def process_incoming_event(event_id: str):
    with db_session() as session:
        # Get event from database
        event = repository.get(id=event_id)
        
        # Determine and execute pipeline
        pipeline = PipelineRegistry.get_pipeline(event)
        result = pipeline.run(event)
        
        # Store results
        event.task_context = result.model_dump()
        repository.update(event)
```

## Pipeline Design Best Practices

### 1. Node Granularity

Design nodes with single responsibilities:
```python
# Good: Focused node
class SentimentNode(LLMNode):
    def process(self, context: TaskContext) -> TaskContext:
        # Only handles sentiment analysis
        return context

# Avoid: Too many responsibilities
class AnalysisNode(LLMNode):
    def process(self, context: TaskContext) -> TaskContext:
        # Handles sentiment, entities, translation, etc.
        return context
```

### 2. Data Flow

Maintain clear data dependencies:
```python
class SummarizeNode(LLMNode):
    def get_context(self, task_context: TaskContext) -> ContextModel:
        # Clearly specify data requirements
        return self.ContextModel(
            text=task_context.nodes["ExtractNode"]["text"],
            style=task_context.nodes["AnalyzeNode"]["tone"]
        )
```

### 3. Router Placement

Place routers at decision points:
```python
pipeline_schema = PipelineSchema(
    start=ValidateNode,
    nodes=[
        NodeConfig(node=ValidateNode, connections=[RouterNode]),
        NodeConfig(
            node=RouterNode,
            connections=[ProcessA, ProcessB],
            is_router=True
        )
    ]
)
```

### 4. Error Handling

Implement robust error handling:
```python
class ProcessingNode(Node):
    def process(self, context: TaskContext) -> TaskContext:
        try:
            result = self.process_data(context)
            context.nodes[self.node_name] = {"status": "success", "data": result}
        except Exception as e:
            context.nodes[self.node_name] = {
                "status": "error",
                "error": str(e)
            }
        return context
```

## Pipeline Organization

Structure your pipelines folder:
```
pipelines/
├── __init__.py
├── registry.py
├── support/
│   ├── __init__.py
│   ├── nodes.py
│   └── pipeline.py
└── content/
    ├── __init__.py
    ├── nodes.py
    └── pipeline.py
```

## Testing Pipelines

Create comprehensive tests:
```python
def test_content_pipeline():
    # Create test event
    event = EventSchema(type="content_analysis", data={...})
    
    # Initialize pipeline
    pipeline = ContentAnalysisPipeline()
    
    # Run pipeline
    result = pipeline.run(event)
    
    # Assert expected results
    assert "AnalyzeNode" in result.nodes
    assert result.nodes["AnalyzeNode"]["sentiment"] == "positive"
```

Remember that well-designed pipelines are:

- Easy to understand
- Maintainable
- Testable
- Reusable
- Error-resistant

The pipeline system provides the structure - your implementation provides the intelligence.

## Pipeline Strategy: Single vs. Multiple

### When to Use a Single Pipeline

A single pipeline is often sufficient when:

1. **Common Processing Flow**: Your application handles variations of the same basic workflow:
```python
class ContentPipeline(Pipeline):
    pipeline_schema = PipelineSchema(
        start=ValidateNode,
        nodes=[
            NodeConfig(node=ValidateNode, connections=[RouterNode]),
            NodeConfig(
                node=RouterNode, 
                connections=[
                    TextAnalysisNode,
                    ImageAnalysisNode,
                    AudioAnalysisNode
                ],
                is_router=True
            ),
            # All paths converge to common processing
            NodeConfig(node=TextAnalysisNode, connections=[EnrichmentNode]),
            NodeConfig(node=ImageAnalysisNode, connections=[EnrichmentNode]),
            NodeConfig(node=AudioAnalysisNode, connections=[EnrichmentNode]),
            NodeConfig(node=EnrichmentNode, connections=[StorageNode]),
        ]
    )
```

2. **Branching Logic**: When differences can be handled through routing:
```python
class RouterNode(BaseRouter):
    def determine_next_node(self, context: TaskContext) -> Node:
        content_type = context.event.data.get("type")
        return {
            "text": TextAnalysisNode(),
            "image": ImageAnalysisNode(),
            "audio": AudioAnalysisNode()
        }.get(content_type, TextAnalysisNode())
```

3. **Shared Context**: When different processes need access to the same context:
```python
class EnrichmentNode(Node):
    def process(self, context: TaskContext) -> TaskContext:
        # Access results from any previous node
        analysis_results = context.nodes.get(
            f"{context.metadata['analysis_type']}AnalysisNode"
        )
        # Enrich with common logic
        return context
```

### When to Use Multiple Pipelines

Consider multiple pipelines when:

1. **Distinct Business Domains**:
```python
class CustomerSupportPipeline(Pipeline):
    # Handle customer inquiries
    pipeline_schema = PipelineSchema(...)

class ContentModerationPipeline(Pipeline):
    # Handle content moderation
    pipeline_schema = PipelineSchema(...)
```

2. **Different Security Requirements**:
```python
class PublicPipeline(Pipeline):
    # Public-facing processing
    pipeline_schema = PipelineSchema(...)

class InternalPipeline(Pipeline):
    # Internal, privileged processing
    pipeline_schema = PipelineSchema(...)
```

3. **Completely Different Workflows**:
```python
class DocumentProcessingPipeline(Pipeline):
    # Document-specific workflow
    pipeline_schema = PipelineSchema(
        nodes=[
            NodeConfig(node=OCRNode),
            NodeConfig(node=ClassificationNode),
            # ...
        ]
    )

class ChatPipeline(Pipeline):
    # Conversational workflow
    pipeline_schema = PipelineSchema(
        nodes=[
            NodeConfig(node=ContextNode),
            NodeConfig(node=ResponseNode),
            # ...
        ]
    )
```

### Hybrid Approach

You can also use a hybrid approach where you have multiple pipelines that share common components:

```python
# Shared nodes module
class CommonNodes:
    class ValidationNode(Node):
        def process(self, context: TaskContext) -> TaskContext:
            # Common validation logic
            return context

# Multiple pipelines using shared components
class Pipeline1(Pipeline):
    pipeline_schema = PipelineSchema(
        start=CommonNodes.ValidationNode,
        nodes=[
            NodeConfig(node=CommonNodes.ValidationNode),
            NodeConfig(node=CustomNode1)
        ]
    )

class Pipeline2(Pipeline):
    pipeline_schema = PipelineSchema(
        start=CommonNodes.ValidationNode,
        nodes=[
            NodeConfig(node=CommonNodes.ValidationNode),
            NodeConfig(node=CustomNode2)
        ]
    )
```

### Decision Framework

When deciding on pipeline structure, consider:

1. **Complexity Management**:
   - Single Pipeline: When variations are minimal
   - Multiple Pipelines: When complexity becomes hard to manage in one pipeline

2. **Maintenance**:
   - Single Pipeline: Easier to maintain when logic is related
   - Multiple Pipelines: Better when different teams manage different workflows

3. **Performance**:
   - Single Pipeline: Can optimize shared resources
   - Multiple Pipelines: Can scale different workflows independently

4. **Security**:
   - Single Pipeline: When security context is uniform
   - Multiple Pipelines: When different security contexts are needed

Remember: Start with a single pipeline and split only when necessary. It's easier to split a pipeline later than to combine multiple pipelines.
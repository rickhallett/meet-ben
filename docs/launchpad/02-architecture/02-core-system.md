# Core Pipeline System

The core system implements a sophisticated yet minimalist approach to workflow automation using directed acyclic graphs (DAGs) and the Chain of Responsibility pattern. This design draws inspiration from Make.com and similar workflow automation tools, but implements these concepts in pure Python with a focus on AI integration.

## Fundamental Philosophy

The system is built around three key principles:

1. **Directed Acyclic Flow**: All workflows are DAGs, preventing infinite loops and ensuring predictable execution paths. This design choice stems from practical experience with AI systems, where cyclic workflows can lead to agents getting stuck in loops.

2. **Chain of Responsibility**: Each processing step (node) handles its specific task and passes the context to the next node, maintaining clean separation of concerns while sharing state through a structured context object.

3. **Structured Data Flow**: A single, well-defined `TaskContext` object flows through the pipeline, ensuring consistent data access and state management across all processing steps.

## Core Components

### Base Node (base.py)

The foundation of the pipeline system is the Node class, which implements the Chain of Responsibility pattern:

```python
class Node(ABC):
    @abstractmethod
    def process(self, task_context: TaskContext) -> TaskContext:
        pass
```

Each node:

- Receives the task context from its predecessor
- Performs its specific processing
- Updates the context with its results
- Passes the context to its successor

### Task Context (task.py)

The TaskContext serves as the shared state container flowing through the pipeline:

```python
class TaskContext(BaseModel):
    event: EventSchema
    nodes: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

This design:

- Maintains the original event data
- Stores each node's processing results
- Provides structured access to pipeline state
- Enables data sharing between nodes

### Pipeline Orchestration (pipeline.py)

The Pipeline class orchestrates the flow of data through nodes:

```python
class Pipeline(ABC):
    pipeline_schema: ClassVar[PipelineSchema]

    def run(self, event: EventSchema) -> TaskContext:
        task_context = TaskContext(event=event, pipeline=self)
        current_node_class = self.pipeline_schema.start
        
        while current_node_class:
            current_node = self.nodes[current_node_class]
            task_context = current_node.process(task_context)
            current_node_class = self._get_next_node_class(
                current_node_class, task_context
            )
```

Key features:

- Validates pipeline structure at initialization
- Manages node execution sequence
- Handles routing decisions
- Provides error handling and logging

### LLM Integration (llm.py)

The LLMNode provides a structured approach to AI model integration:

```python
class LLMNode(Node, ABC):
    class ContextModel(BaseModel):
        pass

    class ResponseModel(BaseModel):
        pass

    @abstractmethod
    def create_completion(self, context: ContextModel) -> ResponseModel:
        pass

    @abstractmethod
    def get_context(self, task_context: TaskContext) -> ContextModel:
        pass
```

This design:

- Enforces structured input/output through Pydantic models
- Separates context preparation from model interaction
- Enables type-safe response handling
- Facilitates integration with the instructor library for structured outputs

### Routing Logic (router.py)

The routing system enables conditional workflow paths:

```python
class BaseRouter(Node):
    def route(self, task_context: TaskContext) -> Node:
        for route_node in self.routes:
            next_node = route_node.determine_next_node(task_context)
            if next_node:
                return next_node
        return self.fallback
```

Features:

- Conditional branching based on task context
- Multiple routing rules support
- Fallback handling
- Clear routing decision tracking

### Pipeline Schema (schema.py)

The schema system defines pipeline structure using Pydantic models:

```python
class PipelineSchema(BaseModel):
    description: Optional[str]
    start: Type[Node]
    nodes: List[NodeConfig]
```

Benefits:

- Type-safe pipeline definition
- Self-documenting structure
- Validation at construction time
- Clear visualization of flow

### Validation (validate.py)

The validation system ensures pipeline integrity:

```python
class PipelineValidator:
    def validate(self):
        self._validate_dag()
        self._validate_connections()
```

Checks:

- DAG structure (no cycles)
- Node reachability
- Valid routing configuration
- Connection consistency

## Design Patterns in Action

### Chain of Responsibility

The pattern manifests in several ways:

1. Each node processes its specific task independently
2. Nodes communicate only through the TaskContext
3. Processing flow is unidirectional
4. Each node decides whether to pass control forward

### Factory Pattern

Used in node instantiation:
```python
def _instantiate_node(node_class: Type[Node]) -> Node:
    return node_class()
```

### Strategy Pattern

Implemented in routers:
```python
class RouterNode(ABC):
    @abstractmethod
    def determine_next_node(self, task_context: TaskContext) -> Optional[Node]:
        pass
```

## Practical Usage

Creating a pipeline involves:

1. Define nodes for each processing step:
```python
class AnalyzeNode(Node):
    def process(self, context: TaskContext) -> TaskContext:
        # Implement analysis logic
        return context
```

2. Define the pipeline structure:
```python
class AnalysisPipeline(Pipeline):
    pipeline_schema = PipelineSchema(
        start=AnalyzeNode,
        nodes=[
            NodeConfig(node=AnalyzeNode, connections=[ResultNode])
        ]
    )
```

3. Execute the pipeline:
```python
pipeline = AnalysisPipeline()
result = pipeline.run(event)
```

This architecture provides a robust foundation for building complex AI workflows while maintaining code clarity and preventing common pitfalls in AI system design.

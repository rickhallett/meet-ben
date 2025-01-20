# Graphs - PydanticAI

## Introduction to Graphs

Graphs and finite state machines (FSMs) are powerful abstractions to model, execute, control, and visualize complex workflows.

- **PydanticAI** offers an async graph and state machine library called **`pydantic-graph`** for Python, leveraging type hints.

- This tool is independent of **pydantic-ai** and can serve as a standalone graph-based state machine library.

> **Note**: Graph support is in very early beta and subject to change.

## Installation

Install `pydantic-graph` using the following commands:

### Using pip
```bash
pip install pydantic-graph
```

### Using uv
```bash
uv add pydantic-graph
```

## Graph Types

### `GraphRunContext`

- **`GraphRunContext`** holds the state of the graph and dependencies and is passed to nodes during execution.

- It is generic in the state type of the graph, `StateT`.

### `End`

- **`End`** indicates the graph run should end.

- It is generic in the graph return type, `RunEndT`.

### Nodes

- Nodes are subclasses of `BaseNode`.
- Generally defined as `dataclass`es with fields for parameters, business logic in the `run` method, and return annotations.

#### Example Node Definition
```python
from dataclasses import dataclass
from pydantic_graph import BaseNode, GraphRunContext

@dataclass
class MyNode(BaseNode[MyState]):
    foo: int

    async def run(self, ctx: GraphRunContext[MyState]) -> AnotherNode:
        ...
        return AnotherNode()
```

### Graph

- **`Graph`** is the execution graph made up of a set of node classes.

- It is generic in `state`, `deps`, and `graph return type`.

#### Example Graph Definition
```python
from dataclasses import dataclass
from pydantic_graph import BaseNode, End, Graph, GraphRunContext

@dataclass
class DivisibleBy5(BaseNode[None, None, int]):
    foo: int

    async def run(self, ctx: GraphRunContext) -> Increment | End[int]:
        if self.foo % 5 == 0:
            return End(self.foo)
        else:
            return Increment(self.foo)

@dataclass
class Increment(BaseNode):
    foo: int

    async def run(self, ctx: GraphRunContext) -> DivisibleBy5:
        return DivisibleBy5(self.foo + 1)

fives_graph = Graph(nodes=[DivisibleBy5, Increment])
result, history = fives_graph.run_sync(DivisibleBy5(4))
```

## Stateful Graphs

- **State** provides a way to access and mutate an object (often a `dataclass` or Pydantic model) as nodes run.
- Future work may include state persistence.

#### Vending Machine Example
```python
from dataclasses import dataclass
from rich.prompt import Prompt
from pydantic_graph import BaseNode, End, Graph, GraphRunContext

@dataclass
class MachineState:
    user_balance: float = 0.0
    product: str | None = None

@dataclass
class InsertCoin(BaseNode[MachineState]):
    async def run(self, ctx: GraphRunContext[MachineState]) -> CoinsInserted:
        return CoinsInserted(float(Prompt.ask('Insert coins')))

# Additional nodes for CoinsInserted, SelectProduct, and Purchase...
vending_machine_graph = Graph(nodes=[InsertCoin, CoinsInserted, SelectProduct, Purchase])
```

## GenAI Example

- Uses PydanticAI or GenAI for real-world functionality.
- Example graph with agents to generate a welcome email and provide feedback.

```python
from dataclasses import dataclass
from pydantic_ai import Agent
from pydantic_graph import BaseNode, End, Graph

@dataclass
class Email:
    subject: str
    body: str

email_writer_agent = Agent('google-vertex:gemini-1.5-pro', result_type=Email)

# Setup for WriteEmail, Feedback nodes and state

feedback_graph = Graph(nodes=(WriteEmail, Feedback))
email, _ = await feedback_graph.run(WriteEmail(), state)
```

## Custom Control Flow

- Graphs can be run one node at a time using `next`, helpful for processes needing external input or extended execution.

#### Example Control Flow
```python
from rich.prompt import Prompt
from pydantic_graph import End, Graph, HistoryStep
from ai_q_and_a_graph import Ask, question_graph, QuestionState, Answer

async def main():
    state = QuestionState()
    node = Ask()
    history: list[HistoryStep[QuestionState]] = []
    while True:
        node = await question_graph.next(node, history, state=state)
        if isinstance(node, Answer):
            node.answer = Prompt.ask(node.question)
        elif isinstance(node, End):
            print(f'Correct answer! {node.data}')
            return
```

## Dependency Injection

- `pydantic-graph` supports dependency injection using `GraphRunContext.deps`.

#### Example Using ProcessPoolExecutor
```python
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pydantic_graph import BaseNode, End, Graph, GraphRunContext

@dataclass
class GraphDeps:
    executor: ProcessPoolExecutor

# Modify nodes to use executor...
async def main():
    with ProcessPoolExecutor() as executor:
        deps = GraphDeps(executor)
        result, history = await fives_graph.run(DivisibleBy5(3), deps=deps)
```

## Mermaid Diagrams

- Generate diagrams using `mermaid_code`, `mermaid_image`, or `mermaid_save`.

- Customize with labels, notes, and highlighting:

```python
from ai_q_and_a_graph import Ask, question_graph

question_graph.mermaid_save('image.png', highlighted_nodes=[Answer])
```

This document provides an overview and code snippets for incorporating graphs with the `pydantic-graph` library in Python.
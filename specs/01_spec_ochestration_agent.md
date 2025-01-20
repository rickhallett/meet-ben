# Specification Template
> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

- Create an **OrchestratorAgent** using pydantic-ai that coordinates communication among various specialized agents, managing which agent is currently active and routing messages properly.

## Mid-Level Objective

- Load existing agents (SetupAgent, ChatAgent, DatabaseAgent, IntentIdentifier, NoteTaker, and any others) into a coherent application flow.
- Track the current "active" agent based on user context or internal logic.
- Route messages and data between agents, ensuring each agent receives the correct input and returns valid outputs.
- Handle transitions between agents based on agent output or user instructions.
- Provide a unified interface for external calls, so that the application (or user) only interacts with a single orchestrator method, while the orchestrator delegates tasks to the right agent(s).

## Implementation Notes

- Use [`Agent` class](/app/utils/docs/pydantic-ai/agents.md) from pydantic-ai to define the OrchestratorAgent.
- The orchestrator must maintain a simple or advanced state machine to know which agent is “currently active,” possibly switching agents in response to certain triggers (like user input or a specific agent’s output).
- Each sub-agent is also a pydantic-ai `Agent` that can be called as a tool or used directly.
- Messages from the user and intermediate results from sub-agents should be tracked in the orchestrator to support debugging and usage reporting.
- Consider usage of an internal usage limit or usage aggregator to track tokens among all sub-agents.

## Context
app/utils/docs/pydantic-ai/agents.md

### Beginning context
- app/core/engine/orchestrator_agent.py
- Other agent definitions exist but are not yet integrated (SetupAgent, ChatAgent, DatabaseAgent, IntentIdentifier, NoteTaker).

### Ending context
- A new file (or an updated file) defining the OrchestratorAgent.
- The orchestrator code can properly import and instantiate other agents, or reference them when orchestrating calls.

## Low-Level Tasks
> Ordered from start to finish

1. **Create OrchestratorAgent structure**  
```aider
**Prompt**  
Add the initial OrchestratorAgent definition to `orchestrator.py`. Create the `OrchestratorAgent` class extending pydantic-ai’s `Agent` (or referencing it in composition).

**File**  
`orchestrator.py`

**New Class**  
`class OrchestratorAgent(Agent)`

**Implementation Details**  
- Use Python typing to specify dependencies (e.g., a `dict` or custom type).
- Initialize sub-agents (e.g., SetupAgent, ChatAgent, DatabaseAgent, IntentIdentifier, NoteTaker).  
- Add placeholders for any custom system prompts or methods.  

Example:
```python
# orchestrator.py
from pydantic_ai import Agent, RunContext
from typing import Any, Optional

class OrchestratorAgent(Agent[None, str]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Example sub-agents (assume they've been imported):
        self.setup_agent = SetupAgent('my-setup-model')  
        self.chat_agent = ChatAgent('my-chat-model')
        self.database_agent = DatabaseAgent('my-db-model')
        self.intent_identifier = IntentIdentifier('my-intent-model')
        self.note_taker = NoteTaker('my-note-model')

    # Additional placeholders:
    # def some_method(...):
    #     ...
```

2. **Implement state tracking for active agent**  
```aider
**Prompt**  
Add a mechanism in `orchestrator.py` to keep track of which agent is “active.” Possibly store `current_agent_name: str` or an enum, plus a helper function to switch states.

**File**  
`orchestrator.py`

**Updated Class**  
`OrchestratorAgent`

**Implementation Details**  
- Introduce a field like `self.current_agent: Optional[str] = None`.
- Provide a method `set_active_agent(agent_name: str) -> None` for updating state.
- Provide a method `get_active_agent() -> Optional[Agent]` to return the instance of the active agent.

Example:
```python
# orchestrator.py

class OrchestratorAgent(Agent[None, str]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_agent = SetupAgent('my-setup-model')
        self.chat_agent = ChatAgent('my-chat-model')
        self.database_agent = DatabaseAgent('my-db-model')
        self.intent_identifier = IntentIdentifier('my-intent-model')
        self.note_taker = NoteTaker('my-note-model')
        self.current_agent: Optional[str] = None

    def set_active_agent(self, agent_name: str) -> None:
        # e.g. "setup", "chat", "database", "intent", "note"
        self.current_agent = agent_name

    def get_active_agent(self) -> Optional[Agent]:
        if self.current_agent == 'setup':
            return self.setup_agent
        elif self.current_agent == 'chat':
            return self.chat_agent
        # etc. for other agents
        return None
```

3. **Implement message routing among sub-agents**  
```aider
**Prompt**  
Within `orchestrator.py`, add a method to delegate messages to the active agent. Possibly call it `route_message(user_input: str, ...) -> str`.

**File**  
`orchestrator.py`

**Updated Class**  
`OrchestratorAgent`

**Implementation Details**  
- A public `route_message` that checks the current agent, calls `agent.run()` or `agent.run_sync()` with the user’s text.
- Possibly read the active agent from `self.get_active_agent()`.
- Return or store the sub-agent’s response.

Example:
```python
# orchestrator.py

class OrchestratorAgent(Agent[None, str]):
    ...

    def route_message(self, user_input: str) -> str:
        active_agent = self.get_active_agent()
        if not active_agent:
            # Default or fallback logic
            return "No active agent selected."
        # Basic synchronous call:
        result = active_agent.run_sync(user_input)
        return result.data
```

4. **Add usage tracking and method to finalize or close orchestrated interactions**  
```aider
**Prompt**  
Still in `orchestrator.py`, expand the `OrchestratorAgent` to track usage from sub-agents. Provide a method like `finalize_session()` to close or summarize usage.

**File**  
`orchestrator.py`

**Updated Class**  
`OrchestratorAgent`

**Implementation Details**  
- Each sub-agent call can pass a shared `usage` object. Or, individually retrieve each `RunResult` usage and sum them up.
- `finalize_session()` could gather usage from each sub-agent, log it, or do cleanup tasks.  

Example:
```python
# orchestrator.py
from pydantic_ai.usage import Usage

class OrchestratorAgent(Agent[None, str]):
    ...
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_usage = Usage()  # accumulates requests/tokens

    def route_message(self, user_input: str) -> str:
        active_agent = self.get_active_agent()
        if not active_agent:
            return "No active agent selected."
        result = active_agent.run_sync(user_input)
        # Aggregate usage
        if result.usage():
            self.total_usage += result.usage()
        return result.data

    def finalize_session(self) -> str:
        # E.g. cleanup
        usage_report = (
            f"Total requests: {self.total_usage.requests}, "
            f"tokens: {self.total_usage.total_tokens}."
        )
        # Potential database save or logging
        # ...
        return usage_report
```



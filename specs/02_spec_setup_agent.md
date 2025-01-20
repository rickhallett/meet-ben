# Specification Template
> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

- Create a **SetupAgent** using pydantic-ai that captures a user’s name, determines whether they’re setting up a formulation for a new client or an existing one, and configures user-specific preferences, especially the `assistance_level`, which impacts how other agents behave.

## Mid-Level Objective

- Prompt user for essential setup inputs (e.g., user’s name).
- Prompt user to choose between creating a new client formulation or using an existing one.
- Update a configuration object/structure that can be accessed by other agents, especially changing `assistance_level`.
- Provide a single entry point (method) that other agents or the orchestrator can use to retrieve the current configuration for a specific user.

## Implementation Notes

- Use [`Agent`](/app/utils/docs/pydantic-ai/agents.md) to define `SetupAgent`.
- The `result_type` can be a custom typed structure or dictionary that stores:
  - `user_name: str`
  - `client_mode: Literal["new", "existing"]`
  - `assistance_level: int`
- The `SetupAgent` might call small function tools or simply be driven by user input, e.g., prompting for more details if the user’s input is incomplete.
- Because `assistance_level` is used widely by other agents, store it in a globally accessible store or provide it via an internal data structure that can be shared with the orchestrator.

## Context

### Beginning context
- app/core/engine/setup_agent.py
- Possibly some shared data store or placeholders exist for user configurations.

### Ending context
- A `setup_agent.py` file (or similar) defining `SetupAgent`.
- The agent can gather user’s name, determine client type, and set `assistance_level` in an internal or shared config.

## Low-Level Tasks
> Ordered from start to finish

1. **Define SetupAgent class**  
```aider
**Prompt**  
Create `setup_agent.py` and define the `SetupAgent` class extending `Agent`.  
Specify a `result_type` with fields for user info, client mode, and assistance level.

**File**  
`setup_agent.py`

**Class**  
`SetupAgent(Agent[..., ...])`

**Implementation Details**  
- `deps_type` might be `None` or a config object, depending on architecture.  
- Provide a system prompt or decorator-based system prompts describing the role.
- Use typed result structure (e.g., pydantic `BaseModel`) or `TypedDict`.
```
2. **Implement data prompts for user name, client mode**  
```aider
**Prompt**  
Inside `SetupAgent`, define logic (system prompts or user tool calls) that asks for or extracts user name and whether they are working on new or existing client formulation.

**File**  
`setup_agent.py`

**Method**  
Possibly a tool or structured function that clarifies user input.

**Implementation Details**  
- A system prompt, e.g., "If you don’t know the user’s name, ask for it, then store it."
- A second question: "Are you working on a new or existing client formulation?"
- Maintain partial results in case user only gave partial info.
```

3. **Set or update assistance_level**  
```aider
**Prompt**  
Define a mechanism to set the user’s `assistance_level` (e.g. an integer or range). Could be asked explicitly, or set by default.

**File**  
`setup_agent.py`

**Implementation Details**  
- Possibly use a separate tool `set_assistance_level(level: int)` or prompt the user for preference.  
- Validate the level (e.g., 1–5).
- Store the final config in `result_type` or in a local config object that can be retrieved.
```

4. **Provide a method to retrieve user config**  
```aider
**Prompt**  
Add a function to SetupAgent (or globally) to retrieve the user’s final config once set.

**File**  
`setup_agent.py`

**Function**  
`get_user_config(user_id: Optional[str] = None) -> dict | typed structure`

**Implementation Details**  
- Could be a plain method or a tool call, returning data from the final `RunResult`.
- Alternatively, keep an internal dictionary keyed by user name or session ID.
- Return `{"user_name": ..., "client_mode": ..., "assistance_level": ...}`.
```

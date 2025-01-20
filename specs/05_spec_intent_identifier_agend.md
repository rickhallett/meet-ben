
# IntentIdentifier Specification

## High-Level Objective
- Create an **IntentIdentifier** agent that analyzes user input to determine intent(s).
- If multiple intents are detected, subdivide them into tasks, to be run sequentially or in parallel.

## Mid-Level Objective
1. Receive user text input.
2. Parse or classify the input to identify one or more possible intents (e.g. “create record”, “ask question”, “retrieve data”).
3. Return a structured result describing recognized intent(s) and recommended execution order (parallel or sequential).
4. Possibly raise clarifications if the input is ambiguous.

## Implementation Notes
- Use [`Agent`](../pydantic-ai/agents.md) to define `IntentIdentifier`.
- `result_type` might be a typed structure listing identified intents, e.g. `[{"intent_name": "some_intent", "parallel": false}, ...]`.
- Internally, this agent can rely on a system prompt providing classification guidelines or might have tool calls for deeper analysis.
- If needed, can request more info from the user via `ChatAgent` or a direct tool call if the input is unclear.

## Context
### Beginning context
- No existing `IntentIdentifier`.
- The orchestrator or ChatAgent is present to supply user input.

### Ending context
- A `intent_identifier.py` file defining `IntentIdentifier`.
- This agent can reliably identify tasks from a user’s command and return them in a structured format.

## Low-Level Tasks
> Ordered from start to finish

1. **Define `IntentIdentifier` class**  
```aider
**Prompt**  
Create `intent_identifier.py` with `IntentIdentifier(Agent[..., ...])`.

**File**  
`intent_identifier.py`

**Class**  
`IntentIdentifier(Agent[..., ...])`

**Implementation Details**  
- Possibly a `result_type` that’s a list of objects representing discovered intents.
- system_prompt can explain how to interpret user text, e.g., “You can identify multiple tasks… if there’s more than one, decide parallel or sequential.”
```

2. **Implement a classification method**  
```aider
**Prompt**  
Add logic to parse the user’s text and assign an intent or multiple. Could be done via a system prompt or function calls.

**File**  
`intent_identifier.py`

**Method**  
`analyze_intent(user_text: str) -> list[IntentData]`

**Implementation Details**  
- Possibly a single run call returning a JSON of tasks.
- Example output: `[{"intent": "update_graph", "parallel": false}]` or `[{"intent":"ask_question","parallel":true}, ...]`.
- Might rely on LLM, e.g. “Given the user text, return a JSON with possible actions.”  
```

3. **Handle ambiguous inputs**  
```aider
**Prompt**  
If input is unclear, raise `ModelRetry` or call ChatAgent for clarifications.

**File**  
`intent_identifier.py`

**Implementation Details**  
- For example, if user text is extremely short, we might prompt: “No clear intent found, please clarify.”  
- Or rely on a system prompt with high temperature to guess.  
```

4. **Return final structured result**  
```aider
**Prompt**  
Ensure the final run of IntentIdentifier includes a `result_type` that matches the discovered tasks or an error message if none found.

**File**  
`intent_identifier.py`

**Implementation Details**  
- Example typed structure or `TypedDict`, e.g. `List[dict[str, Any]]`.
- On success, each dict might have `intent_name`, `confidence`, `run_mode` (parallel/sequential).
- On failure, return a single-object list with an error code or message.  
```
```
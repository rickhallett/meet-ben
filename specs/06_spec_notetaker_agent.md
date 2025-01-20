```md
# NoteTaker Specification

## High-Level Objective
- Create a **NoteTaker** agent that updates the graph (handled by DatabaseAgent or an in-memory approach) based on user input.
- Communicate with a hypothetical **QuestionAgent** to generate follow-up questions, which may be queued and displayed to the user via ChatAgent.

## Mid-Level Objective
1. Accept user input describing new data or updates to be applied to the graph.
2. Coordinate with **QuestionAgent** to generate optional follow-up questions for clarification.
3. Maintain a queue of pending questions (for the user to optionally answer later) and pass them to **ChatAgent** for display.
4. Commit the final validated updates to the graph (either directly or by sending them to DatabaseAgent).

## Implementation Notes
- Use [`Agent`](../pydantic-ai/agents.md) to define **NoteTaker**.
- The `result_type` could be:
  - A success message, or
  - A typed structure containing newly updated graph data or references to new nodes/edges.
- For generating follow-ups, call or reference a **QuestionAgent** (not yet fully specified, but presumably an agent that produces clarifying questions).
- For queueing questions, you might store them in a list on this agent’s instance or in a more global data store, then forward them to **ChatAgent**.
- Actual graph commits could be done by:
  1. Directly calling a DatabaseAgent tool, or
  2. Storing updates for later commit.

## Context

### Beginning context
- No existing `NoteTaker` definition.
- A working or planned `DatabaseAgent`, `ChatAgent`, and possibly a `QuestionAgent`.
- The system already can handle user messages and agent outputs in an orchestrated environment.

### Ending context
- A `note_taker.py` file defining `NoteTaker`.
- This agent can apply user-provided updates to the graph, request clarifications from the user, and queue additional questions.

## Low-Level Tasks
> Ordered from start to finish

1. **Define `NoteTaker` class**  
```aider
**Prompt**  
Create `note_taker.py` and define `NoteTaker(Agent[..., ...])`.

**File**  
`note_taker.py`

**Class**  
`NoteTaker(Agent[None, str])` (or whatever fits your typed structures)

**Implementation Details**  
- Possibly store references like `self.database_agent`, `self.question_agent`, `self.chat_agent`.
- A system prompt describing the role, e.g., "You're responsible for adding or updating data in the user's graph notes..."
```

2. **Implement graph update method**  
```aider
**Prompt**  
Add a function or tool in `NoteTaker` (e.g., `update_graph(data: dict) -> str`) that processes user input and modifies the graph. Possibly calls `DatabaseAgent` for actual DB changes.

**File**  
`note_taker.py`

**Method / Tool**  
`update_graph(data: dict) -> str`

**Implementation Details**  
- Could parse user input into a structured `data` object.
- Validate data. If incomplete, request clarifications from `QuestionAgent`.
- If complete, call `database_agent.save_changes(...)` or a relevant method to store changes.
- Return a success message or an error/warning string.
```

3. **Communicate with QuestionAgent for clarifications**  
```aider
**Prompt**  
Add logic to call (or reference) a `question_agent.run_sync()` with partial data to generate follow-up queries. Possibly store them in an internal list.

**File**  
`note_taker.py`

**Implementation Details**  
- Something like:
  ```python
  follow_ups = self.question_agent.run_sync("Analyze this partial data...", ...)
  self._pending_questions.extend(follow_ups.data)
  ```
- If user answers them, integrate responses into the final data.
```

4. **Queue follow-up questions for ChatAgent**  
```aider
**Prompt**  
Include a method that returns or sends the queued follow-ups to the user via ChatAgent.

**File**  
`note_taker.py`

**Method**  
`request_follow_ups() -> None`

**Implementation Details**  
- Possibly do `self.chat_agent.request_user_clarification(question)` for each pending question.
- Maintain a list `self._pending_questions: list[str]` that gets cleared once answered or discarded.
- The orchestrator or ChatAgent might handle the actual user loop to gather answers.  
```

5. **Store final updates**  
```aider
**Prompt**  
Once clarifications are resolved, finalize the updated data in the graph.

**File**  
`note_taker.py`

**Implementation Details**  
- If you haven’t already updated the DB, now you do it. Or you can keep changes in memory until an explicit commit from the orchestrator.  
- Return or log a success message with references to updated or newly added nodes.  
```
```
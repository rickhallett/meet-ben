```md
# Specification Template
> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

- Create a **ChatAgent** using pydantic-ai to capture user input before passing it to the IntentIdentifier agent.
- Format responses from other agents into a user-friendly style, determined by `personality` configuration (e.g. `"friendly"`, `"formal"`, `"clinical"`, or `"technical"`).
- Allow any other agent to call the ChatAgent if they need more information from the user.
- Store both user inputs and agent outputs in the message history database for UI updates.

## Mid-Level Objective

1. Collect user input and funnel it to the IntentIdentifier agent for analysis.
2. Provide a standardized, user-friendly response format based on the `personality` configuration.
3. Expose a method or tool enabling other agents to query the user (via ChatAgent) for clarifications.
4. Automatically save all inputs and outputs to the message history so the chat UI can display them.

## Implementation Notes

- Use [`Agent`](/app/utils/docs/pydantic-ai/agents.md) to define `ChatAgent`.
- The `ChatAgent` may have a `deps_type` referencing some config or a user session object to retrieve the user’s `personality`.
- The `result_type` might be `str` or a custom typed structure that includes a `formatted_response`.
- `ChatAgent` can hold a reference to `IntentIdentifier` or call it via a function tool. Alternatively, the orchestrator may pass messages to `ChatAgent`, which then calls `IntentIdentifier`.
- The ChatAgent must add user inputs and its own outputs to the message history storage. This can be done using PydanticAI’s built-in message logging or a custom solution.

## Context

### Beginning context
- app/core/engine/chat_agent.py
- An existing `IntentIdentifier` agent is presumably available, or at least planned.
- A message history DB or logging mechanism is in place or planned.

### Ending context
- A file `chat_agent.py` defining `ChatAgent`.
- This agent can intercept user messages, pass them to the IntentIdentifier agent, and apply personality-based formatting to final responses before returning them to the user or orchestrator.

## Low-Level Tasks
> Ordered from start to finish

1. **Define `ChatAgent` class**  
```aider
**Prompt**  
Create `chat_agent.py` and implement `ChatAgent(Agent[...])`.  
Include placeholders for references to the IntentIdentifier agent and a personality config.

**File**  
`chat_agent.py`

**Class**  
`ChatAgent(Agent[Any, str])`

**Implementation Details**  
- Possibly pass in or store a reference to `IntentIdentifier` in `__init__`.
- Use typed fields or a config object to store `personality: Literal["friendly","formal","clinical","technical"]`.
- Might define a system prompt describing the agent’s role: “You are a chatbot that collects user input, identifies intent, and returns a user-friendly response in a specified style.”  
```

2. **Capture user input, route to IntentIdentifier**  
```aider
**Prompt**  
Implement a method like `process_user_input(user_text: str)` that passes user_text to the IntentIdentifier.

**File**  
`chat_agent.py`

**Method**  
`process_user_input(user_text: str) -> str`

**Implementation Details**  
- Could internally call something like `self.intent_identifier.run_sync(user_text)`.
- Keep track of the identified intent or sub-intents. Possibly store them in a local variable or return them so you can respond accordingly.
```

3. **Format responses based on personality**  
```aider
**Prompt**  
Add a function to transform raw text from any agent into a style consistent with the user’s selected personality.

**File**  
`chat_agent.py`

**Method**  
`format_response(raw_text: str) -> str`

**Implementation Details**  
- If `self.personality == "friendly"`, prepend “Hey friend!” or use casual language.
- If `self.personality == "formal"`, structure the text more precisely.
- If `self.personality == "clinical"`, maybe use more technical/medical references.
- If `self.personality == "technical"`, ensure jargon or short bullet points.  
```

4. **Add tool/method for other agents to request clarifications via ChatAgent**  
```aider
**Prompt**  
Provide a function that other agents can call (like `request_user_clarification(question: str) -> str`) which asks the user for more info.

**File**  
`chat_agent.py`

**Method**  
`request_user_clarification(question: str) -> str`

**Implementation Details**  
- This might be a tool function in ChatAgent (decorated with `@chat_agent.tool_plain` or `@chat_agent.tool`).
- Possibly triggers a system message to the user: “Another agent needs your input: {question}.”
- Return the user’s input or store it in the message DB for reference.  
```

5. **Log all interactions to message history**  
```aider
**Prompt**  
Ensure that for each user input and ChatAgent output, we store data in the message history.

**File**  
`chat_agent.py`

**Implementation Details**  
- Use either built-in PydanticAI logging or a custom DB call.
- E.g., after calling `intent_identifier.run_sync()`, add the user’s query and the returned result to the message history.
- After formatting a response, store that as well. This ensures the chat UI can reflect the entire conversation.  
```
```
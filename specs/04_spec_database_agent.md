```md
# DatabaseAgent Specification

## High-Level Objective
- Create a **DatabaseAgent** to interact with a graph database, storing and retrieving data.
- Implement an internal in-memory cache of the graph to reduce database calls.
- Only commit changes to the database when explicitly requested (via a “save” command), upon session termination/timeout, or at periodic intervals.

## Mid-Level Objective
1. Load graph data from the database into an in-memory structure on initialization.
2. Apply modifications (updates, inserts, deletes) in memory without immediately writing to the database.
3. Provide a “save” method (or function tool) to commit changes to the database.
4. Handle session timeouts or orchestrator triggers to either discard changes or commit them, depending on business logic.

## Implementation Notes
- Use [`Agent`](../pydantic-ai/agents.md) from pydantic-ai to define `DatabaseAgent`.
- The `result_type` may be domain-specific (like a graph object or success/error message) or a more generic data structure.  
- Provide function tools for retrieving nodes or edges, modifying them in the cache, and storing them.
- Possibly maintain a `last_backup_time` to know when a periodic backup is due.

## Context
### Beginning context
- No existing `DatabaseAgent`.
- A graph database is available (Neo4j or similar, or a custom adjacency list).
- A plan or requirement for in-memory caching exists.

### Ending context
- A `database_agent.py` (or similar) file defining `DatabaseAgent`.
- The agent can handle calls to fetch or modify graph data, storing changes in memory until a commit is triggered.

## Low-Level Tasks
> Ordered from start to finish

1. **Define `DatabaseAgent` class**  
```aider
**Prompt**  
Create `database_agent.py` and define `DatabaseAgent` extending `Agent`.

**File**  
`database_agent.py`

**Class**  
`DatabaseAgent(Agent[..., ...])`

**Implementation Details**  
- Possibly `deps_type` is a database connection or config object.
- The `result_type` might be a status message (`str` or a small structure).
- The system prompt can explain: “You are responsible for graph DB read/write. Avoid excessive calls by caching data in memory.”
```

2. **Initialize graph cache**  
```aider
**Prompt**  
In the constructor or an init method, fetch the full graph (or relevant portion) from DB into an in-memory data structure (e.g. dict, adjacency list).

**File**  
`database_agent.py`

**Implementation Details**  
- Connect to the graph database (via `ctx.deps` or a configured environment).
- Store data in `self._graph_cache`.
```

3. **Provide function tools for read/write operations**  
```aider
**Prompt**  
Create methods or pydantic-ai tools to query or mutate the graph in memory.

**File**  
`database_agent.py`

**Method / Tools**  
- `get_node(node_id: str) -> NodeData`
- `update_node(node_id: str, new_data: dict) -> bool`
- `create_edge(from_id: str, to_id: str, relationship: str) -> bool`
- etc.

**Implementation Details**  
- All changes apply to `self._graph_cache`, not DB.
- On each call, confirm or raise an error if something’s missing.
```

4. **Implement “save” and “discard”**  
```aider
**Prompt**  
Add a function tool or method to commit all cached changes to the DB, plus optionally discard unsaved changes.

**File**  
`database_agent.py`

**Method**  
- `save_changes() -> str`
- `discard_changes() -> str`

**Implementation Details**  
- For “save,” transform the in-memory delta into queries for the DB.
- For “discard,” revert `self._graph_cache` from DB or a last-known safe copy.
- Possibly track “last_backup_time,” auto-saving if needed.
```

5. **Handle session end or periodic backups**  
```aider
**Prompt**  
Where needed, define logic to auto-commit or discard changes after session end, a specific time period, or a usage event.

**File**  
`database_agent.py`

**Implementation Details**  
- Could be triggered from orchestrator or a usage limit event.
- Decide how to store the last backup time, e.g. `self._last_backup: datetime`.
- If a backup interval is reached, call `save_changes()`.
```

---

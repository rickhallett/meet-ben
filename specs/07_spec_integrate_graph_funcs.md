```md
# Graph Integration Specification

> This specification focuses on integrating the functions in `graph_constructor.py` with relevant agents (most notably the **DatabaseAgent** and possibly the **NoteTaker**, or other agents that require reading/writing to the graph).

## High-Level Objective

- Incorporate utility methods from `graph_constructor.py` into the broader agent architecture.  
- Ensure that **DatabaseAgent** (and others, e.g. NoteTaker) can load, save, query, and modify the in-memory or persisted graph using these methods.  
- Maintain the caching and session-based logic introduced by the agent, while still using the robust set of utilities available in the `graph_constructor.py` file.

## Mid-Level Objectives

1. **Consolidate**: Decide which methods from `graph_constructor.py` should be:
   - Called directly within **DatabaseAgent** (e.g. saving/loading, adding nodes, connecting nodes, subgraph extraction, etc.).
   - Potentially exposed as function tools or ephemeral calls from other agents (e.g. NoteTaker wanting to add a node or retrieve a subgraph).
2. **Modify**: If needed, lightly adapt or wrap certain functions to fit the agent’s caching logic (in-memory vs. DB commits).
3. **Coordinate**: Ensure that calls from other agents to read or write the graph go through a central agent interface (i.e. DatabaseAgent’s function tools).
4. **Session awareness**: Leverage session-based timestamps, tracking, or partial commits in the same manner as `graph_constructor.py` uses them, ensuring consistent usage across the application.

## Context

### Beginning context
- `graph_constructor.py` provides a broad suite of utility functions for building, searching, and modifying a NetworkX graph.
- **DatabaseAgent** is conceptualized to store in-memory changes, then commit them to the database on command.
- A separate or combined approach for reading/writing from JSON is present in `graph_constructor.py` (`to_json_store` and `from_json_store`).

### Ending context
- The relevant agent(s) (most importantly the **DatabaseAgent**) will seamlessly incorporate the methods from `graph_constructor.py`, either by:
  - Importing and calling them directly, or
  - Wrapping them with pydantic-ai tools for external usage.
- `graph_constructor.py` remains a utility module, while the logic for caching and session-based changes belongs to the agent.

## Low-Level Tasks
> Ordered from start to finish

1. **Determine Which Methods Map to Agent Tools**  
```aider
**Prompt**  
"Review `graph_constructor.py` and decide which methods are relevant for direct agent usage. 
For example:
- `create_graph`, `build_graph` might be used at agent init or session start.
- `to_json_store`, `from_json_store` might map to 'save'/'load' calls in DatabaseAgent’s function tools.
- Node/edge queries (like `find_node_by_id`, `find_neighbors`, `add_node`, etc.) might also be wrapped as DatabaseAgent function tools."

**File**  
`database_agent.py` or `note_taker.py`

**Implementation Details**  
- In `database_agent.py`, define which functions are direct imports vs. wrapped.  
- If the agent uses an internal `nx.DiGraph`, integrate them by passing `self._graph_cache` to these functions.
```

2. **Adapt or Wrap Functions for DatabaseAgent**  
```aider
**Prompt**  
"In `database_agent.py`, create agent tools that call the relevant `graph_constructor` functions. 
For example, a `load_graph_from_store()` tool that calls `from_json_store()`, or `add_graph_node()` that calls `add_node(...)` with session-based logic."

**File**  
`database_agent.py`

**Implementation Details**  
- If the agent’s caching logic requires partial changes, ensure that calls to e.g. `to_json_store(graph)` only happen during a final commit or timed interval.
- Possibly rename or unify function signatures if agent usage differs slightly from the original method. 
- For each function tool, decorate with `@database_agent.tool` or `@database_agent.tool_plain`.
```

3. **Integrate Session Info**  
```aider
**Prompt**  
"Make sure each method is session-aware by passing `session_info` or referencing it from the agent’s context. 
Add or update timestamps in the node/edge data the same way `graph_constructor.py` handles it."

**File**  
`database_agent.py` or shared session config

**Implementation Details**  
- If `DatabaseAgent` has a `deps_type` referencing a session object, pass that info to `graph_constructor` calls (like `add_node`, `connect_nodes`).
- For example:  

  def add_node_tool(ctx: RunContext[Session], node_id: str, content: str):
      add_node(self._graph_cache, node_id, content, "layer-2", ctx.deps.session_info)

- Maintain consistent timestamp usage with `ZoneInfo("UTC")`.
```

4. **Expose Graph CRUD to Other Agents**  
```aider
**Prompt**  
"Ensure that other agents, like NoteTaker, can call DatabaseAgent to read or write node data. Possibly define function tools that match the usage patterns from `note_taker.py`."

**File**  
`note_taker.py`, `database_agent.py` (both)

**Implementation Details**  
- For example, `NoteTaker` wanting to add a new node might call `database_agent.run_sync("add_node_tool", {...})`.
- This pattern ensures all actual graph interactions pass through DatabaseAgent’s caching logic, and the underlying `graph_constructor.py` methods get invoked in a controlled manner.
```

5. **Ensure Save/Load Behavior**  
```aider
**Prompt**  
"Guarantee that agent’s final commit logic and session termination triggers a `save_graph` or `to_json_store(...)` call. Also allow loading an existing graph on session start. Add graceful error handling for missing files."

**File**  
`database_agent.py` (or orchestrator logic)

**Implementation Details**  
- For example, `DatabaseAgent` might have:

  @database_agent.tool
  def load_graph_tool():
      self._graph_cache = from_json_store("store.json")
  
  @database_agent.tool
  def save_graph_tool():
      to_json_store(self._graph_cache, "store.json")

- On session end or when user requests a save, call `save_graph_tool()`.
```

6. **Extend or Customize** (Optional)  
```aider
**Prompt**  
"Optionally refine advanced features such as BFS, DFS, or other graph queries and provide them as agent methods if required by the system or user."

**File**  
`database_agent.py` (others if needed)

**Implementation Details**  
- The aggregator or orchestrator can then do e.g. `database_agent.run_sync("depth_first_search", {"start_node": "fusion"})`.
- Return results in a structured format for UI consumption.
```

```
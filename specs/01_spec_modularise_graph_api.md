# Graph Module Partition Specification

> **Goal**: Split the single `graph_constructor.py` file into multiple modules for better maintainability, logical grouping, and clarity.

## High-Level Objective

- Refactor `graph_constructor.py` into separate Python modules that logically group related functions.
- Preserve existing functionality, ensuring no major interface changes (unless necessary for cleanliness).

## Mid-Level Objective

1. **Core Graph Construction**  
   - Basic operations (creating a new graph, adding nodes/edges, building the full markup-based graph).
   - Keep data models (`Node`, `Edge`, enumerations) co-located for ease of reference.

2. **Graph Analysis & Utilities**  
   - Traversal methods (DFS, BFS, custom walks).
   - Query methods (neighbors, searching by content/weight/timestamp, etc.).
   - Methods for exploring or summarizing node/edge relationships.

3. **Graph Persistence**  
   - Save/load graph JSON routines.
   - Backup/restore or test save/load flows.

## Implementation Notes

- Maintain code that references `Node`/`Edge` pydantic models in one central place.  
- Keep each module small but cohesive:
  - e.g. `graph_core.py` for node/edge creation, `graph_utils.py` for BFS/DFS/traversals, `graph_store.py` for save/load.
- Update imports across modules if certain internal functions need to call from each other (careful to avoid circular imports).

## Context

### Beginning Context

- `graph_constructor.py` is ~2000 lines, containing enumerations, data models, node/edge creation, utilities for searching, BFS/DFS, plus load/save logic.

### Ending Context

- Possibly 3–4 smaller `.py` modules like:
  1. **graph_core.py**:  
     - Enums: `NodeType`, `EdgeType`, `ProgramMode`  
     - Pydantic classes: `Node`, `Edge`  
     - Functions: `create_graph`, `add_node`, `connect_nodes`, `build_graph`, etc.
  2. **graph_utils.py**:  
     - All BFS/DFS/traversals: `depth_first_walk`, `breadth_first_walk`, `find_neighbors`, `traverse_by_edge_type`, `extract_subgraph`, etc.  
     - Query methods: `find_nodes_by_content`, `find_nodes_by_weight`, `find_nodes_by_timestamp`, `find_shortest_path`  
     - More advanced operations like `custom_walk`, `identify_conflicts`, etc.
  3. **graph_store.py**:  
     - `to_json_store`, `from_json_store`, `test_save_load`  
     - Possibly additional logic for partial or advanced store/restore if needed.
  4. **graph_analysis.py** (optional, or included in `graph_utils.py`):
     - Summaries, expansions, e.g. `summarize_changes_over_time`, `nodes_missing_updates`, `find_underexplored_nodes`, `find_highly_connected_nodes`, `get_node_history`, `mark_node_as_explored`, `mark_node_as_rejected`, etc.
- The final set of modules is flexible, as needed by the maintainers.

## Low-Level Tasks
> Ordered from start to finish

1. **Create new module files**  
```aider
**Prompt**  
"Create `graph_core.py`, `graph_utils.py`, and `graph_store.py` (and optional `graph_analysis.py` if desired)."

**Files**  
`graph_core.py`, `graph_utils.py`, `graph_store.py` (and `graph_analysis.py` optionally)

**Implementation Details**  
- Start by copying relevant code from `graph_constructor.py` into each file.  
- Keep `Node`, `Edge`, `NodeType`, `EdgeType` in `graph_core.py`.  
- Migrate core building logic (`create_graph`, `add_node`, `connect_nodes`, `build_graph`) to `graph_core.py`.

# Specification: Day 1 Implementation

## High-Level Objective
- Establish the foundational codebase for the chatbot’s **graph-based data structure** using NetworkX.

## Mid-Level Objectives
- Set up a basic **NetworkX** directed, weighted graph structure.
- Use pydantic to define the Node and Edge objects, additional objects etc
- Implement **node** and **edge** creation with minimal timestamps.
- Creation of helper functions to add nodes and edges to the graph
- Include **simple tests** to confirm that nodes and edges can be added.

## Implementation Notes

- **Design Decision:**  
  Instead of using raw dictionaries for nodes and edges, we will define custom classes (objects) for both **Node** and **Edge**. This choice provides:
  - **Encapsulation:** All attributes (type, content, timestamps, weight) and behaviors (e.g., updating timestamps, recalculating weights) are contained within their respective classes.
  - **Separation of Concerns:** Specific logic for nodes (e.g., comparing value completeness) is isolated from edge logic (e.g., computing relationship strength), simplifying maintenance.
  - **Type Safety & Validation:** Custom constructors and type hints can enforce that required fields are provided and correctly formatted.
  - **Extensibility:** Future changes—such as adding new methods for merging nodes or automatic timeline updates—can be implemented in dedicated classes without impacting other parts of the system.
  - **Testing & Readability:** Object-oriented code is easier to unit test on an individual basis, and the use of `Node` and `Edge` classes makes the system self-documenting and clear.

- **Additional Tools:** Optionally use `pytest` for testing.
- **Coding Standards:** Follow PEP 8; keep functions small and testable; use clear class and method naming.
- **Important Technical Detail:**  
  Both **Node** and **Edge** objects will include a `timestamps` object (from TimeStamp class) Object fields to include `type: str`, `content: str`, `timestamp: datetime`, `weight: Float`. These objects will later be integrated with the NetworkX graph by storing them as data attributes or by using their properties as needed.

- **Integration with NetworkX:**  
  When adding nodes or edges to the NetworkX `DiGraph`, the custom objects will be serialized into attributes (or directly stored if appropriate) so that graph algorithms can be applied while preserving our custom object data.

- **Other Technical Guidance:**  
  All new changes should be accompanied by unit tests (using `pytest`) to ensure that the object behavior (creation, updates, and integration with the graph) is correct.

- **Dependencies and Requirements:**  
  - `networkx` for the graph framework.
  - Custom class definitions for `Node` and `Edge` to replace raw dictionary use.

- **Files to be Created or Updated:**  
  - `graph_manager.py`: Contains class definitions for `Node` and `Edge`, along with graph management functions.
  - `requirements.txt`: Lists dependencies including `networkx` and `pytest`.
  - `test_graph_manager.py`: Includes unit tests to verify correct object instantiation, serialization, and integration.


## Context

### Beginning Context
- No existing Python files (developed in isolation from the rest of the existing codebase initially)
- The only file is this `spec_graph_poc.md` (hypothetical) containing instructions.

### Ending Context
- A new file structure:
  - `requirements.txt` (listing dependencies)
  - `graph_manager.py` (core module for graph logic)
  - `test_graph_manager.py` (basic tests for node/edge creation)

## Low-Level Tasks

1. **Create the base Python module for the graph logic**|
  ```aider
  What prompt would you run to complete this task?
  - I'd create a file named `graph_manager.py` in my code editor or IDE.

  What file do you want to CREATE or UPDATE?
  - CREATE `graph_manager.py`

  What function do you want to CREATE or UPDATE?
  - CREATE `initialize_graph()`

  What are details you want to add to drive the code changes?
  - The function should return an empty DiGraph instance with no nodes or edges.
  - Include basic docstring describing purpose.
  ```
2. **Implement node and edge creation with timestamps**
  ```aider
  What prompt would you run to complete this task?
  - Update `graph_manager.py` to add two functions: `add_node_with_timestamp` and `add_edge_with_timestamp`.

  What file do you want to CREATE or UPDATE?
  - UPDATE `graph_manager.py`

  What function do you want to CREATE or UPDATE?
  - CREATE `add_node_with_timestamp(graph, node_id, node_type, content, session_info)`
  - CREATE `add_edge_with_timestamp(graph, source_id, target_id, edge_type, session_info)`

  What are details you want to add to drive the code changes?
  - Each function attaches a `timestamps` list to the node/edge data.
  - Example of session_info: `{"session": 1, "note": "Initial creation"}`.
  - Each addition can also store a `weight` defaulting to 0.5 if none provided.
  ```
3. **Test the node and edge creation**
  ```aider
    What prompt would you run to complete this task?
  - Create a file `test_graph_manager.py` and run it with `pytest`.

  What file do you want to CREATE or UPDATE?
  - CREATE `test_graph_manager.py`

  What function do you want to CREATE or UPDATE?
  - CREATE test functions (e.g., `test_initialize_graph`, `test_add_node_with_timestamp`, `test_add_edge_with_timestamp`)

  What are details you want to add to drive the code changes?
  - `test_initialize_graph`: Check if returned object is a DiGraph with no nodes or edges.
  - `test_add_node_with_timestamp`: Ensure node is created with timestamps, correct `type`, `content`.
  - `test_add_edge_with_timestamp`: Ensure edge is created with timestamps, `weight`, correct `type`.

4. **Create a TimeStamp class**
  ```aider
  What prompt would you run to complete this task?
  - Create a file `timestamp.py` and define the `TimeStamp` class.
  ```
5. **Integrate the TimeStamp class with the Node and Edge classes**
  ```aider
  What prompt would you run to complete this task?
  - Update `graph_manager.py` to use the `TimeStamp` class for the `timestamps` field in `Node` and `Edge`.
  ```
6. **Test the integration**
  ```aider
  What prompt would you run to complete this task?
  - Create a new test file `test_timestamp.py` and add tests for the `TimeStamp` class.
  ```

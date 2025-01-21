import networkx as nx
import json
from networkx.readwrite import json_graph
from .graph_core import build_graph

def to_json_store(graph: nx.Graph, filepath='store.json') -> None:
    """Serialize the entire graph to a JSON file."""
    data = json_graph.node_link_data(graph)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Saved graph to {filepath}")

def from_json_store(filepath='store.json') -> nx.Graph:
    """Deserialize a graph from a JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File {filepath} not found. Building new graph.")
        return build_graph()
    graph = json_graph.node_link_graph(data)
    print(f"Loaded graph from {filepath}")
    return graph

def test_save_load():
    """Test saving and loading the graph."""
    print("Testing save/load")
    graph = build_graph()
    to_json_store(graph, filepath='store.json')
    restored_graph = from_json_store(filepath='store.json')
    assert nx.is_isomorphic(graph, restored_graph)

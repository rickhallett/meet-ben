from graphviz import Digraph
from core.pipeline import Pipeline
from IPython.display import Image


def visualize_pipeline(pipeline: Pipeline) -> Image:
    """
    Generates a visual representation of the pipeline flow with a modern look and returns a PNG image.

    Args:
        pipeline: The Pipeline object to visualize.

    Returns:
        An IPython Image object containing the PNG representation of the pipeline diagram.

    Raises:
        ImportError: If graphviz or IPython is not installed.

    Note:
        Requires both the Graphviz Python package and system package to be installed.
        Also requires IPython to be installed.
        Install dependencies with: pip install graphviz ipython
    """
    try:
        dot = Digraph(comment="Pipeline Visualization")
        _apply_graph_styling(dot)

        # Add nodes
        for node_config in pipeline.pipeline_schema.nodes:
            node_name = node_config.node.__name__
            if node_config.is_router:
                # Use diamond shape for router nodes
                dot.node(node_name, node_name, shape="diamond")
            else:
                dot.node(node_name, node_name)

        # Add edges
        start_node = pipeline.pipeline_schema.start.__name__
        dot.node("Event", "Event", shape="ellipse", fillcolor="#ececfd")
        dot.edge("Event", start_node, tailport="e", headport="w")

        for node_config in pipeline.pipeline_schema.nodes:
            node_name = node_config.node.__name__
            for connection in node_config.connections:
                dot.edge(node_name, connection.__name__, tailport="e", headport="w")

        # Render the graph to PNG and return as Image
        png_data = dot.pipe(format="png")
        return Image(png_data)
    except ImportError:
        raise ImportError(
            "Please install graphviz and IPython: pip install graphviz ipython"
        )


def _apply_graph_styling(dot: Digraph) -> None:
    """
    Applies styling to the graph, nodes, and edges.

    Args:
        dot: The Digraph object to style.
    """
    dot.attr(
        rankdir="LR",
        bgcolor="#ffffff",
        fontname="Helvetica,Arial,sans-serif",
        pad="0.5",
        nodesep="0.5",
        ranksep="0.75",
    )

    dot.attr(
        "node",
        shape="rectangle",
        style="filled",
        fillcolor="#ececfd",
        color="#8e71d5",
        fontcolor="#333333",
        fontname="Helvetica",
        fontsize="12",
        height="0.6",
        width="1.5",
        penwidth="2",
    )

    dot.attr(
        "edge",
        color="#333333",
        penwidth="2",
        arrowsize="0.8",
        fontname="Helvetica",
        fontsize="10",
    )

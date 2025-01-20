"""
Demonstrates how to display a tree of files / directories with the Tree renderable.
Executable to pipe output to a file or LLM for repository structure analysis
"""

import os
import pathlib
import sys

from rich import print, console
from rich.filesize import decimal
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree
from rich.console import Console

def walk_directory(directory: pathlib.Path, tree: Tree) -> None:
    """Recursively build a Tree with directory contents."""
    # Sort dirs first then by filename
    paths = sorted(
        pathlib.Path(directory).iterdir(),
        key=lambda path: (path.is_file(), path.name.lower()),
    )
    for path in paths:
        # Remove hidden files
        if path.name.startswith(".") or path.name.startswith("__"):
            continue
        if path.is_dir():
            style = "dim" if path.name.startswith("__") else ""
            branch = tree.add(
                f"[bold magenta]:open_file_folder: [link file://{path}]{escape(path.name)}",
                style=style,
                guide_style=style,
            )
            walk_directory(path, branch)
        else:
            text_filename = Text(path.name, "green")
            text_filename.highlight_regex(r"\..*$", "bold red")
            text_filename.stylize(f"link file://{path}")
            file_size = path.stat().st_size
            text_filename.append(f" ({decimal(file_size)})", "blue")
            icon = "🐍 " if path.suffix == ".py" else "📄 "
            tree.add(Text(icon) + text_filename)


def generate_tree(directory_path: str) -> Tree:
    """Generate a Tree object for the given directory."""
    directory = os.path.abspath(directory_path)
    tree = Tree(
        f":open_file_folder: [link file://{directory}]{directory}",
        guide_style="bold bright_blue",
    )
    console = Console(record=True)

    walk_directory(pathlib.Path(directory), tree)
    
    # Create console and capture output
    console.print(tree)

    with open("tree.txt", "w") as f:
        f.write(console.export_text(clear=False))

    with open("tree.html", "w") as f:
        f.write(console.export_html())

def find_project_root(current_dir=os.getcwd()):
    root_markers = ['.git']
    while current_dir != '/':
        if any(os.path.exists(os.path.join(current_dir, marker)) for marker in root_markers):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    return os.getcwd()  # Fallback to current directory if no marker found

if __name__ == "__main__":
    try:
        directory = os.path.abspath(find_project_root())
    except IndexError:
        print("[b]Usage:[/] python tree.py <DIRECTORY>")
    else:
        generate_tree(directory)

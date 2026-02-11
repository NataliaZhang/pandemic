# python/core/io.py

import json
import networkx as nx
from pathlib import Path
from typing import List, Union, Optional, Tuple
from pathlib import Path

def load_graph_json(path=""):
    """
    Load an undirected graph from the project JSON format.

    Format:
    {
        "0": ["1", "3"],
        "1": ["0", "2"],
        ...
    }

    Returns:
        G (networkx.Graph) with integer node labels.

    Usage:
        G = load_graph_json("path/to/graph.json")
    """
    with open(path, "r") as f:
        data = json.load(f)

    G = nx.Graph()

    # Add all nodes first (important for isolated nodes)
    for node in data.keys():
        G.add_node(int(node))

    # Add edges
    for node, neighbors in data.items():
        u = int(node)
        for v in neighbors:
            G.add_edge(u, int(v))

    return G

def write_submission_txt(
    seeds_by_round: List[List[int]],
    out_path: Union[str, Path]
) -> None:
    """Write seeds in the required submission format.

    Each line contains exactly one node id.
    The file concatenates rounds in order: round1 k lines, round2 k lines, ...

    Example: for k=4, rounds=50 => total 200 lines.
    """
    out_path = Path(out_path)
    with out_path.open("w", encoding="utf-8") as f:
        for round_seeds in seeds_by_round:
            for s in round_seeds:
                f.write(f"{int(s)}\n")

def infer_from_filename(
    path: Union[str, Path]
) -> Tuple[Optional[str], Optional[int]]:
    """
    Try to infer competition style and k from filename like:
    RR.5.10.json
    J.20.31.json

    Returns:
        tuple[str | None, int | None]: competition style and k if parsed successfully,
        otherwise (None, None).
    """
    name = Path(path).stem  # remove .json
    parts = name.split(".")

    if len(parts) >= 2:
        try:
            return parts[0], int(parts[1])
        except ValueError:
            return None, None
    return None, None
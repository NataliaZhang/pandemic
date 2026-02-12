# python/core/io.py

import json
import networkx as nx
from pathlib import Path
from typing import List, Union, Optional, Tuple
from pathlib import Path

# Graph family labels
GRAPH_ER = "ER"
GRAPH_PA = "PA"
GRAPH_SSBM = "SSBM"
GRAPH_CALTECH = "Caltech"
GRAPH_SNAP = "SNAP"

GRAPH_UNKNOWN = None

def load_graph_json(path: Union[str, Path]) -> nx.Graph:
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

def _infer_family(comp: str, unique_id: int) -> Optional[str]:
    if comp == "RR":
        if 10 <= unique_id <= 17:
            return GRAPH_ER
        if 20 <= unique_id <= 27:
            return GRAPH_PA
        if 30 <= unique_id <= 37:
            return GRAPH_SSBM
        if 40 <= unique_id <= 47:
            return GRAPH_CALTECH
        if 50 <= unique_id <= 57:
            return GRAPH_SNAP
        return GRAPH_UNKNOWN

    if comp == "J":
        if 10 <= unique_id <= 15:
            return GRAPH_SSBM
        if 20 <= unique_id <= 25:
            return GRAPH_CALTECH
        if 30 <= unique_id <= 35:
            return GRAPH_SNAP
        return GRAPH_UNKNOWN

    return GRAPH_UNKNOWN

def infer_from_filename(
    path: Union[str, Path]
) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    """
    Parse filename like:
      RR.5.10.json
      J.20.31.json

    Returns:
      (style, k, family)

    If parsing fails:
      (None, None, None)
    """
    name = Path(path).stem  # remove .json
    parts = name.split(".")

    if len(parts) < 3:
        return None, None, None

    comp = parts[0].strip()
    try:
        k = int(parts[1])
        unique_id = int(parts[2])
    except ValueError:
        return None, None, None

    family = _infer_family(comp, unique_id)
    return comp, k, family
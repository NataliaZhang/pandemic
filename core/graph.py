from __future__ import annotations

import networkx as nx
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Optional, Union, Dict, Any
from pathlib import Path

from core.io import infer_from_filename

@dataclass(frozen=True)
class Graph:
    """Light wrapper over an undirected graph with cached adjacency and degrees.

    We assume nodes are labeled 0..n-1 (ints).
    """
    n: int
    neighbors: List[List[int]]
    degrees: List[int]

    comp: Optional[str] = None      # 'RR' or 'J'
    k: Optional[int] = None         # seeds per round
    family: Optional[str] = None    # 'ER', 'PA', 'SSBM', 'Caltech', 'SNAP'

    @staticmethod
    def from_networkx(G: nx.Graph, *, comp: Optional[str] = None, k: Optional[int] = None,
                      family: Optional[str] = None) -> "Graph":
        n = G.number_of_nodes()
        # assumes nodes 0..n-1
        neighbors = [list(G.neighbors(u)) for u in range(n)]
        degrees = [len(neighbors[u]) for u in range(n)]
        return Graph(
            n=n,
            neighbors=neighbors,
            degrees=degrees,
            comp=comp,
            k=k,
            family=family,
        )

    def validate_seeds(self, seeds: Sequence[int]) -> None:
        for s in seeds:
            if not (0 <= int(s) < self.n):
                raise ValueError(f"Seed out of range: {s} (n={self.n})")

def wrap_graph(
        G_nx:nx.Graph, 
        sourse_path: Union[str, Path],
        meta_override: Optional[Dict[str, Any]] = None
    ) -> Graph:
    """
    Convert a networkx graph to our Graph format, inferring metadata from the source path.
    """
    comp, k, family = infer_from_filename(sourse_path)
    if meta_override is not None:
        comp = meta_override.get("comp", comp)
        k = meta_override.get("k", k)
        family = meta_override.get("family", family)
    return Graph.from_networkx(G_nx, comp=comp, k=k, family=family)
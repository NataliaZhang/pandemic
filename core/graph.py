from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

import networkx as nx


@dataclass(frozen=True)
class Graph:
    """Light wrapper over an undirected graph with cached adjacency and degrees.

    We assume nodes are labeled 0..n-1 (ints).
    """
    n: int
    neighbors: List[List[int]]
    degrees: List[int]

    @staticmethod
    def from_networkx(G: nx.Graph) -> "Graph":
        # Ensure deterministic node ordering: 0..n-1
        nodes = sorted(G.nodes())
        if nodes and nodes[0] != 0:
            raise ValueError("Expected nodes labeled from 0.")
        if nodes and nodes[-1] != len(nodes) - 1:
            raise ValueError("Expected nodes labeled 0..n-1 with no gaps.")
        n = len(nodes)
        neighbors: List[List[int]] = [[] for _ in range(n)]
        degrees: List[int] = [0 for _ in range(n)]
        for u in nodes:
            nbrs = list(G.neighbors(u))
            neighbors[u] = nbrs
            degrees[u] = len(nbrs)
        return Graph(n=n, neighbors=neighbors, degrees=degrees)

    def validate_seeds(self, seeds: Sequence[int]) -> None:
        for s in seeds:
            if not (0 <= int(s) < self.n):
                raise ValueError(f"Seed out of range: {s} (n={self.n})")

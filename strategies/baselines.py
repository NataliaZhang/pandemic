from __future__ import annotations

from typing import List, Set, FrozenSet
import random

from core.graph import Graph
from strategies.base import Strategy, StrategyContext
from strategies.cluster import (
    ClusterBoundaryTakeoverSpectral,
    ClusterTopDegreeProportionalSpectral,
)

def get_strategy(name: str, **kwargs) -> Strategy:
    name = name.strip().lower()
    if name in {"random_k"}:
        return RandomK()
    if name in {"top_degree_random_tie"}:
        return TopDegreeRandomTie(**kwargs)
    if name in {"top_degree_no_repeat"}:
        return TopDegreeNoRepeat(**kwargs)
    if name in {"cluster_boundary_takeover_spectral", "edge_cluster"}:
        return ClusterBoundaryTakeoverSpectral(**kwargs)
    if name in {"cluster_top_degree_proportional_spectral", "degree_cluster"}:
        return ClusterTopDegreeProportionalSpectral(**kwargs)
    raise ValueError(f"Unknown strategy: {name}")

class RandomK(Strategy):
    name = "random_k"

    def select_seeds(self, G: Graph, k: int, rng: random.Random, ctx: StrategyContext) -> List[int]:
        if k > G.n:
            print(f"Warning: k={k} > n={G.n}, have repeat seeds.")
            return [rng.randint(0, G.n - 1) for _ in range(k)]
        return rng.sample(range(G.n), k)

class TopDegreeRandomTie(Strategy):
    """Pick k seeds by sampling uniformly from the top-M degree nodes.

    This matches the common baseline: 'randomly select among the highest-degree nodes'.
    """
    name = "top_degree_random_tie"

    def __init__(self, top_m):
        self.top_m = top_m

    def select_seeds(self, G: Graph, k: int, rng: random.Random, ctx: StrategyContext) -> List[int]:
        if k > G.n:
            raise ValueError(f"k={k} > n={G.n}")
        m = min(G.n, max(k, int(self.top_m * k)))
        # indices of nodes sorted by degree desc
        nodes_sorted = sorted(range(G.n), key=lambda u: G.degrees[u], reverse=True)
        pool = nodes_sorted[:m]
        if k > len(pool):
            return pool[:]  # fallback
        return rng.sample(pool, k)

    
class TopDegreeNoRepeat(Strategy):
    """

    """
    name = "top_degree_no_repeat"
    def __init__(self, top_m):
        self.top_m = top_m

    def select_seeds(self, G: Graph, k: int, rng: random.Random, ctx: StrategyContext) -> List[int]:
        raise NotImplementedError("This strategy has not been implemented yet.")
      
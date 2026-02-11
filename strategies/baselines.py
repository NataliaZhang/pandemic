from __future__ import annotations

from typing import List
import random

from core.graph import Graph
from strategies.base import Strategy, StrategyContext


class RandomK(Strategy):
    name = "random_k"

    def select_seeds(self, G: Graph, k: int, rng: random.Random, ctx: StrategyContext) -> List[int]:
        if k > G.n:
            raise ValueError(f"k={k} > n={G.n}")
        return rng.sample(range(G.n), k)


class TopDegreeRandomTie(Strategy):
    """Pick k seeds by sampling uniformly from the top-M degree nodes.

    This matches the common baseline: 'randomly select among the highest-degree nodes'.
    """
    name = "top_degree_random_tie"

    def __init__(self, top_m: int = 50):
        self.top_m = top_m

    def select_seeds(self, G: Graph, k: int, rng: random.Random, ctx: StrategyContext) -> List[int]:
        if k > G.n:
            raise ValueError(f"k={k} > n={G.n}")
        m = min(self.top_m, G.n)
        # indices of nodes sorted by degree desc
        nodes_sorted = sorted(range(G.n), key=lambda u: G.degrees[u], reverse=True)
        pool = nodes_sorted[:m]
        if k > len(pool):
            return pool[:]  # fallback
        return rng.sample(pool, k)


def get_strategy(name: str) -> Strategy:
    name = name.strip().lower()
    if name in {"random", "random_k"}:
        return RandomK()
    if name in {"top_degree", "top_degree_random", "top_degree_random_tie"}:
        return TopDegreeRandomTie()
    raise ValueError(f"Unknown strategy: {name}")

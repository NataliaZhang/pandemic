from __future__ import annotations

from typing import List, Set, FrozenSet
import random

from core.graph import Graph
from strategies.base import Strategy, StrategyContext

def get_strategy(name: str, **kwargs) -> Strategy:
    name = name.strip().lower()
    if name in {"random_k"}:
        return RandomK()
    if name in {"top_degree_random_tie"}:
        return TopDegreeRandomTie(**kwargs)
    if name in {"top_degree_no_repeat"}:
        return TopDegreeNoRepeat(**kwargs)
    # TODO: add more baselines like degree discount, greedy, etc.
    raise ValueError(f"Unknown strategy: {name}")

class RandomK(Strategy):
    name = "random_k"

    def select_seeds(self, G: Graph, k: int, rng: random.Random, ctx: StrategyContext) -> List[int]:
        if k > G.n:
            print(f"Warning: k={k} > n={G.n}, have repeat seeds.")
            return [rng.randint(0, G.n - 1) for _ in range(k)]
        return rng.sample(range(G.n), k)

    def select_seeds_50(
        self, G: Graph, k: int, rng: random.Random, ctx: StrategyContext, rounds: int = 50
    ) -> List[List[int]]:
        seen: Set[FrozenSet[int]] = set()
        out: List[List[int]] = []
        for _ in range(rounds):
            # try a few times to avoid exact repeats
            for _attempt in range(5):
                seeds = self.select_seeds(G, k, rng, ctx)
                key = frozenset(seeds)
                if key not in seen:
                    seen.add(key)
                    out.append(seeds)
                    break
            else:
                # fallback: accept repetition if graph is small / k is large
                out.append(self.select_seeds(G, k, rng, ctx))
        return out

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

    def select_seeds_50(
        self, G: Graph, k: int, rng: random.Random, ctx: StrategyContext, rounds: int = 50
    ) -> List[List[int]]:
        seen: Set[FrozenSet[int]] = set()
        out: List[List[int]] = []
        for _ in range(rounds):
            for _attempt in range(10):
                seeds = self.select_seeds(G, k, rng, ctx)
                key = frozenset(seeds)
                if key not in seen:
                    seen.add(key)
                    out.append(seeds)
                    break
            else:
                out.append(self.select_seeds(G, k, rng, ctx))
        return out
    
class TopDegreeNoRepeat(Strategy):
    """
    Each round:
      - form a pool of size m from the highest-degree nodes that have NOT been used before
      - sample k seeds uniformly from that pool
    Global constraint:
      - once a node has been used in any previous round, it cannot be used again
      - this constraint is lifted only after ALL nodes in the graph have been used at least once
        (then we reset and start over)

    Note: This strategy is defined at the 50-round level only.
    """
    name = "top_degree_no_repeat"
    def __init__(self, top_m):
        self.top_m = top_m

    def select_seeds(self, G: Graph, k: int, rng: random.Random, ctx: StrategyContext) -> List[int]:
        raise NotImplementedError("This strategy is defined at the 50-round level only.")

    def select_seeds_50(
        self,
        G: Graph,
        k: int,
        rng: random.Random,
        ctx: StrategyContext,
        rounds: int = 50
    ) -> List[List[int]]:
        if k > G.n:
            raise ValueError(f"k={k} > n={G.n}")
        if rounds <= 0:
            return []

        # Fixed pool ratio (as you requested)
        m = min(G.n, max(k, int(self.top_m * k)))

        # Sort ONCE by degree desc
        nodes_sorted = sorted(range(G.n), key=lambda u: G.degrees[u], reverse=True)

        # Map node -> position in sorted list
        pos_of = [0] * G.n
        for i, u in enumerate(nodes_sorted):
            pos_of[u] = i

        def build_linked_list():
            """Initialize a doubly-linked list over positions 0..n-1 (all unused)."""
            n = G.n
            next_pos = list(range(1, n)) + [-1]
            prev_pos = [-1] + list(range(0, n - 1))
            head = 0
            return next_pos, prev_pos, head, n  # also track unused_count

        def remove_pos(p, next_pos, prev_pos):
            """Splice position p out of the linked list. Return new head."""
            nonlocal head
            a = prev_pos[p]
            b = next_pos[p]
            if a != -1:
                next_pos[a] = b
            else:
                head = b  # removing head
            if b != -1:
                prev_pos[b] = a
            prev_pos[p] = -2  # mark removed
            next_pos[p] = -2

        next_pos, prev_pos, head, unused_count = build_linked_list()
        used: Set[int] = set()  # optional; used only for sanity/debugging

        out: List[List[int]] = []

        for _ in range(rounds):
            # If not enough unused nodes to fill a round, reset (start over)
            if unused_count < k:
                next_pos, prev_pos, head, unused_count = build_linked_list()
                used.clear()

            # Collect top-m unused nodes by walking from head
            pool: List[int] = []
            p = head
            steps = 0
            while p != -1 and steps < m:
                u = nodes_sorted[p]
                pool.append(u)
                p = next_pos[p]
                steps += 1

            # If pool is smaller than k (rare; only if n < k, already guarded),
            # or if list is too short, reset and rebuild pool once.
            if len(pool) < k:
                next_pos, prev_pos, head, unused_count = build_linked_list()
                used.clear()
                pool = []
                p = head
                steps = 0
                while p != -1 and steps < m:
                    pool.append(nodes_sorted[p])
                    p = next_pos[p]
                    steps += 1

            seeds = rng.sample(pool, k)
            out.append(seeds)

            # Remove chosen nodes globally (without replacement until reset)
            for u in seeds:
                if u in used:
                    # Should not happen before reset; keep as a guard.
                    continue
                used.add(u)
                p = pos_of[u]
                # If already removed, skip (shouldn't happen)
                if prev_pos[p] == -2:
                    continue
                remove_pos(p, next_pos, prev_pos)
                unused_count -= 1

        return out
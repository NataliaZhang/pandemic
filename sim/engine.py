from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import random

from core.graph import Graph
from sim.rules import UNCOLORED, apply_seed_conflicts, update_node


@dataclass
class SimulationResult:
    final_colors: List[int]          # length n, values in {-1, 0..T-1}
    num_generations: int             # number of update generations executed
    scores: List[int]                # nodes owned per team
    history: Optional[List[List[int]]] = None  # optional snapshots per generation


def simulate(
    G: Graph,
    seeds_by_team: List[List[int]],
    *,
    record_history: bool = False,
    rng: Optional[random.Random] = None,
) -> SimulationResult:
    """Run competing epidemic simulation until stable (or random cap like TA).

    seeds_by_team: list of seed lists, one per team.
                   Team ids are 0..T-1 by list index.
    """
    if rng is None:
        rng = random.Random()

    T = len(seeds_by_team)
    # Resolve conflicts (nobody gets collided seed nodes)
    seeds_by_team = apply_seed_conflicts(seeds_by_team)

    colors = [UNCOLORED] * G.n
    for t, seeds in enumerate(seeds_by_team):
        for s in seeds:
            colors[int(s)] = t

    generation = 1
    prev: Optional[List[int]] = None
    max_rounds = rng.randint(100, 200)  # TA uses randint(100, 200)

    history: Optional[List[List[int]]] = [] if record_history else None

    def is_stable(gen: int, max_r: int, prev_state: Optional[List[int]], curr_state: List[int]) -> bool:
        if gen <= 1 or prev_state is None:
            return False
        if gen == max_r:
            return True
        return prev_state == curr_state

    while not is_stable(generation, max_rounds, prev, colors):
        prev = colors[:]  # snapshot
        if record_history:
            history.append(prev[:])

        for u in range(G.n):
            changed, new_color = update_node(u, prev, G.neighbors[u])
            if changed:
                colors[u] = new_color

        generation += 1

    # final snapshot (optional, so animation ends at fixed point)
    if record_history and history is not None:
        history.append(colors[:])

    scores = [0] * T
    for c in colors:
        if c != UNCOLORED:
            scores[c] += 1

    return SimulationResult(
        final_colors=colors,
        num_generations=generation,
        scores=scores,
        history=history,
    )

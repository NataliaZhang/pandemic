from __future__ import annotations

from collections import Counter
from typing import List, Tuple


UNCOLORED = -1


def update_node(
    node: int,
    prev_colors: List[int],
    neighbors: List[int],
) -> Tuple[bool, int]:
    """Compute next color for a node, following the TA simulator logic.

    - Only colored neighbors vote (weight 1).
    - If the node is currently colored, it adds 1.5 votes for itself.
    - If some color has a strict majority, node switches/adopts that color.
    - Else, it stays as-is.

    IMPORTANT: This matches the TA-provided sim.py exactly, including the
    majority threshold being based on (# colored neighbors) / 2.0.
    """
    colored_nbr_colors = [prev_colors[v] for v in neighbors if prev_colors[v] != UNCOLORED]
    team_count = Counter(colored_nbr_colors)

    curr = prev_colors[node]
    if curr != UNCOLORED:
        team_count[curr] += 1.5

    most_common = team_count.most_common(1)
    if most_common:
        top_color, top_votes = most_common[0]
        # TA logic: compare to half the number of colored neighbors (not total vote weight)
        if top_votes > (len(colored_nbr_colors) / 2.0):
            return True, int(top_color)

    return False, curr


def apply_seed_conflicts(seeds_by_team: List[List[int]]) -> List[List[int]]:
    """Resolve seed conflicts: if multiple teams pick the same node, nobody gets it.

    Returns filtered seeds per team with conflicted nodes removed.
    """
    counts = Counter()
    for seeds in seeds_by_team:
        counts.update(int(s) for s in seeds)

    filtered: List[List[int]] = []
    for seeds in seeds_by_team:
        filtered.append([int(s) for s in seeds if counts[int(s)] == 1])
    return filtered

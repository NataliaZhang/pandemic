from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import random

from core.graph import Graph


@dataclass
class StrategyContext:
    """Optional metadata passed into strategies."""
    graph_type: Optional[str] = None
    extras: Optional[Dict[str, Any]] = None


class Strategy:
    """Seed-selection strategy interface."""

    name: str = "strategy"

    def select_seeds(self, G: Graph, k: int, rng: random.Random, ctx: StrategyContext) -> List[int]:
        raise NotImplementedError

    def select_seeds_50(self, G: Graph, k: int, rng: random.Random, ctx: StrategyContext, rounds: int = 50) -> List[List[int]]:
        """Select seeds for multiple rounds."""
        return [self.select_seeds(G, k, rng, ctx) for _ in range(rounds)]

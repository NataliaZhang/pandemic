#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
from pathlib import Path

from core.io import load_graph_json, write_submission_txt, infer_k_from_filename
from core.graph import Graph
from strategies.base import StrategyContext
from strategies.baselines import get_strategy


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Pandemaniac seed submission file.")
    parser.add_argument("--graph", required=True, type=str, help="Path to input JSON graph.")
    parser.add_argument("--k", type=int, default=None,
    help="Number of seeds per round. If omitted, inferred from filename (default fallback: 5).",
)
    parser.add_argument("--rounds", default=50, type=int, help="Number of rounds (default: 50).")
    parser.add_argument("--strategy", default="top_degree_random_tie", type=str, help="Strategy name.")
    parser.add_argument("--seed", default=0, type=int, help="RNG seed for reproducibility.")
    parser.add_argument("--out", required=True, type=str, help="Output submission .txt path.")
    args = parser.parse_args()

    G_nx = load_graph_json(args.graph)
    G = Graph.from_networkx(G_nx)

    strat = get_strategy(args.strategy)
    rng = random.Random(args.seed)
    ctx = StrategyContext()

    # Infer k from filename if not provided
    k_inferred = infer_k_from_filename(args.graph)

    if args.k is not None:
        k = args.k
        if k_inferred is not None and k != k_inferred:
            print(f"Warning: Provided k={k} differs from inferred k={k_inferred} from filename.")
    elif k_inferred is not None:
        k = k_inferred
        print(f"Inferred k={k} from filename.")
    else:
        k = 5  # default fallback
        print(f"Could not infer k from filename. Using default k={k}.")

    seeds_by_round = strat.select_seeds_50(G, k, rng, ctx, rounds=args.rounds)

    # Basic validation
    for r, seeds in enumerate(seeds_by_round):
        if len(seeds) != k:
            raise ValueError(f"Round {r}: expected {k} seeds, got {len(seeds)}")
        G.validate_seeds(seeds)

    write_submission_txt(seeds_by_round, args.out)
    print(f"Wrote {args.rounds * k} seeds to {Path(args.out).resolve()}")

if __name__ == "__main__":
    main()

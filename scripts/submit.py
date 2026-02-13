#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
from pathlib import Path

from core.io import load_graph_json, write_submission_txt, infer_from_filename
from core.graph import Graph, wrap_graph
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
    parser.add_argument("--out-dir", default="submissions", type=str, help="Output directory for submission .txt files.")

    # top_degree stratrgy 
    parser.add_argument("--top-m", type=float, default=1, help="Top-M pool size ratio for top_degree_random_tie and top_degree_avoid. (>=1)")

    args = parser.parse_args()

    G_nx = load_graph_json(args.graph)
    G = wrap_graph(G_nx, args.graph)    # metadata has been inferred here: comp, k, family

    if args.strategy == "top_degree_random_tie" or args.strategy == "top_degree_avoid":
        strat = get_strategy(args.strategy, top_m=args.top_m)
    else:
        strat = get_strategy(args.strategy)
    rng = random.Random(args.seed)
    ctx = StrategyContext()

    is_generated = G.family is not None and G.comp is None

    if is_generated:
        # Test mode: do not infer k from filename
        if args.k is None:
            G = wrap_graph(G_nx, args.graph, meta_override={"k": 5})
            print(f"Generated graph detected. Using default k={G.k}.")
        else:
            G = wrap_graph(G_nx, args.graph, meta_override={"k": args.k})
    else:
        # Competition mode: infer k, allow override
        if args.k is not None:
            if G.k is not None and args.k != G.k:
                print(f"Warning: Provided k={args.k} differs from inferred k={G.k} from filename.")
            G = wrap_graph(G_nx, args.graph, meta_override={"k": args.k})  # override for validation
        elif G.k is not None:
            k = G.k
            print(f"Inferred k={k} from filename.")
        else:
            G = wrap_graph(G_nx, args.graph, meta_override={"k": 5})  # default fallback
            print(f"Could not infer k from filename. Using default k={G.k}.")

    seeds_by_round = strat.select_seeds_50(G, G.k, rng, ctx, rounds=args.rounds)

    # Basic validation
    for r, seeds in enumerate(seeds_by_round):
        if len(seeds) != G.k:
            raise ValueError(f"Round {r}: expected {G.k} seeds, got {len(seeds)}")
        G.validate_seeds(seeds)

    if args.strategy == "top_degree_avoid" or args.strategy == "top_degree_random_tie":
        out_filename = f"{Path(args.graph).stem}/{args.strategy}_topm{args.top_m}_seed{args.seed}.txt"
    else:
        out_filename = f"{Path(args.graph).stem}/{args.strategy}_seed{args.seed}.txt"
    out_path = Path(args.out_dir) / out_filename
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_submission_txt(seeds_by_round, out_path)
    print(f"Wrote {args.rounds * G.k} seeds to {out_path.resolve()}")

if __name__ == "__main__":
    main()

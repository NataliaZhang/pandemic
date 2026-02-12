#!/usr/bin/env python3
import argparse
from pathlib import Path
from typing import List, Optional, Tuple

import random

from core.io import load_graph_json, infer_from_filename
from core.graph import Graph, wrap_graph
from sim.engine import simulate


def read_submission_txt(path: str, k: int, rounds: int = 50) -> List[List[int]]:
    """
    Read a submission file with exactly (k * rounds) lines, each a node id.
    Returns: seeds_by_round[round_idx] = list of k ints
    """
    p = Path(path)
    lines = [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip() != ""]
    nums = [int(x) for x in lines]

    expected = k * rounds
    if len(nums) != expected:
        raise ValueError(f"{path}: expected exactly {expected} lines, got {len(nums)}")

    out: List[List[int]] = []
    for r in range(rounds):
        out.append(nums[r * k : (r + 1) * k])
    return out

def infer_graph_path_from_submission(sub_path: str) -> Optional[str]:
    """
    Given submission path like:
        submissions/RR.5.1/top_degree_no_repeat_seed0.txt
        Expect structure: submissions/<graph_name>/<file.txt>

    Return:
        graphs/RR.5.1.json
    """
    p = Path(sub_path)
    if p.parent is None:
        return None
    graph_name = p.parent.name
    if not graph_name:
        return None
    return str(Path("graphs") / f"{graph_name}.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate two submissions on the same graph (50 rounds).")
    parser.add_argument("--sub1", required=True, type=str, help="Submission txt for team 0.")
    parser.add_argument("--sub2", required=True, type=str, help="Submission txt for team 1.")
    parser.add_argument("--graph", default=None, type=str, help="Graph JSON path (optional; inferred if omitted).")
    parser.add_argument("--rounds", default=50, type=int, help="Number of rounds (default: 50).")
    parser.add_argument("--k", default=None, type=int, help="Seeds per round (optional; inferred from filename).")
    parser.add_argument(
        "--seed",
        default=0,
        type=int,
        help="RNG seed to drive TA-style random max-iteration cap inside simulate().",
    )
    args = parser.parse_args()

    # Graph path inference
    graph_path = args.graph
    if graph_path is None:
        graph_path_1 = infer_graph_path_from_submission(args.sub1) 
        graph_path_2 = infer_graph_path_from_submission(args.sub2)
        if graph_path_1 == graph_path_2:
            graph_path = graph_path_1
        else:
            print(f"[Warn] Inferred graph paths differ: {graph_path_1} vs {graph_path_2}. Please specify --graph explicitly.")
    if graph_path is None:
        raise ValueError("Could not infer graph path; please pass --graph explicitly.")

    # Infer k from filename unless user overrides
    comp, k_inferred, family = infer_from_filename(graph_path)
    if args.k is not None:
        k = args.k
        if k_inferred is not None and k != k_inferred:
            print(
                f"[Warn] --k={k} differs from inferred k={k_inferred} from {Path(graph_path).name}. Using --k."
            )
    else:
        k = k_inferred if k_inferred is not None else 5
        if k_inferred is None:
            print("[Info] Could not infer k from filename. Using default k=5.")
        else:
            print(f"[Info] Inferred k={k} from filename.")

    # Load graph
    G_nx = load_graph_json(graph_path)
    G = wrap_graph(G_nx, graph_path)

    # Read submissions
    seeds1 = read_submission_txt(args.sub1, k=k, rounds=args.rounds)
    seeds2 = read_submission_txt(args.sub2, k=k, rounds=args.rounds)

    # Validate seeds (in-range, unique within a round)
    for r in range(args.rounds):
        G.validate_seeds(seeds1[r])
        G.validate_seeds(seeds2[r])

    rng = random.Random(args.seed)

    team1_wins = 0
    team2_wins = 0
    ties = 0
    total1 = 0
    total2 = 0

    for r in range(args.rounds):
        res = simulate(
            G,
            seeds_by_team=[seeds1[r], seeds2[r]],
            record_history=False,
            rng=rng,  # important: drives the TA-style randint cap per round
        )
        s1, s2 = res.scores[0], res.scores[1]
        total1 += s1
        total2 += s2

        if s1 > s2:
            team1_wins += 1
        elif s2 > s1:
            team2_wins += 1
        else:
            ties += 1

        # print(f"Round {r+1:02d}: team0={s1:4d} team1={s2:4d}  gens={res.num_generations}")

    print("\n=== Summary ===")
    print(f"Graph: {graph_path}")
    print(f"k={k}, rounds={args.rounds}")
    print(f"Totals (sum of per-round node counts): team0={total1}, team1={total2}")
    print(f"Round wins: team0={team1_wins}, team1={team2_wins}, ties={ties}")


if __name__ == "__main__":
    main()
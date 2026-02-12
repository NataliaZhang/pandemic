#!/usr/bin/env python3
import argparse
from pathlib import Path
from typing import List, Optional

import random

from core.io import load_graph_json, infer_from_filename
from core.graph import wrap_graph
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
    submissions/<graph_name>/<file>.txt

    Prefer:
      graphs/<graph_name>.json
    If not exists:
      graphs/gen/<graph_name>.json
    """
    p = Path(sub_path)
    graph_name = p.parent.name if p.parent else None
    if not graph_name:
        return None

    cand1 = Path("graphs") / f"{graph_name}.json"
    if cand1.exists():
        return str(cand1)

    cand2 = Path("graphs/gen") / f"{graph_name}.json"
    if cand2.exists():
        return str(cand2)

    print(f"[Warn] Could not infer graph path from submission {sub_path}. Checked {cand1} and {cand2}.")
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simulate 2-5 submissions competing on the same graph (50 rounds)."
    )

    parser.add_argument("--sub1", required=True, type=str, help="Submission txt for team 0.")
    parser.add_argument("--sub2", required=True, type=str, help="Submission txt for team 1.")
    parser.add_argument("--sub3", default=None, type=str, help="Submission txt for team 2 (optional).")
    parser.add_argument("--sub4", default=None, type=str, help="Submission txt for team 3 (optional).")
    parser.add_argument("--sub5", default=None, type=str, help="Submission txt for team 4 (optional).")
    parser.add_argument("--sub6", default=None, type=str, help="Submission txt for team 5 (optional).")

    parser.add_argument("--graph", default=None, type=str, help="Graph JSON path (optional; inferred if omitted).")
    parser.add_argument("--rounds", default=50, type=int, help="Number of rounds (default: 50).")
    parser.add_argument("--k", default=None, type=int, help="Seeds per round (optional; inferred from filename).")
    parser.add_argument("--seed", default=0, type=int, help="RNG seed for random cap inside simulate().")
    args = parser.parse_args()

    # Gather submissions (2..6)
    subs = [args.sub1, args.sub2]
    for s in [args.sub3, args.sub4, args.sub5, args.sub6]:
        if s is not None and str(s).strip() != "":
            subs.append(s)

    if len(subs) < 2:
        raise ValueError("Need at least 2 submissions.")
    if len(subs) > 6:
        raise ValueError("Allow at most 6 submissions.")

    # Infer graph path
    graph_path = args.graph
    if graph_path is None:
        inferred_paths = [infer_graph_path_from_submission(s) for s in subs]
        inferred_paths = [p for p in inferred_paths if p is not None]
        if not inferred_paths:
            graph_path = None
        else:
            # all must match
            if len(set(inferred_paths)) == 1:
                graph_path = inferred_paths[0]
            else:
                print(f"[Warn] Inferred graph paths differ across submissions: {sorted(set(inferred_paths))}")
                graph_path = None

    if graph_path is None:
        raise ValueError("Could not infer graph path; please pass --graph explicitly.")

    # Infer k from filename unless user overrides
    comp, k_inferred, family = infer_from_filename(graph_path)
    if args.k is not None:
        k = args.k
        if k_inferred is not None and k != k_inferred:
            print(f"[Warn] --k={k} differs from inferred k={k_inferred} from {Path(graph_path).name}. Using --k.")
    else:
        k = k_inferred if k_inferred is not None else 5
        if k_inferred is None:
            print("[Info] Could not infer k from filename. Using default k=5.")
        else:
            print(f"[Info] Inferred k={k} from filename.")

    # Load graph
    G_nx = load_graph_json(graph_path)
    G = wrap_graph(G_nx, graph_path)

    # Read seeds for each team: seeds_by_team[team][round] = [k seeds]
    seeds_by_team: List[List[List[int]]] = []
    for s in subs:
        seeds_by_team.append(read_submission_txt(s, k=k, rounds=args.rounds))

    # Validate seeds
    for t in range(len(subs)):
        for r in range(args.rounds):
            G.validate_seeds(seeds_by_team[t][r])

    rng = random.Random(args.seed)

    T = len(subs)
    totals = [0] * T
    round_wins = [0] * T
    tie_rounds = 0

    for r in range(args.rounds):
        seeds_this_round = [seeds_by_team[t][r] for t in range(T)]
        res = simulate(G, seeds_by_team=seeds_this_round, record_history=False, rng=rng)

        # accumulate scores
        for t in range(T):
            totals[t] += res.scores[t]

        # determine round winner(s)
        max_score = max(res.scores)
        winners = [t for t, sc in enumerate(res.scores) if sc == max_score]
        if len(winners) == 1:
            round_wins[winners[0]] += 1
        else:
            tie_rounds += 1

    # overall winner: most round wins, break ties by totals
    max_round_wins = max(round_wins)
    best = [t for t in range(T) if round_wins[t] == max_round_wins]
    if len(best) == 1:
        overall = best[0]
    else:
        max_total = max(totals[t] for t in best)
        best2 = [t for t in best if totals[t] == max_total]
        overall = best2[0]  # deterministic pick

    print("\n=== Summary ===")
    print(f"Graph: {graph_path}")
    print(f"Teams: {T}")
    print(f"k={k}, rounds={args.rounds}")
    for t in range(T):
        print(f"team{t}: total={totals[t]}  round_wins={round_wins[t]}  sub={subs[t]}")
    print(f"tie_rounds={tie_rounds}")
    print(f"Overall winner: team{overall}")


if __name__ == "__main__":
    main()
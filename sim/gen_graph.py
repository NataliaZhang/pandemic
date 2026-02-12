import argparse
import math
from pathlib import Path
from typing import Optional

import networkx as nx

from core.io import save_graph_json

def gen_ER(n: int, p: Optional[float], seed: int) -> nx.Graph:
    """
    Erdos-Renyi random graph G(n,p).
    """
    if p is None:
        lo = 1.0 / n
        hi = math.log(n) / n
        p = (lo + hi) / 2
    return nx.gnp_random_graph(n, p, seed=seed, directed=False)

def gen_PA(n: int, m: int, seed: int) -> nx.Graph:
    """
    Preferential attachment: Barabasi-Albert model.
    m = edges per new node (m>=1 and m<n).
    """
    if m < 1 or m >= n:
        raise ValueError(f"Invalid m={m} for PA graph with n={n}. Must have 1 <= m < n.")
    return nx.barabasi_albert_graph(n, m, seed=seed)

def gen_ssbm(n: int, k:int, p_in: float, p_out: float, seed: int) -> nx.Graph:
    """
    Symmetric Stochastic Block Model with k equal-sized communities.
    p_in = edge probability within community
    p_out = edge probability across communities
    """
    if n % k != 0:
        raise ValueError(f"n={n} must be divisible by k={k} for equal-sized communities.")
    sizes = [n // k] * k
    probs = [[p_in if i == j else p_out for j in range(k)] for i in range(k)]
    return nx.stochastic_block_model(sizes, probs, seed=seed)

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate test graphs into graphs/gen/*.json")
    parser.add_argument("--type", required=True, choices=["ER", "PA", "SSBM"], help="Graph family to generate.")
    parser.add_argument("--n", required=True, type=int, help="Number of nodes.")
    parser.add_argument("--seed", default=0, type=int, help="Random seed.")
    parser.add_argument("--out-dir", default="graphs/gen", type=str, help="Output directory.")

    # ER params
    parser.add_argument("--p", default=None, type=float, help="ER edge probability (optional).")

    # PA params
    parser.add_argument("--m", default=1, type=int, help="PA parameter: edges per new node (default 1).")

    # SSBM params
    parser.add_argument("--k-blocks", default=5, type=int, help="SSBM blocks (default 5).")
    parser.add_argument("--p-in", default=0.05, type=float, help="SSBM intra-block p (default 0.05).")
    parser.add_argument("--p-out", default=0.005, type=float, help="SSBM inter-block p (default 0.005).")

    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)


    if args.type == "ER":
        G = gen_ER(args.n, args.p, args.seed)
        default_name = f"ER_n{args.n}_p{(args.p if args.p is not None else 'auto')}_seed{args.seed}"
    elif args.type == "PA":
        G = gen_PA(args.n, args.m, args.seed)
        default_name = f"PA_n{args.n}_m{args.m}_seed{args.seed}"
    else:
        G = gen_ssbm(args.n, args.k_blocks, args.p_in, args.p_out, args.seed)
        default_name = f"SSBM_n{args.n}_k{args.k_blocks}_pin{args.p_in}_pout{args.p_out}_seed{args.seed}"

    
    out_path = out_dir / f"{default_name}.json"
    save_graph_json(G, out_path)
    print(f"Wrote {args.type} graph to {out_path}")


if __name__ == "__main__":
    main()
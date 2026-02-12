from __future__ import annotations

from typing import Dict, List, Set, FrozenSet, Tuple
import random
import numpy as np

from core.graph import Graph
from strategies.base import Strategy, StrategyContext

from typing import List, Set, FrozenSet

# max_clusters should be somehow related to k and number of rounds
# select_seeds_50 is unsure I just used method Natalia wrote in baseline 
# problem with current method: 50 runs cannot get different answers 
# but I am not sure how to do that

def _select_seeds_50_unique(
    strategy: Strategy,
    G: Graph,
    k: int,
    rng: random.Random,
    ctx: StrategyContext,
    rounds: int = 50,
    max_attempts: int = 30,
    max_jaccard: float = 0.85,   # allow overlap, but avoid near-identical sets
) -> List[List[int]]:
    seen_exact: Set[FrozenSet[int]] = set()
    out: List[List[int]] = []
    seen: Set[FrozenSet[int]] = set()
    out: List[List[int]] = []
    
    for _ in range(rounds):
        for _attempt in range(max_attempts):
            seeds = strategy.select_seeds(G, k, rng, ctx)
            key = frozenset(seeds)
            if key not in seen:
                seen.add(key)
                out.append(seeds)
                break
        else:
            out.append(strategy.select_seeds(G, k, rng, ctx))
    return out

def _spectral_clusters_sorted_fiedler(
    G: Graph,
    rng: random.Random,
    min_cluster_size: int = 20,
    max_clusters: int = 50,
    normalized: bool = True,
) -> List[List[int]]:
    """
    Recursive spectral bisection:
      - Build Laplacian (normalized by default)
      - Take Fiedler vector (2nd smallest eigenvector)
      - Sort nodes by that vector
      - Sweep cut to minimize conductance
      - Recurse on both sides until stopping criteria

    Returns: list of clusters (each is a list of node ids in original graph).
    """
    neighbors = G.neighbors
    degrees = G.degrees

    # includes nodes in nodes and all edges from original graph whose endpoints are both in S
    def induced_subgraph(nodes: List[int]) -> Tuple[np.ndarray, np.ndarray, List[int]]:
        """Return (A, deg, nodes) for the induced subgraph on 'nodes'."""
        idx = {u: i for i, u in enumerate(nodes)} # dictionary {nodes: idx}
        n2 = len(nodes)
        A = np.zeros((n2, n2), dtype=np.float64)
        deg = np.zeros(n2, dtype=np.float64)
        for i, u in enumerate(nodes):
            for v in neighbors[u]:
                j = idx.get(v)
                if j is not None:
                    A[i, j] = 1.0
            deg[i] = A[i].sum()
        return A, deg, nodes

    # Given an induced subgraph’s adjacency matrix A and its degree vector deg
    # returns order of nodes based on the Fiedler vector
    def fiedler_order(A: np.ndarray, deg: np.ndarray) -> np.ndarray:
        n2 = A.shape[0]
        if n2 <= 2:
            return np.arange(n2)

        if normalized:
            # L_sym = I - D^{-1/2} A D^{-1/2}
            with np.errstate(divide="ignore"):
                inv_sqrt = np.where(deg > 0, 1.0 / np.sqrt(deg), 0.0)
            D_inv_sqrt = np.diag(inv_sqrt)
            L = np.eye(n2) - D_inv_sqrt @ A @ D_inv_sqrt
        else:
            # L = D - A
            L = np.diag(deg) - A

        # w: eigenvalues sorted in ascending order
        # V: eigenvectors as columns (V[:, i] corresponds to eigenvalue w[i])
        w, V = np.linalg.eigh(L)  # symmetric

        # choose the smallest nonzero eigenvector:
        # for connected components, eigenvalue 0 multiplicity = #components.
        eps = 1e-10
        idx_nonzero = np.where(w > eps)[0]
        if len(idx_nonzero) == 0:
            # fully disconnected; arbitrary order
            return np.arange(n2)
        vec = V[:, idx_nonzero[0]]  # lowest nonzero
        return np.argsort(vec)

    def best_sweep_cut(nodes: List[int], order_local: np.ndarray) -> int:
        """
        Given local node ordering, pick cut index t minimizing conductance over prefix S_t.
        Returns t in [1, n-1].
        """
        n2 = len(nodes)
        if n2 <= 2:
            return 1

        local_of: Dict[int, int] = {u: i for i, u in enumerate(nodes)}
        inS = np.zeros(n2, dtype=bool)
        volS = 0
        total_vol = 0
        for u in nodes:
            total_vol += degrees[u]

        cut = 0
        best_phi = float("inf")
        best_t = 1

        # We update cut incrementally as we add one node at a time.
        for t in range(1, n2):
            u_local = int(order_local[t - 1])
            u = nodes[u_local]
            inS[u_local] = True
            volS += degrees[u]

            for v in neighbors[u]:
                j = local_of.get(v)
                if j is None:
                    continue
                if inS[j]:
                    cut -= 1
                else:
                    cut += 1

            volT = total_vol - volS
            denom = min(volS, volT)
            if denom <= 0:
                continue
            phi = cut / denom
            if phi < best_phi:
                best_phi = phi
                best_t = t
            else:
                return best_t

        return best_t

    # recursive splitting
    clusters: List[List[int]] = [list(range(G.n))]
    out: List[List[int]] = []

    while clusters and len(out) + len(clusters) < max_clusters:
        clusters.sort(key=len, reverse=True)
        nodes = clusters.pop(0)

        if len(nodes) < 2 * min_cluster_size:
            out.append(nodes)
            continue

        A, deg_local, nodes_ref = induced_subgraph(nodes)
        order_local = fiedler_order(A, deg_local)
        t = best_sweep_cut(nodes_ref, order_local)

        left_local = set(order_local[:t].tolist())
        left = [nodes_ref[i] for i in left_local]
        right = [nodes_ref[i] for i in range(len(nodes_ref)) if i not in left_local]

        if len(left) < min_cluster_size or len(right) < min_cluster_size:
            out.append(nodes)
            continue

        clusters.append(left)
        clusters.append(right)

        if len(out) + len(clusters) >= max_clusters:
            break

    out.extend(clusters)

    # randomize cluster order slightly (helps tie-breaking stability)
    rng.shuffle(out)
    return out

def _allocate_budget_proportional(sizes: List[int], k: int) -> List[int]:
    total = sum(sizes)
    if total <= 0:
        return [0] * len(sizes)

    alloc = [max(1, int(round(k * (s / total)))) for s in sizes] if sizes else []
    
    # fix to exactly k
    total_alloc = sum(alloc)
    if total_alloc > k:
        excess = total_alloc - k

        # sort indices by alloc descending
        idxs = sorted(range(len(alloc)), key=lambda i: alloc[i], reverse=True)

        for i in idxs:
            if excess == 0:
                break
            if alloc[i] > 0:
                alloc[i] -= 1
                excess -= 1

    while sum(alloc) < k:
        i = max(range(len(alloc)), key=lambda i: sizes[i] - alloc[i])
        alloc[i] += 1
    return alloc


# Method 1: boundary takeover

class ClusterBoundaryTakeoverSpectral(Strategy):
    """
    Method 1:
      - Find clusters via spectral bisection (sorted Fiedler)
      - For each cluster, score nodes by #edges leaving the cluster
      - Allocate seeds proportional to cluster size
      - Pick top outgoing/boundary nodes (random tie-break)
    """
    name = "cluster_boundary_takeover_spectral"

    def __init__(
        self,
        min_cluster_size: int = 20,
        max_clusters: int = 10,
        normalized_laplacian: bool = True,
        per_cluster_tie_shuffle: bool = True,
    ):
        self.min_cluster_size = min_cluster_size
        self.max_clusters = max_clusters
        self.normalized_laplacian = normalized_laplacian
        self.per_cluster_tie_shuffle = per_cluster_tie_shuffle

    def select_seeds_50(
        self, G: Graph, k: int, rng: random.Random, ctx: StrategyContext, rounds: int = 50
    ) -> List[List[int]]:
        return _select_seeds_50_unique(self, G, k, rng, ctx, rounds=rounds, max_attempts=10)

    def select_seeds(self, G: Graph, k: int, rng: random.Random, ctx: StrategyContext) -> List[int]:
        if k <= 0:
            return []
        if k > G.n:
            raise ValueError(f"k={k} > n={G.n}")

        clusters = _spectral_clusters_sorted_fiedler(
            G,
            rng=rng,
            min_cluster_size=self.min_cluster_size,
            max_clusters=k, # unsure about this number
            normalized=self.normalized_laplacian,
        )
        sizes = [len(c) for c in clusters]
        # alloc[i] tells you how many seeds to pick from clusters[i].
        alloc = _allocate_budget_proportional(sizes, k) 

        used: Set[int] = set()
        seeds: List[int] = []

        for cluster, a in sorted(zip(clusters, alloc), key=lambda x: len(x[0]), reverse=True):
            if a <= 0:
                continue
            cset = set(cluster) # for fast access

            # [(u, out_deg), ...]
            scored: List[Tuple[int, int]] = []
            for u in cluster:
                out_deg = 0
                for v in G.neighbors[u]:
                    if v not in cset:
                        out_deg += 1
                scored.append((u, out_deg))

            scored.sort(key=lambda x: (x[1], G.degrees[x[0]]), reverse=True)

            i = 0
            picked = 0
            while picked < a and i < len(scored):
                j = i
                while j < len(scored) and scored[j][1] == scored[i][1]:
                    j += 1
                block = [u for (u, _) in scored[i:j] if u not in used]
                if self.per_cluster_tie_shuffle:
                    rng.shuffle(block)
                for u in block:
                    if picked >= a:
                        break
                    seeds.append(u)
                    used.add(u)
                    picked += 1
                i = j

        # fallback fill by degree if needed (select nodes with highest degree)
        if len(seeds) < k:
            remaining = [u for u in range(G.n) if u not in used]
            remaining.sort(key=lambda u: G.degrees[u], reverse=True)
            seeds.extend(remaining[: (k - len(seeds))])

        return seeds[:k]


# Method 2: degree proportional

class ClusterTopDegreeProportionalSpectral(Strategy):
    """
    Method 2:
      - Find clusters via spectral bisection (sorted Fiedler)
      - Allocate seeds proportional to cluster size
      - In each cluster, choose highest-degree nodes (random tie-break)
    """
    name = "cluster_top_degree_proportional_spectral"

    def __init__(
        self,
        min_cluster_size: int = 20,
        max_clusters: int = 50,
        normalized_laplacian: bool = True,
        tie_shuffle: bool = True,
    ):
        self.min_cluster_size = min_cluster_size
        self.max_clusters = max_clusters
        self.normalized_laplacian = normalized_laplacian
        self.tie_shuffle = tie_shuffle

    def select_seeds_50(
        self, G: Graph, k: int, rng: random.Random, ctx: StrategyContext, rounds: int = 50
    ) -> List[List[int]]:
        return _select_seeds_50_unique(self, G, k, rng, ctx, rounds=rounds, max_attempts=10)

    def select_seeds(self, G: Graph, k: int, rng: random.Random, ctx: StrategyContext) -> List[int]:
        if k <= 0:
            return []
        if k > G.n:
            raise ValueError(f"k={k} > n={G.n}")

        clusters = _spectral_clusters_sorted_fiedler(
            G,
            rng=rng,
            min_cluster_size=self.min_cluster_size,
            max_clusters=k,
            normalized=self.normalized_laplacian,
        )
        sizes = [len(c) for c in clusters]
        alloc = _allocate_budget_proportional(sizes, k)

        used: Set[int] = set()
        seeds: List[int] = []

        for cluster, a in sorted(zip(clusters, alloc), key=lambda x: len(x[0]), reverse=True):
            if a <= 0:
                continue

            # sort by degree desc
            nodes_sorted = sorted(cluster, key=lambda u: G.degrees[u], reverse=True)

            i = 0
            while a > 0 and i < len(nodes_sorted) and len(seeds) < k:
                deg_i = G.degrees[nodes_sorted[i]]
                j = i
                while j < len(nodes_sorted) and G.degrees[nodes_sorted[j]] == deg_i:
                    j += 1
                block = [u for u in nodes_sorted[i:j] if u not in used]
                if self.tie_shuffle:
                    rng.shuffle(block)
                for u in block:
                    if a <= 0 or len(seeds) >= k:
                        break
                    seeds.append(u)
                    used.add(u)
                    a -= 1
                i = j

        # fallback fill if needed
        if len(seeds) < k:
            remaining = [u for u in range(G.n) if u not in used]
            remaining.sort(key=lambda u: G.degrees[u], reverse=True)
            seeds.extend(remaining[: (k - len(seeds))])

        return seeds[:k]
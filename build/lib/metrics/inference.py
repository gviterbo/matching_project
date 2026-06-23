from collections import defaultdict
import numpy as np
from scipy.optimize import brentq
from core import Instance
from top_k_mallows import mallows_kendall as mk


def compute_borda_consensus(instance: Instance) -> list[int]:
    """Compute full project-ID consensus with Borda aggregation."""
    m = len(instance.projects)
    borda_scores = defaultdict(float)
    
    for student in instance.students:
        for rank, proj_id in enumerate(instance.preferences.get(student.id, [])):
            borda_scores[proj_id] += (m - rank)

    computed_consensus = sorted(borda_scores.keys(), key=lambda x: (-borda_scores[x], x))
    all_project_ids = {p.id for p in instance.projects}
    return computed_consensus + sorted(all_project_ids - set(computed_consensus))


def estimate_kendall_mallows_phi(instance: Instance, consensus_ranking: list[int]) -> float:
    """Estimate Mallows phi for Kendall distance from partial rankings."""
    m = len(instance.projects)
    if not instance.students or m <= 1:
        return 1.0

    p_to_idx = {project.id: idx for idx, project in enumerate(instance.projects)}

    def _to_beta(ranking: list[int], p_to_idx: dict[int, int]) -> np.ndarray:
        """Convert ranking (project IDs) to beta vector using global project-to-index mapping."""
        beta = np.full(len(p_to_idx), np.nan)
        for pos, pid in enumerate(ranking):
            beta[p_to_idx[pid]] = pos
        return beta

    distances_and_lengths = [
        (mk.p_distance(_to_beta(pref, p_to_idx), _to_beta(consensus_ranking, p_to_idx), k=len(pref), p=0), len(pref))
        for student in instance.students
        if (pref := instance.preferences.get(student.id, []))
    ]

    if not distances_and_lengths:
        return 1.0

    observed_total = sum(d for d, _ in distances_and_lengths)

    def objective_function(phi_val: float) -> float:
        expected_total = sum(mk.expected_dist_top_k(m, min(k, m), phi=phi_val) for _, k in distances_and_lengths)
        return (expected_total - observed_total) / len(distances_and_lengths)

    eps = 1e-6
    lower, upper = eps, 1.0 - eps

    if (f_lower := objective_function(lower)) >= 0:
        return f_lower
    
    if (f_upper := objective_function(upper)) <= 0:
        return f_upper

    return max(0.001, min(0.999, brentq(objective_function, lower, upper)))


def infer_kendall_mallows_parameters(instance: Instance, consensus_ranking: list[int] | None = None) -> tuple[list[int], float]:
    """Infer Kendall-Mallows parameters for kendall distance (consensus ranking, phi)."""
    if consensus_ranking is None:
        consensus_ranking = compute_borda_consensus(instance)
    else:
        missing = set(p.id for p in instance.projects) - set(consensus_ranking)
        consensus_ranking = consensus_ranking + sorted(missing)
    
    return consensus_ranking, estimate_kendall_mallows_phi(instance, consensus_ranking)

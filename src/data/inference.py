from collections import defaultdict
import numpy as np
from scipy.optimize import brentq
from core import Instance
from top_k_mallows import mallows_kendall as mk

# =====================================================================
# I. KENDALL HELPERS
# =====================================================================

def compute_partial_kendall_distance(ranking_a: list[int], ranking_b: list[int]) -> int:
    """
    Compute Kendall distance between two (possibly partial) index rankings.

    Args:
        ranking_a: Ordered list of project indices.
        ranking_b: Ordered list of project indices.

    Returns:
        Kendall distance.
    """
    if not ranking_a:
        return 0

    n = max(len(ranking_a), len(ranking_b))
    beta_a = np.full(n, np.nan)
    beta_b = np.full(n, np.nan)

    for pos, item in enumerate(ranking_a):
        if 0 <= item < n:
            beta_a[item] = pos
    for pos, item in enumerate(ranking_b):
        if 0 <= item < n:
            beta_b[item] = pos

    return int(mk.p_distance(beta_a, beta_b, k=len(ranking_a), p=0))


def compute_expected_kendall_partial(phi_val: float, m: int, k: int) -> float:
    """
    Compute expected Kendall distance under Mallows for a top-k list.

    Args:
        phi_val: Mallows dispersion parameter.
        m: Number of projects.
        k: Observed ranking length.

    Returns:
        Expected distance.
    """
    if m <= 0 or k <= 0:
        return 0.0
    k = min(k, m)
    return float(mk.expected_dist_top_k(m, k, phi=phi_val))


def _deduplicate_preserve_order(values: list[int]) -> list[int]:
    """Remove duplicates while preserving order."""
    seen = set()
    deduped: list[int] = []
    for value in values:
        if value in seen:
            continue
        deduped.append(value)
        seen.add(value)
    return deduped


def _build_project_id_to_index_map(instance: Instance) -> dict[int, int]:
    """Map project IDs to contiguous indices."""
    ordered_project_ids = [project.id for project in instance.projects]
    return {project_id: idx for idx, project_id in enumerate(ordered_project_ids)}


def _encode_ranking_with_index_map(ranking: list[int], project_id_to_idx: dict[int, int]) -> list[int]:
    """Convert project-ID ranking to index ranking and deduplicate."""
    cleaned = [project_id_to_idx[project_id] for project_id in ranking if project_id in project_id_to_idx]
    return _deduplicate_preserve_order(cleaned)


def _complete_indexed_consensus(consensus_idx: list[int], m: int) -> list[int]:
    """Complete a consensus to cover all indices exactly once."""
    deduped_consensus = _deduplicate_preserve_order(consensus_idx)
    consensus_set = set(deduped_consensus)
    missing = [idx for idx in range(m) if idx not in consensus_set]
    return deduped_consensus + missing


# =====================================================================
# II. CONSENSUS AND PHI INFERENCE
# =====================================================================

def compute_borda_consensus(instance: Instance) -> list[int]:
    """
    Compute full project-ID consensus with Borda aggregation.

    Args:
        instance: Input instance.

    Returns:
        Consensus ranking over project IDs.
    """
    m = len(instance.projects)
    borda_scores = defaultdict(float)
    valid_project_ids = {project.id for project in instance.projects}
    
    for student in instance.students:
        student_pref = [proj_id for proj_id in instance.preferences.get(student.id, []) if proj_id in valid_project_ids]
        student_pref = _deduplicate_preserve_order(student_pref)
        for rank, proj_id in enumerate(student_pref):
            borda_scores[proj_id] += (m - rank)

    computed_consensus = sorted(borda_scores.keys(), key=lambda x: (-borda_scores[x], x))

    all_project_ids = {p.id for p in instance.projects}
    missing_projects = sorted(all_project_ids - set(computed_consensus))

    return computed_consensus + missing_projects


def estimate_kendall_mallows_phi(instance: Instance, consensus_ranking: list[int]) -> float:
    """
    Estimate Mallows phi for Kendall distance from partial rankings.

    Args:
        instance: Input instance.
        consensus_ranking: Consensus project-ID ranking.

    Returns:
        Estimated phi clipped to [0.001, 0.999].
    """
    m = len(instance.projects)

    if not instance.students or m <= 1:
        return 1.0

    project_id_to_idx = _build_project_id_to_index_map(instance)
    consensus_idx = _encode_ranking_with_index_map(consensus_ranking, project_id_to_idx)
    consensus_idx = _complete_indexed_consensus(consensus_idx, m)

    distances_and_lengths: list[tuple[float, int]] = []
    for student in instance.students:
        student_pref_ids = instance.preferences.get(student.id, [])
        student_pref_idx = _encode_ranking_with_index_map(student_pref_ids, project_id_to_idx)
        if not student_pref_idx:
            continue
        observed_k = len(student_pref_idx)
        observed_distance = float(compute_partial_kendall_distance(student_pref_idx, consensus_idx))
        distances_and_lengths.append((observed_distance, observed_k))

    if not distances_and_lengths:
        return 1.0

    observed_total = sum(observed_distance for observed_distance, _ in distances_and_lengths)

    def objective_function(phi_val: float) -> float:
        expected_total = 0.0
        for _, observed_k in distances_and_lengths:
            expected_total += compute_expected_kendall_partial(phi_val, m, observed_k)
        return (expected_total - observed_total) / len(distances_and_lengths)

    eps = 1e-6
    lower, upper = eps, 1.0 - eps
    f_lower = objective_function(lower)
    f_upper = objective_function(upper)

    if f_lower >= 0:
        phi_estimated = lower
    elif f_upper <= 0:
        phi_estimated = upper
    else:
        phi_estimated = brentq(objective_function, lower, upper)

    return max(0.001, min(0.999, float(phi_estimated)))


def infer_kendall_mallows_parameters(instance: Instance, consensus_ranking: list[int] | None = None) -> tuple[list[int], float]:
    """
    Infer Kendall-Mallows parameters (consensus ranking, phi).

    Args:
        instance: Input instance.
        consensus_ranking: Optional project-ID consensus ranking.

    Returns:
        Tuple (consensus_ranking, phi_estimated).
    """
    if consensus_ranking is None:
        consensus_ranking = compute_borda_consensus(instance)
    else:
        project_ids = [project.id for project in instance.projects]
        valid_project_ids = set(project_ids)
        provided = _deduplicate_preserve_order([proj_id for proj_id in consensus_ranking if proj_id in valid_project_ids])
        missing = [proj_id for proj_id in project_ids if proj_id not in set(provided)]
        consensus_ranking = provided + missing
        
    phi_estimated = estimate_kendall_mallows_phi(instance, consensus_ranking)
    
    return consensus_ranking, phi_estimated

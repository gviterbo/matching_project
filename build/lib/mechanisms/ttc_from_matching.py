from core.instance import Instance
from core.matching import Matching
import functools

from metrics.cost import (
    rank_sum_cost,
    borda_welfare_cost,
    top_n_assigned_cost,
    square_rank_sum_cost,
    nash_welfare_cost,
    max_rank_cost,
    unassigned_students_cost,
)

"""
   WARNING : ttc_from_matching needs an objective function
"""

def _strict_rank(instance: Instance, student_id: int, project_id: int) -> int:
    """Rank of project_id in student_preference_list ; +inf if not listed."""
    prefs = instance.preferences[student_id]
    try:
        return prefs.index(project_id)
    except ValueError:
        return float("inf")


def _best_cycle(instance, current, work, objective, max_cycle_length, max_cycles_scanned):
    """Return the best cycle according to the objective function, or None if there aren't"""
    assigned = [student for student in current.keys()]                  # students with a project
    pos = {student: idx for idx, student in enumerate(assigned)}                        # canonical order for thee students

    # adjacency: s -> list of students whose project s would strictly prefer
    adj = {s: [] for s in assigned}
    for s in assigned:
        rank_now = _strict_rank(instance, s, current[s])
        if rank_now == 0:
            continue                                # already has its first choice
        for t in assigned:
            if t is s or current[t] == current[s]:
                continue
            if _strict_rank(instance, s, current[t]) < rank_now:
                adj[s].append(t)

    best = None
    best_key = None
    scanned = 0

    # Depth First Search enumeration of simple cycles ()
    def dfs(start, node, path, in_path):
        nonlocal scanned, best, best_key
        if scanned >= max_cycles_scanned:
            return
        for nxt in adj[node]:
            if nxt is start and len(path) >= 2:
                scanned += 1
                _consider(path)
                if scanned >= max_cycles_scanned:
                    return
            elif nxt not in in_path and pos[nxt] > pos[start]:
                if max_cycle_length is not None and len(path) >= max_cycle_length:
                    continue
                in_path.add(nxt)
                path.append(nxt)
                dfs(start, nxt, path, in_path)
                path.pop()
                in_path.discard(nxt)

    def _consider(path):
        nonlocal best, best_key
        cycle = list(path)
        k = len(cycle)
        target = {cycle[i]: current[cycle[(i + 1) % k]] for i in range(k)}

        # total strict rank improvement of the participants (>0 by construction)
        rank_gain = 0
        for s in cycle:
            rank_gain += _strict_rank(instance, s, current[s]) - _strict_rank(instance, s, target[s])

        # score the resulting matching with the objective, then revert
        saved = {s: current[s] for s in cycle}
        for s in cycle:
            work.assign(s, target[s])
        score = objective(work)
        for s in cycle:
            work.assign(s, saved[s])

        # selection key: best objective first, then biggest student improvement,
        # then shorter cycle (cheaper / more local exchange).
        key = (score, -rank_gain, k)
        if best_key is None or key < best_key:
            best_key = key
            best = (cycle, target)

    for start in assigned:
        dfs(start, start, [start], {start})
        if scanned >= max_cycles_scanned:
            break

    return best

def ttc_from_matching(matching: Matching, objective=None, max_cycle_length=None, max_cycles_scanned=20000, max_iterations=10000) -> Matching:
    assert objective != None, "WARNING : ttc_from_matching needs an objective function to know what to improve, see /src/metrics/cost.py to choose a metric"
    
    instance = matching.instance
    current = dict(matching.assignments)            # student.id -> project.id (copy of matching.assignments)

    result = Matching(instance)                        # scored matching, kept in sync with `current`
    for s_id, p_id in current.items():
        result.assign(s_id, p_id)

    for _ in range(max_iterations):
        best = _best_cycle(instance, current, result, objective,
                           max_cycle_length, max_cycles_scanned)
        if best is None:
            break
        cycle, target = best          # target[s] = project s will take
        for s_id in cycle:
            result.assign(s_id, target[s_id])
            current[s_id] = target[s_id]

    return result



# maximise overall student satisfaction  ==  minimise the Borda gap
def ttc_maximize_student_satisfaction(matching, **kw):
    return ttc_from_matching(matching, objective=borda_welfare_cost, **kw)

# minimise overall student non-satisfaction  ==  minimise the rank sum of the project (the lower the more preferred)
def ttc_minimize_student_insatisfaction(matching, **kw):
    return ttc_from_matching(matching, objective=rank_sum_cost, **kw)

# one variant per function of cost.py - the cost functions are used as-is
def ttc_min_rank_sum(matching, **kw):
    return ttc_from_matching(matching, objective=rank_sum_cost, **kw)

def ttc_min_borda_welfare(matching, **kw):
    return ttc_from_matching(matching, objective=borda_welfare_cost, **kw)

def ttc_min_top_n(matching, n, **kw):
    return ttc_from_matching(matching, objective=functools.partial(top_n_assigned_cost, n=n), **kw)

def ttc_min_square_rank_sum(matching, **kw):
    return ttc_from_matching(matching, objective=square_rank_sum_cost, **kw)

def ttc_min_nash_welfare(matching, **kw):
    return ttc_from_matching(matching, objective=nash_welfare_cost, **kw)

def ttc_min_max_rank(matching, **kw):
    return ttc_from_matching(matching, objective=max_rank_cost, **kw)

def ttc_min_unassigned(matching, **kw):
    # constant under exchange cycles ; provided for API uniformity
    return ttc_from_matching(matching, objective=unassigned_students_cost, **kw)
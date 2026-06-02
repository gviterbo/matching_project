import math
from core.matching import Matching


##################### Global efficiency #####################
# Measures overall student satisfaction by aggregating individual preference ranks.


def rank_sum_cost(matching: Matching) -> float:
    """
    Computes the normalized average rank cost.\n
    0 = Every student gets their first choice.\n
    1 = Every student gets their least preferred choice or remains unassigned.\n
    """
    total_cost = 0
    worst_instance_rank = len(matching.instance.projects) - 1
    max_theoretical_cost = len(matching.instance.students) * worst_instance_rank

    if max_theoretical_cost == 0:
        return 0.0

    for student in matching.instance.students:
        assigned_proj_rank = matching.project_rank_of(student.id)
        total_cost += assigned_proj_rank if assigned_proj_rank is not None else worst_instance_rank
            
    return total_cost / max_theoretical_cost

def borda_welfare_cost(matching: Matching) -> float:
    """
    Computes the normalized Borda opportunity cost.\n
    0 = Every student gets their first choice.\n
    1 = Every student gets their least preferred choice or remains unassigned.\n
    """
    total_borda_satisfaction = 0
    max_borda_possible = 0

    if max_borda_possible == 0:
        return 0.0
    
    for student in matching.instance.students:
        assigned_proj_rank = matching.project_rank_of(student.id)
        len_pref_list = len(matching.instance.preferences[student.id])

        total_borda_satisfaction += len_pref_list - assigned_proj_rank - 1 if assigned_proj_rank is not None else 0
        max_borda_possible += len_pref_list - 1
        
    return (max_borda_possible - total_borda_satisfaction) / max_borda_possible

def top_n_assigned_cost(matching: Matching, n: int):
    """
    Computes the miss rate outside the top N choices.\n
    0 = Every student gets one of their top N choices.\n
    1 = No student gets one of their top N choices.\n
    """
    count = 0
    max_theoretical_count = len(matching.instance.students)

    if max_theoretical_count == 0:
        return 0.0
    
    for student in matching.instance.students:
        assigned_proj_rank = matching.project_rank_of(student.id)
        count += 0 if 0 <= assigned_proj_rank < n else 1
    
    return count / max_theoretical_count



##################### Fairness #####################
# Evaluates rank distribution equity to ensure no student is disproportionately penalized.

def square_rank_sum_cost(matching: Matching):
    """
    Computes the normalized squared rank sum cost.\n
    0 = Every student gets their first choice.\n
    1 = Every student gets their least preferred choice or remains unassigned.\n
    """
    total_cost = 0
    worst_instance_rank = len(matching.instance.projects) - 1
    max_theoretical_cost = len(matching.instance.students) * (worst_instance_rank ** 2)

    if max_theoretical_cost == 0:
        return 0.0

    for student in matching.instance.students:
        assigned_proj_rank = matching.project_rank_of(student.id)
        total_cost += (assigned_proj_rank if assigned_proj_rank is not None else worst_instance_rank) ** 2
            
    return total_cost / max_theoretical_cost

def nash_welfare_cost(matching: Matching):
    """
    Computes the negative log-normalized Nash welfare product.\n
    0 = Every student gets their first choice.\n
    1 = Every student gets their least preferred choice or remains unassigned.\n
    """
    total_log_borda = 0.0
    max_log_possible = 0.0

    if max_log_possible == 0:
        return 0.0
    
    for student in matching.instance.students:
        assigned_proj_rank = matching.project_rank_of(student.id)
        len_pref_list = len(matching.instance.preferences[student.id])
                
        total_log_borda += math.log((len_pref_list - assigned_proj_rank + 1) if assigned_proj_rank is not None else 1)
        max_log_possible += math.log(len_pref_list + 1)
        
    return (max_log_possible - total_log_borda) / max_log_possible

def max_rank_cost(matching: Matching):
    """
    Computes the normalized maximum rank suffered by any student.\n
    0 = Every student gets their first choice.\n
    1 = At least one student gets the worst possible rank or remains unassigned.\n
    """
    max_rank_idx = 0
    worst_possible_idx = len(matching.instance.projects) - 1

    if worst_possible_idx == 0:
        return 0.0
    
    for student in matching.instance.students:
        assigned_proj_rank = matching.project_rank_of(student.id)

        current_idx = assigned_proj_rank if assigned_proj_rank is not None else worst_possible_idx
        max_rank_idx = max(max_rank_idx, current_idx)
        
    return max_rank_idx / worst_possible_idx



##################### Feasibility #####################
# Tracks the mechanism's operational capacity to assign every student to a project.

def unassigned_students_cost(matching: Matching) -> float:
    """
    Computes the ratio of unassigned students.\n
    0 = Every student is assigned.\n
    1 = No student is assigned.\n
    """
    total_students = len(matching.instance.students)

    if total_students == 0:
        return 0.0
    
    return len(matching.unmatched_students()) / total_students

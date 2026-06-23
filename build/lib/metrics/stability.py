from core.matching import Matching


##################### Stability #####################
# This section measures the respect of projects' priority criteria and the fairness 
# of the allocation regarding student merits (e.g., GPA).

def blocking_pairs_stability_score(matching: Matching) -> float:
    """
    Computes the ratio of unstable (student, project) blocking pairs.\n
    0 = No blocking pairs.\n
    1 = Every pair is a blocking pair.\n
    """
    blocking_pairs_count = 0
    students = matching.instance.students
    projects = matching.instance.projects
    total_possible_pairs = len(students) * len(projects)

    if total_possible_pairs == 0:
        return 0.0

    for project in projects:
        assigned_students = matching.students_in(project.id)
        empty_slots = project.capacity - len(assigned_students)
        
        for student in students:
            pref_list = matching.instance.preferences[student.id]
            
            # A student cannot form a blocking pair with a project they did not rank
            if project.id not in pref_list:
                continue
                
            assigned_proj_rank = matching.project_rank_of(student.id)
            
            # Condition 1: The student prefers this project to their current assignment
            if assigned_proj_rank is None or pref_list.index(project.id) < assigned_proj_rank:
                
                # Condition 2a : The project has empty slots (waste)
                if empty_slots > 0:
                    blocking_pairs_count += 1
                
                # Condition 2b : The project is full but prefers this student over at least one assigned student (envy)
                elif any(matching.instance.is_prefered(project.id, student.id, other_id) for other_id in assigned_students):
                    blocking_pairs_count += 1

    return blocking_pairs_count / total_possible_pairs

def justified_envy_stability_score(matching: Matching) -> float:
    """
    Computes the ratio of students experiencing justified envy.
    0 = No student experiences justified envy.
    1 = Every student experiences justified envy.
    """
    envying_students_count = 0
    total_students = len(matching.instance.students)

    if total_students == 0:
        return 0.0

    for student in matching.instance.students:
        pref_list = matching.instance.preferences[student.id]
        assigned_proj_rank = matching.project_rank_of(student.id)

        # Slice preferences to evaluate only projects ranked strictly higher than the current assignment
        target_projects = pref_list if assigned_proj_rank is None else pref_list[:assigned_proj_rank]
        
        has_envy = False
        for project_id in target_projects:
            assigned_students = matching.students_in(project_id)
            
            # Check if the project ranks the current student higher than any of its assigned students
            if any(matching.instance.is_prefered(project_id, student.id, other_id) for other_id in assigned_students):
                has_envy = True
                break
                    
        if has_envy:
            envying_students_count += 1

    return envying_students_count / total_students

def wasteful_capacity_stability_score(matching: Matching) -> float:
    """
    Computes the ratio of wasted project slots.\n
    0 = No waste (no empty slot is desired by an unassigned or poorly assigned student).\n
    1 = Every available slot in the instance is wasted.\n
    """
    wasted_slots_count = 0
    total_capacity = sum(project.capacity for project in matching.instance.projects)

    if total_capacity == 0:
        return 0.0

    for project in matching.instance.projects:
        empty_slots = project.capacity - len(matching.students_in(project.id))
        
        if empty_slots == 0: continue

        is_wasted = False
        for student in matching.instance.students:
            pref_list = matching.instance.preferences[student.id]

            if project.id not in pref_list: continue

            assigned_proj_rank = matching.project_rank_of(student.id)
            
            # A slot is wasted if an unassigned student or a student who ranks this project higher desires it
            if assigned_proj_rank is None or pref_list.index(project.id) < assigned_proj_rank:
                is_wasted = True
                break
        
        if is_wasted:
            wasted_slots_count += empty_slots

    return wasted_slots_count / total_capacity

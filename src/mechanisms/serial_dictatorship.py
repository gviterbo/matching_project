from core import Instance, Matching


def complete_preferences(instance: Instance) -> Instance:
    """
    Returns a new Instance where each student's preference list is extended
    with any unranked projects appended in arbitrary order at the end.
    """
    all_project_ids = {project.id for project in instance.projects}
    
    completed = {
        student_id: prefs + [p for p in all_project_ids if p not in prefs]
        for student_id, prefs in instance.preferences.items()
    }
    
    return Instance(
        students=instance.students,
        projects=instance.projects,
        preferences=completed,
        school_priorities=instance.school_priorities,
    )

def serial_dictatorship(instance: Instance, order: list[int] = None) -> Matching:
    instance = complete_preferences(instance)
    matching = Matching(instance)
    capacities = {project.id: project.capacity for project in instance.projects}

    if order == None : 
        order = [student.id for student in instance.students]

    for student_id in order:
        for project_id in instance.preferences[student_id]:
            if capacities[project_id] > 0:
                matching.assign(student_id, project_id)
                capacities[project_id] -= 1
                break
    return matching

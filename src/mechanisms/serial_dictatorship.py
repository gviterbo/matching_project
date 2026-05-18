from core.instance import Instance
from core.matching import Matching

def serial_dictatorship(instance: Instance, order: list[int]) -> Matching:
    matching = Matching(instance)
    capacities = {project.id: project.capacity for project in instance.projects}
    for student_id in order:
        for project_id in instance.preferences[student_id]:
            if capacities[project_id] > 0:
                matching.assign(student_id, project_id)
                capacities[project_id] -= 1
                break
    return matching
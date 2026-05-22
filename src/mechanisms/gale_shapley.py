from core.instance import Instance
from core.matching import Matching
from collections import deque

def gale_shapley(instance: Instance) -> Matching:
    matching = Matching(instance)
    capacities = {project.id: project.capacity for project in instance.projects}
    free = deque(instance.students)
    next_proposal = {student.id: 0 for student in instance.students}
    
    while not len(free) == 0:
        student = free[0]

        if next_proposal[student.id] >= len(instance.preferences[student.id]):
            free.popleft()
            continue

        project_id = instance.preferences[student.id][next_proposal[student.id]]
        project = instance._project_by_id[project_id]

        next_proposal[student.id] += 1

        if capacities[project.id] > 0:
            matching.assign(student.id, project.id)
            capacities[project.id] -= 1
            free.popleft()

        else:
            assigned_students = matching.students_in(project.id)
            
            former_student_id = min(assigned_students, key=lambda s: instance.students[s].gpa)
            former_student = instance.students[former_student_id]

            if student.gpa > former_student.gpa:
                matching.unassign(former_student.id)
                matching.assign(student.id, project.id)
                free.popleft()
                free.append(former_student)
            
            else:
                continue
                
            
    return matching

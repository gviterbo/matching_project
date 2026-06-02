from core.instance import Instance
from core.matching import Matching
from collections import deque

def gale_shapley(instance: Instance, useGPA = False) -> Matching:
    matching = Matching(instance)
    capacities = {project.id: project.capacity for project in instance.projects}
    free = deque(instance.students)
    next_proposal = {student.id: 0 for student in instance.students}
    INF = float("inf")
    if instance.school_priorities : 
        rank = {project_id : {student_id : i for i, student_id in enumerate(order)} for project_id, order in instance.school_priorities.items()}
    
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
            if instance.school_priorities : 
                worst_assigned_student = max(assigned_students, key=lambda x : rank[project_id].get(x, INF))
                # if the current student is better than the worse assigned student 
                if rank[project_id].get(student, INF) < rank[project_id][worst_assigned_student] : 
                    matching.unassign(worst_assigned_student)
                    matching.assign(student, project_id)
                    free.popleft() # pop student, the head of the queue (because free is a double headed queue "deque")
                    free.append(worst_assigned_student)
            elif useGPA : 
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

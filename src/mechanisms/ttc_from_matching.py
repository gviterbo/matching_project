from core.instance import Instance
from core.matching import Matching 
import random

"""
We choose to implement the ttc that improves a stable solution
because the more important is that everyone gets a project 
and the ttc algorithm garantees a pareto-optimal solution but not
a stable one.
"""

# Implementation of the "Top Trading Cycle" Algorithm
def ttc_from_matching(matching : Matching, useGPA = False) -> Matching : 
    instance = matching.instance
    current_matching = dict(matching.assignments)                                        # student.id -> project.id
    current_project_to_student = {project.id : [] for project in instance.projects}      # project.id -> [student.id]
    for student_id, project_id in current_matching.items() : 
        current_project_to_student[project_id].append(student_id)


    # Using list of priorities for the schools
    all_student_ids = [student.id for student in instance.students] 
    if instance.school_priorities : 
        project_preferences = {}
        for project in instance.projects : 
            if project.id in instance.school_priorities : 
                project_preferences[project.id] = list(instance.school_priorities[project.id])
            # If no priorities, we shuffle all the student_ids to create the priority list
            else : 
                project_preferences[project.id] = random.sample(all_student_ids, len(all_student_ids))
    # Using GPA if no list of priorities : /!\ no difference between the projects preferences
    elif useGPA: 
        sorted_by_gpa = sorted(instance.students, key=lambda s: s.gpa or 0, reverse=True)
        project_preferences = {project.id : [student.id for student in sorted_by_gpa] for project in instance.projects}
    else :
        project_preferences = {project.id : random.sample(all_student_ids, len(all_student_ids)) for project in instance.projects}


    # each students only keeps the projects that are strictly better than the one they currently have
    student_preferences = {}
    for student_id, project_id in current_matching.items():
        preferences = instance.preferences[student_id]
        if project_id in preferences : 
            current_assign_rank = preferences.index(project_id)
        else : 
            current_assign_rank = len(preferences)
        student_preferences[student_id] = list(preferences[:current_assign_rank])

    # The student points on its favourite project if he still has favourite projects
    student_points_projects = {student_id : student_preferences[student_id][0] for student_id in current_matching if student_preferences.get(student_id)}
    students_to_improve = set(student_points_projects)

    # Looking for upgrading cycles
    while students_to_improve : 
        project_points_student = {}
        for project in instance.projects : 
            for student_id in project_preferences[project.id] :
                 # If the student wants to be improved (wants to leave its current project) and is assigned to the selected project :
                 if student_id in current_project_to_student[project.id] and student_id in students_to_improve :
                    project_points_student[project.id] = student_id
                    break 
        
        cycles = _find_all_cycles(students_to_improve, student_points_projects, project_points_student)

        if not cycles : 
            # If we can't improve the matching
            students_blocked = {student_id for student_id in students_to_improve if student_points_projects[student_id] not in project_points_student}
            if students_blocked :
                for student_id in students_blocked :
                    student_preferences[student_id].pop(0)
                    if student_preferences[student_id]:
                        student_points_projects[student_id] = student_preferences[student_id][0]
                    else:
                        student_points_projects.pop(student_id, None)
                        students_to_improve.discard(student_id)
            else :
                break
        
        for cycle in cycles :
            new_matching = {student_id : student_points_projects[student_id] for student_id in cycle}
            for student_id in cycle :
                old_project, new_project = current_matching[student_id], new_matching[student_id]
                current_project_to_student[old_project].remove(student_id)
                current_project_to_student[new_project].append(student_id)
                current_matching[student_id] = new_project
                student_id_preferences = instance.preferences[student_id]
                if new_project in student_id_preferences :
                    new_assign_rank = student_id_preferences.index(new_project)
                else :
                    new_assign_rank = len(student_id_preferences)
                student_preferences[student_id] = list(student_id_preferences[:new_assign_rank])
                if student_preferences[student_id] :
                    student_points_projects[student_id] = student_preferences[student_id][0]
                else :
                    student_points_projects.pop(student_id, None)
                    students_to_improve.discard(student_id)

    result_matching = Matching(instance)
    for student_id, project_id in current_matching.items():
        result_matching.assign(student_id, project_id)
    return result_matching


def _find_all_cycles(students_to_improve, student_points_projects, project_point_student):
    """
    TODO : add the notion of capacity when we search the cycles
    """
    cycles = []
    visited = set()
    for start in students_to_improve : 
        if start not in visited : 
            path, path_index, current_student = [], {}, start 
            while current_student not in visited : 
                if current_student in path_index : 
                    cycles.append(path[path_index[current_student]:])
                    break 
                if current_student not in student_points_projects : 
                    break 
                path_index[current_student] = len(path)
                path.append(current_student)
                project = student_points_projects[current_student]
                if project in project_point_student :
                    current_student = project_point_student[project]
                else :
                    break
            for student in path : 
                visited.add(student)
    return cycles
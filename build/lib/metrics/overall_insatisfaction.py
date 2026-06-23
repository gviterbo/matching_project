from core.matching import Matching
from core.instance import Instance

def overall_insatisfaction(matching : Matching, school_priorities = False) : 
    instance = matching.instance
    nb_students = len(instance.students)
    nb_projects = len(instance.projects)
    students_insatisfaction = 0 

    for student_id, project_id in matching.assignments.items() : 
        student_preferences = instance.preferences[student_id]
        if project_id in student_preferences :
            students_insatisfaction += student_preferences.index(project_id)
        else : 
            students_insatisfaction += nb_projects
    
    if school_priorities : 
        projects_insatisfaction = 0
        for project_id, students_in_project in matching._students_in_project.items() : 
            project_priorities = instance.school_priorities[project_id]
            for student_id in students_in_project : 
                if student_id in project_priorities : 
                    projects_insatisfaction += project_priorities.index(student_id)
                else : 
                    projects_insatisfaction += nb_students
        return {"students" : students_insatisfaction/nb_projects, "projects" : projects_insatisfaction/nb_students}

                
    else : 
        return {"students" :students_insatisfaction/nb_projects}
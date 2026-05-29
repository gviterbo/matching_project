import numpy as np
import mallows_kendall as mk
from core.instance import Instance, Student, Project

def make_instance(n_students, n_projects, capacity=1, phi=0.5, seed=42):
    np.random.seed(seed)
    raw = mk.sample(m=n_students, n=n_projects, phi=phi)
    # raw[i][j] = rank of project j for student i -> argsort for ordered list
    preferences = {i: list(np.argsort(raw[i])) for i in range(n_students)}
    students = tuple(Student(id=i) for i in range(n_students))
    projects = tuple(Project(id=j, capacity=capacity) for j in range(n_projects))
    return Instance(students=students, projects=projects, preferences=preferences)


instance = make_instance(n_students=20, n_projects=8, capacity=3, phi=0.5)
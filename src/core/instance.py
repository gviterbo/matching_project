from dataclasses import dataclass, field
# Some comments will be removed later, dont worry about them
# Sorry for writting a novel here :(


@dataclass(frozen=True)
class Student: 
    id: int
    gpa: float | None = None


@dataclass(frozen=True)
class Project: 
    id: int
    capacity: int = 1


# later I will explain this on detail:
# Here, tuple was used instead of list for students and projects 
# because tuples are immutable in our dataclass.
# This immutability can help prevent accidental changes later on
# (And it also looks fancier than lists :P)
@dataclass(frozen=True)
class Instance:
    students: tuple[Student, ...]
    projects: tuple[Project, ...]
    preferences: dict[int, list[int]] # student id -> list of project ids
    school_priorities: dict[int, list[int]] | None = None # project id -> list of student ids
    _student_by_id: dict[int, Student] = field(default_factory=dict, repr=False, compare=False)
    _project_by_id: dict[int, Project] = field(default_factory=dict, repr=False, compare=False)
    
    # called immediately after the dataclass is initialized, 
    # and it is used to perform some checks and create some 
    # caches for faster lookup later on
    def __post_init__(self): 
        #creating a cache for students and projects by id for faster lookup
        temp_stu = {} 
        for student in self.students:
            temp_stu[student.id] = student
        object.__setattr__(self, "_student_by_id", temp_stu)
        temp_proj = {}
        for project in self.projects:
            temp_proj[project.id] = project
        object.__setattr__(self, "_project_by_id", temp_proj)

        # verification 1: check if there are no inexistent projects in the preferences
        for student_id, prefs in self.preferences.items():
            for project_id in prefs:
                if project_id not in self._project_by_id:
                    raise ValueError(f"Student {student_id} has a preference for an inexistent project {project_id}")
        
        # verification 2: check if there are no duplicate students
        if len(self._student_by_id) != len(self.students):
            raise ValueError("There are duplicate students in the instance")

        # verification 3: check if there are no duplicate projects
        if len(self._project_by_id) != len(self.projects):
            raise ValueError("There are duplicate projects in the instance")
        

    # here we have the "getter" methods for Students and Projects 
    def student(self, student_id: int) -> Student:
        return self._student_by_id[student_id]

    def project(self, project_id: int) -> Project:
        return self._project_by_id[project_id]

    # now, I thought for more than 30 minutes about what should we 
    # consider when a student forgets or simply doesn't have a preference for a project, 
    # and I decided that in this case, we will consider that the student id indifferent 
    # to the remaining projects, and we will simply add all the projects to the student's 
    # preference list behind the others. I think this is the most reasonable thing to do,
    # and it also makes the implementation of the algorithms a bit easier later on.
    # Also, everything will regarding this question eventually be implemented in the loaders.py
    def rank_of(self, student_id:int, project_id:int) -> int:
        return self.preferences[student_id].index(project_id)
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Student: 
    id: int
    gpa: float | None = None

    def __str__(self) -> str:
        return f"Student {self.id:4d} (gpa : {self.gpa or "-"})"


@dataclass(frozen=True)
class Project: 
    id: int
    capacity: int = 1


@dataclass(frozen=True)
class Instance:
    students: tuple[Student, ...]
    projects: tuple[Project, ...]
    preferences: dict[int, list[int]] # student id -> list of project ids
    school_priorities: dict[int, list[int]] | None = None # project id -> list of student ids
    _student_by_id: dict[int, Student] = field(default_factory=dict, repr=False, compare=False)
    _project_by_id: dict[int, Project] = field(default_factory=dict, repr=False, compare=False)
    
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
    
    def rank_of(self, student_id: int, project_id: int) -> int | None:
        pref_list = self.preferences[student_id]
        return pref_list.index(project_id) if project_id in pref_list else None
    
    def is_prefered(self, project_id: int, student_id: int, student_id_ref: int) -> bool:
        if self.school_priorities is None:
            return True
        if project_id not in self.school_priorities:
            return True
        priority_list = self.school_priorities[project_id]
        if student_id_ref not in priority_list:
            return True
        if student_id not in priority_list:
            return False
        return priority_list.index(student_id) < priority_list.index(student_id_ref)
    
    def __str__(self) -> str:
        lines = []
            
        lines.append("\n=== Preferences (Student ID -> Project IDs) ===")
        if self.preferences:
            for student_id, project_ids in self.preferences.items():
                lines.append(f"  {self.student(student_id)} : {project_ids}")
        else:
            lines.append("  None")
            
        lines.append("\n=== School Priorities (Project ID -> Student IDs) ===")
        if self.school_priorities is not None:
            if self.school_priorities:
                for project_id, student_ids in self.school_priorities.items():
                    lines.append(f"  Project {project_id:4d} : {student_ids}")
            else:
                lines.append("  None")
        else:
            lines.append("  None")
            
        return "\n".join(lines)

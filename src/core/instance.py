from dataclasses import dataclass, field

@dataclass(frozen=True)
class Student: 
    id: int
    gpa: float | None = None

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
    

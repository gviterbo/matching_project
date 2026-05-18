from dataclasses import dataclass, field
from core.instance import Instance

@dataclass
class Matching:
    instance: Instance
    assignments: dict[int, int] = field(default_factory=dict) # student id -> project id
    _students_in_project: dict[int, list[int]] = field(default_factory=dict, repr=False, compare=False) # project id -> list of student ids

    def __post_init__(self):
        reverse = {}
        for project in self.instance.projects:
            reverse[project.id] = []
        for student_id, project_id in self.assignments.items():
            reverse[project_id].append(student_id)
        self._students_in_project = reverse

    def unassign(self, student_id: int) -> None:
        proj = self.assignments.pop(student_id, None)
        if proj is not None:
            self._students_in_project[proj].remove(student_id)
    
    def assign(self, student_id: int, project_id: int) -> None:
        if student_id in self.assignments:
            self.unassign(student_id)
        self.assignments[student_id] = project_id
        self._students_in_project[project_id].append(student_id)

    def project_of(self, student_id: int) -> int | None:
        return self.assignments.get(student_id)
    
    def students_in(self, project_id: int) -> list[int]:
        return list(self._students_in_project[project_id])
    
    def unmatched_students(self) -> list[int]:
        ans = []
        for student in self.instance.students:
            if student.id not in self.assignments:
                ans.append(student.id)
        return ans

    def is_complete(self) -> bool:
        return len(self.assignments) == len(self.instance.students)
    
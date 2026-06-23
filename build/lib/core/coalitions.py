from dataclasses import dataclass
from core.instance import Instance


@dataclass(frozen=True)
class Coalition:
    members: tuple[int, ...]

    def __post_init__(self):
        if len(set(self.members)) != len(self.members):
            raise ValueError("A coalition cannot contain duplicated students")

    @property
    def size(self) -> int:
        return len(self.members)


class CoalitionInstance:
    def __init__(self, instance: Instance, coalitions: list[tuple[int, ...]]):
        self.instance = instance

        self.coalitions = [
            Coalition(tuple(sorted(group)))
            for group in coalitions
        ]

        students_in_coalitions = {
            student_id
            for coalition in self.coalitions
            for student_id in coalition.members
        }

        self.singles = [
            Coalition((student.id,))
            for student in instance.students
            if student.id not in students_in_coalitions
        ]

    @property
    def groups(self) -> list[Coalition]:
        return self.coalitions + self.singles

    def coalition_preferences(self, coalition: Coalition) -> list[int]:
        project_ids = [
            project.id
            for project in self.instance.projects
        ]

        scores = {}

        for project_id in project_ids:
            total_rank = 0

            for student_id in coalition.members:
                rank = self.instance.rank_of(student_id, project_id)
                total_rank += rank if rank is not None else len(project_ids)

            scores[project_id] = total_rank

        return sorted(project_ids, key=lambda project_id: (scores[project_id], project_id))

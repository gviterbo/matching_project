"""Loaders for matching instances from CSV files."""

import csv
from collections import defaultdict
from dataclasses import replace

from core.instance import Instance, Student, Project


def parse_id(raw_id: str) -> int:
    return int(raw_id.split("_")[1])


def _read_preferences_csv(path: str) -> dict[int, list[tuple[int, int]]]:
    grouped: dict[int, list[tuple[int, int]]] = defaultdict(list)

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            student_id = parse_id(row["stu_id"])
            project_id = parse_id(row["proj_id"])
            points = int(row["points"])
            grouped[student_id].append((project_id, points))

    return dict(grouped)


def load_instance_from_csv(path: str, capacity: int = 5) -> Instance:
    grouped = _read_preferences_csv(path)

    project_ids: set[int] = set()
    for entries in grouped.values():
        for project_id, _ in entries:
            project_ids.add(project_id)

    students = tuple(Student(id=stu_id) for stu_id in sorted(grouped.keys()))
    projects = tuple(
        Project(id=proj_id, capacity=capacity) for proj_id in sorted(project_ids)
    )

    preferences: dict[int, list[int]] = {}
    for student_id, entries in grouped.items():
        ranked = sorted(entries, key=lambda pair: -pair[1])
        preferences[student_id] = [project_id for project_id, _ in ranked]

    return Instance(
        students=students,
        projects=projects,
        preferences=preferences,
    )


def load_gpas_from_csv(path: str) -> dict[int, float]:
    gpas: dict[int, float] = {}

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            student_id = parse_id(row["stu_id"])
            gpas[student_id] = float(row["gpa"])

    return gpas


def enrich_with_gpas(instance: Instance, gpas: dict[int, float]) -> Instance:
    missing = [s.id for s in instance.students if s.id not in gpas]
    if missing:
        raise KeyError(
            f"GPA ausente para os estudantes: {missing}. "
            "Verifique o CSV de GPAs."
        )

    new_students = tuple(
        replace(student, gpa=gpas[student.id]) for student in instance.students
    )

    sorted_student_ids = sorted(
        (s.id for s in instance.students),
        key=lambda sid: (-gpas[sid], sid),
    )

    school_priorities = {
        project.id: list(sorted_student_ids) for project in instance.projects
    }

    return Instance(
        students=new_students,
        projects=instance.projects,
        preferences=instance.preferences,
        school_priorities=school_priorities,
    )
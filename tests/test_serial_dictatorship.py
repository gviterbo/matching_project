from core.instance import Instance, Student, Project
from mechanisms.serial_dictatorship import serial_dictatorship


def test_sd_respects_order_and_capacity():
    students = (Student(id=1), Student(id=2), Student(id=3))
    projects = (Project(id=10, capacity=1), Project(id=11, capacity=1))
    preferences = {
        1: [10, 11],
        2: [10, 11],
        3: [10, 11],
    }
    instance = Instance(students=students, projects=projects, preferences=preferences)
    order = [1, 2, 3]

    result = serial_dictatorship(instance, order)

    assert result.project_of(1) == 10
    assert result.project_of(2) == 11
    assert result.project_of(3) is None
    assert result.unmatched_students() == [3]
    assert result.is_complete() is False

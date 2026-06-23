from core import Matching
from core.coalitions import Coalition, CoalitionInstance

def coalition_serial_dictatorship(
    coalition_instance: CoalitionInstance,
    order: list[Coalition] | None = None,
) -> Matching:
    if order is None:
        order = sorted(coalition_instance.groups, key=lambda group: -group.size)

    matching = Matching(coalition_instance.instance)

    capacities = {
        project.id: project.capacity
        for project in coalition_instance.instance.projects
    }

    for coalition in order:
        for project_id in coalition_instance.coalition_preferences(coalition):
            if capacities[project_id] >= coalition.size:
                for student_id in coalition.members:
                    matching.assign(student_id, project_id)

                capacities[project_id] -= coalition.size
                break

    return matching

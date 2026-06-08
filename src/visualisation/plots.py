import matplotlib.pyplot as plt
from collections import Counter
from core.matching import Matching

def plot_rank_distribution(matching: Matching):
    """
    Generates a bar chart showing the distribution of preference ranks obtained
    by students, including unassigned students and students assigned outside their choices.
    """
    ranks = []
    unassigned_count = len(matching.unmatched_students())
    outside_prefs_count = 0
    
    for student in matching.instance.students:
        if student.id in matching.assignments:
            rank = matching.project_rank_of(student.id)
            if rank is not None:
                ranks.append(rank)  # Convert 0-index to 1st choice, 2nd choice...
            else:
                outside_prefs_count += 1
                
    rank_counts = Counter(ranks)
    
    labels = []
    counts = []
    
    for r in sorted(rank_counts.keys()):
        labels.append(f"Rank {r}")
        counts.append(rank_counts[r])
        
    if outside_prefs_count > 0:
        labels.append("Outside Preferences")
        counts.append(outside_prefs_count)
        
    if unassigned_count > 0:
        labels.append("Unassigned")
        counts.append(unassigned_count)
        
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, counts, color="#1f77b4", edgecolor="black")
    
    ax.set_xlabel("Preference Rank")
    ax.set_ylabel("Number of Students")
    ax.set_title("Distribution of Assigned Preference Ranks")
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.xticks(rotation=45, ha='right')
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.1, int(yval), ha='center', va='bottom')
        
    plt.tight_layout()
    plt.show()


def plot_project_occupancy(matching: Matching):
    """
    Generates a stacked bar chart showing the occupancy rate of each project
    relative to its maximum capacity.
    """
    projects_data = []
    
    for project in matching.instance.projects:
        assigned_count = len(matching.students_in(project.id))
        capacity = project.capacity
        empty_slots = max(0, capacity - assigned_count)
        projects_data.append({
            "id": project.id,
            "assigned": assigned_count,
            "empty": empty_slots
        })
        
    projects_data.sort(key=lambda x: x["assigned"], reverse=True)
    
    project_ids = [f"Proj {p['id']}" for p in projects_data]
    assigned_counts = [p["assigned"] for p in projects_data]
    empty_slots = [p["empty"] for p in projects_data]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.bar(project_ids, assigned_counts, label="Occupied Slots", color="#2ca02c", edgecolor="black")
    ax.bar(project_ids, empty_slots, bottom=assigned_counts, label="Empty Slots", color="#ff7f0e", alpha=0.6, edgecolor="black")
    
    ax.set_ylabel("Number of Students / Capacity")
    ax.set_xlabel("Projects")
    ax.set_title("Project Occupancy vs Capacity")
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

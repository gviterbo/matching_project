import pandas as pd
import numpy as np
from core import Instance, Student, Project
from top_k_mallows import mallows_kendall as mk



##################### Real data #####################

def clean_preferences(df: pd.DataFrame) -> pd.DataFrame:
    """Remove missing values and keep rows where 'points' is between 0 and 100 inclusive."""
    df = df.dropna(subset=["stu_id", "proj_id", "points"]) # Remove rows with missing values
    df = df[df["points"].between(0, 100)] # Remove rows with invalid points
    df = df.sort_values("points", ascending=False).drop_duplicates(subset=["stu_id", "proj_id"]) # Keep the highest points for each student-project pair
    df["stu_id"] = df["stu_id"].str[4:].astype(int) # Converts the string STU_X to the int X
    df["proj_id"] = df["proj_id"].str[4:].astype(int) # Converts the string PRJ_X to the int X
    return df

def complete_preferences(df: pd.DataFrame) -> pd.DataFrame:
    """Add unranked projects with -1 points for each student to complete their preference list."""
    projects = df["proj_id"].unique()
    students = df["stu_id"].unique()

    full_index = pd.MultiIndex.from_product([students, projects], names=["stu_id", "proj_id"])
    df_complete = pd.DataFrame(index=full_index).reset_index() # Create a complete DataFrame with all student-project combinations

    df = pd.merge(df_complete, df, on=["stu_id", "proj_id"], how="left") # Merge with the original DataFrame to fill in existing points
    df["points"] = df["points"].fillna(-1) # Assign -1 points to unranked projects
    return df

def sort_preferences_with_tiebreak(df: pd.DataFrame) -> pd.DataFrame:
    """Shuffle data and sort by student (ascending) and points (descending) with stable tie-breaking."""
    df = df.sample(frac=1, random_state=42) # Shuffle the DataFrame to ensure random tie-breaking for projects with the same points
    df = df.sort_values(by=["stu_id", "points"], ascending=[True, False], kind="stable") # Sort the DataFrame by student ID (ascending) and points (descending) with stable sorting to maintain the random order for ties
    return df

def build_instance(df: pd.DataFrame, capacity: int) -> Instance:
    """Build the Instance object from the input DataFrame."""
    preferences = df.groupby("stu_id")["proj_id"].apply(list).to_dict() # Group project IDs into a sorted list for each student ID
    return Instance(
        students=tuple(Student(id=stu_id) for stu_id in preferences.keys()),
        projects=tuple(Project(id=int(proj_id), capacity=capacity) for proj_id in sorted(df["proj_id"].unique())),
        preferences=preferences
    )

def load_real_instance(file_path: str, capacity: int = 5) -> Instance:
    """Loads and processes a real-world matching instance from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file containing student preferences.
        capacity (int, default=5): Max capacity per project.
        
    Returns:
        Instance: Object with processed students, projects, and resolved preferences,
                  or None if a file/permission error occurs.
    """
    try:
        df = pd.read_csv(file_path)
        df = clean_preferences(df)
        df = complete_preferences(df)
        df = sort_preferences_with_tiebreak(df)
        instance = build_instance(df, capacity)
        return instance
    
    except FileNotFoundError:
        print(f"The specified file could not be found: {file_path}")
        return None
    
    except PermissionError:
        print(f"Insufficient permissions to read the file: {file_path}")
        return None



##################### Synthetic data #####################

def create_synthetic_instance(n_students, n_projects, capacity=5, phi=0.5, s0=None, seed=42):
    """Generates a matching problem instance with Mallows-model preferences.
    
    Args:
        n_students (int): Number of students.
        n_projects (int): Number of projects.
        capacity (int, default=5): Max capacity per project.
        phi (float, default=0.5): Dispersion (0: high consensus, 1: random).
        s0 (ndarray, optional): Consensus ranking. Defaults to [0, ..., n_projects-1].
        seed (int, default=42): Seed for reproducibility.
        
    Returns:
        Instance: Object with students, projects, and sorted preferences.
    """

    np.random.seed(seed)

    # Students preferences
    raw = mk.sample(m=n_students, n=n_projects, phi=phi, s0=s0) # raw[i][j] = rank of project j for student i -> argsort for ordered list
    
    # Project preferences
    gpas = np.random.choice([round(x * 0.01, 2) for x in range(401)], n_students, replace=False) # Generate unique GPAs between 0.00 and 4.00 for each student
    project_preferences = sorted(range(len(gpas)), key=lambda i: gpas[i], reverse=True) # List of student IDs sorted by GPA in descending order

    return Instance(
        students=tuple(Student(id=i, gpa=gpas[i]) for i in range(n_students)),
        projects=tuple(Project(id=j, capacity=capacity) for j in range(n_projects)),
        preferences={i: list(np.argsort(raw[i])) for i in range(n_students)},
        school_priorities={j: project_preferences for j in range(n_projects)}
    )

import pandas as pd
from core import Instance, Student, Project


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

def load_dataset(file_path: str, capacity: int = 5) -> Instance:
    try:
        df = pd.read_csv(file_path)
        df = clean_preferences(df)
        df = complete_preferences(df)
        df = sort_preferences_with_tiebreak(df)
        df = build_instance(df, capacity)
        return df
    
    except FileNotFoundError:
        print(f"Le fichier spécifié est introuvable : {file_path}")
        return None
    
    except PermissionError:
        print(f"Permissions insuffisantes pour lire le fichier : {file_path}")
        return None

import pandas as pd
import json


##################### Real data #####################

def clean_preferences(df: pd.DataFrame) -> pd.DataFrame:
    """Remove missing values and keep rows where 'points' is between 0 and 100 inclusive."""
    df = df.dropna(subset=["stu_id", "proj_id", "points"]) # Remove rows with missing values
    df = df[df["points"].between(0, 100)] # Remove rows with invalid points
    df = df.sort_values("points", ascending=False).drop_duplicates(subset=["stu_id", "proj_id"]) # Keep the highest points for each student-project pair
    return df

def complete_preferences(df: pd.DataFrame) -> pd.DataFrame:
    """Add unranked projects with 0 points for each student to complete their preference list."""
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

def build_preferences(df: pd.DataFrame) -> dict[str, list[str]]:
    """Group project IDs into an ordered list for each student ID."""
    preferences = df.groupby("stu_id")["proj_id"].apply(list).to_dict() # Group project IDs into a sorted list for each student ID
    return preferences


##################### Synthetic data #####################

pass


##################### Loaders #####################

def load_dataset(file_path: str, data_type: str = "real") -> dict[str, list[str]]:
    """Load and format the dataset from a file path based on the specified data type."""
    if data_type == "real":
        df = pd.read_csv(file_path)
        df = clean_preferences(df)
        df = complete_preferences(df)
        df = sort_preferences_with_tiebreak(df)
        return build_preferences(df)

    elif data_type == "synthetic":
        with open(file_path, "r") as f:
            return json.load(f)

    else:
        raise ValueError("Unknown data type. Choose 'real' or 'synthetic'.")

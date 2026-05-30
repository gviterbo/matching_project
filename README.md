# Matching User Preferences: Optimal Assignment of Students to Projects

## Description
This project addresses the matching problem for assigning students to projects. Each student submits an ordinal preference list of available projects, and the goal is to produce a satisfactory and fair final assignment.

While the previous DSAI project allocation used a linear program, this project aims to implement, compare, and evaluate classical algorithms on the same dataset, and then explore extensions beyond the standard one-sided, single-shot formulation.

The main theoretical foundation is based on Chapter 14 of the Handbook of Computational Social Choice (Klaus, Manlove, Rossi).

## Project Structure
```text
├── data/               # Raw and anonymized datasets
├── doc/                # Project documentation and planning
├── notebooks/          # Jupyter notebooks for exploration and prototyping
├── src/                # Source code of the project
│   ├── core/           # Core data structures (instances, matchings)
│   ├── data/           # Data loading utilities
│   ├── mechanisms/     # Implementation of matching algorithms (SD, GS, TTC)
│   └── metrics/        # Evaluation metrics (cost, stability)
├── tests/              # Unit tests
├── .gitignore          # Specifies intentionally untracked files to ignore
├── LICENSE             # Legal terms and permissions for project reuse
├── project.toml        # Project metadata and pytest configuration
├── README.md           # Main documentation and project overview
└── requirements.txt    # List of required Python packages and dependencies
```

## Installation

### Prerequisites
* Python 3.10 or higher
* pip or conda package manager

### Instructions
1. Clone the repository :
```bash
git clone git@github.com:gviterbo/matching_project.git # cloning via ssh
cd matching_project
```

2. Create a virtual environment :
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows : .venv\Scripts\activate
```

3. Install dependencies :
```bash
pip install -r requirements.txt
```

## Usage
**TODO :** Explains how to execute the scripts and run the matching algorithms with concrete command-line examples.

## Data

### Source
* **Real Data :** Anonymized data from the DSAI project matching (April 2026).
* **Synthetic Data :** Generated according to controlled preference models for testing purposes.

### Format
The dataset is structured as a CSV file located in the `data/` directory, using the following schema :

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `proj_id` | String | Unique identifier for the project. |
| `points` | Integer | Preference weight assigned by the student to the project (from 0 to 100, where 100 represents the highest preference). |
| `stu_id` | String | Unique identifier for the student (anonymized). |

### Example
```csv
proj_id,points,stu_id
PRJ_002,100,STU_074
PRJ_003,85,STU_074
```

## Contributors
* Gabriel Pereira Viterbo - Student
* Gwendal Deléage - Student
* Jasser Mejri - Student
* Rafael Sesoko - Student
* Sébastien Rivière - Student
* Ekhine Irurozki Arrieta - Supervisor

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

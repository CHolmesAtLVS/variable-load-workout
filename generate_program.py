"""
Generate a variable load workout program based on StrongFirst principles.
Reads TRM values from data/trm.csv and outputs a 12-session program.
All weights are in pounds (lbs).
"""
import csv
from typing import Dict, List, Any
from datetime import date

# Define the training tables as per README
TRAINING_TABLES = {
    "A": {
        "Main Lifts": [
            ("Deadlift", "Hip Hinge"),
            ("Barbell Military Press", "Vertical Press"),
            ("Barbell Back Squat", "Squat"),
            ("Bench Press", "Horizontal Press"),
        ],
        "SV Lifts": [
            ("Romanian Deadlift", "Hip Hinge"),
            ("Overhead Dumbbell Press", "Vertical Press"),
            ("Barbell Front Squat", "Squat"),
            ("Incline Dumbbell Press", "Horizontal Press"),
        ],
    },
    "B": {
        "Main Lifts": [
            ("Chin-Ups", "Vertical Pull"),
            ("Barbell Dead Row", "Horizontal Pull"),
            ("Deadlift", "Hip Hinge"),
            ("Barbell Military Press", "Vertical Press"),
        ],
        "SV Lifts": [
            ("Close Grip Pull-downs", "Vertical Pull"),
            ("One Arm Row", "Horizontal Pull"),
            ("Romanian Deadlift", "Hip Hinge"),
            ("Overhead Dumbbell Press", "Vertical Press"),
        ],
    },
    "C": {
        "Main Lifts": [
            ("Barbell Back Squat", "Squat"),
            ("Bench Press", "Horizontal Press"),
            ("Chin-Ups", "Vertical Pull"),
            ("Barbell Dead Row", "Horizontal Pull"),
        ],
        "SV Lifts": [
            ("Barbell Front Squat", "Squat"),
            ("Incline Dumbbell Press", "Horizontal Press"),
            ("Close Grip Pull-downs", "Vertical Pull"),
            ("One Arm Row", "Horizontal Pull"),
        ],
    },
}

# 12-session progression as per README
SESSION_PROGRESSIONS = [
    {"main": (5, 2, 0.70), "sv": (6, 3, "10RM")},
    {"main": (2, 5, 0.85), "sv": (3, 5, "5RM")},
    {"main": (5, 2, 0.75), "sv": (5, 4, "8RM")},
    {"main": (3, 3, 0.80), "sv": (4, 5, "6RM")},
    {"main": (5, 2, 0.70), "sv": (6, 3, "10RM")},
    {"main": (1, 6, 0.90), "sv": (3, 5, "5RM")},
    {"main": (2, 5, 0.75), "sv": (5, 4, "8RM")},
    {"main": (2, 3, 0.85), "sv": (4, 5, "6RM")},
    {"main": (5, 2, 0.70), "sv": (6, 3, "10RM")},
    {"main": (2, 3, 0.85), "sv": (3, 5, "5RM")},
    {"main": (2, 5, 0.75), "sv": (5, 4, "8RM")},
    {"main": (3, 4, 0.80), "sv": (4, 5, "6RM")},
]

RM_TO_COL = {
    "1RM": "TRM-1RM (lbs)",
    "2RM": "TRM-2RM (lbs)",
    "3RM": "TRM-3RM (lbs)",
    "4RM": "TRM-4RM (lbs)",
    "5RM": "TRM-5RM (lbs)",
    "6RM": "TRM-6RM (lbs)",
    "7RM": "TRM-7RM (lbs)",
    "8RM": "TRM-8RM (lbs)",
    "9RM": "TRM-9RM (lbs)",
    "10RM": "TRM-10RM (lbs)",
}


def load_trm(filepath: str) -> Dict[str, Dict[str, Any]]:
    """
    Load TRM data from CSV. Returns a dict mapping exercise name to TRM values.
    """
    trm_data: Dict[str, Dict[str, Any]] = {}
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row["Exercise"].strip().strip('"')
            trm_data[name] = row
    return trm_data


def get_trm(row: Dict[str, Any], percent: float = None, rm: str = None) -> float:
    """
    Get TRM for a given row, either by percent of 1RM or by RM column.
    """
    if percent is not None:
        try:
            base = float(row["TRM-1RM (lbs)"])
            return round(base * percent, 2)
        except (KeyError, ValueError):
            return 0.0
    if rm is not None and rm in RM_TO_COL:
        try:
            return float(row[RM_TO_COL[rm]])
        except (KeyError, ValueError):
            return 0.0
    return 0.0


def generate_program(trm_data: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate the 12-session program as a list of dicts.
    """
    program: List[Dict[str, Any]] = []
    table_order = ["A", "B", "C", "B", "C", "A", "C", "A", "B", "A", "B", "C"]  # Example rotation
    for session_idx, session in enumerate(SESSION_PROGRESSIONS):
        table = table_order[session_idx % len(table_order)]
        lifts = TRAINING_TABLES[table]
        entry = {"Session": session_idx + 1, "Table": table, "Main": [], "SV": []}
        # Main lifts
        reps, sets, percent = session["main"]
        for ex, _ in lifts["Main Lifts"]:
            if isinstance(percent, float):
                weight = get_trm(trm_data.get(ex, {}), percent=percent)
            else:
                weight = 0.0
            entry["Main"].append({"Exercise": ex, "Sets": sets, "Reps": reps, "Weight (lbs)": weight})
        # SV lifts
        sv_reps, sv_sets, sv_rm = session["sv"]
        for ex, _ in lifts["SV Lifts"]:
            weight = get_trm(trm_data.get(ex, {}), rm=sv_rm)
            entry["SV"].append({"Exercise": ex, "Sets": sv_sets, "Reps": sv_reps, "Weight (lbs)": weight})
        program.append(entry)
    return program


def print_program(program: List[Dict[str, Any]]) -> None:
    """
    Print the generated program in a readable format.
    """
    for session in program:
        print(f"Session {session['Session']} (Table {session['Table']}):")
        print("  Main Lifts:")
        for lift in session["Main"]:
            print(f"    - {lift['Exercise']}: {lift['Sets']}x{lift['Reps']} @ {lift['Weight (lbs)']} lbs")
        print("  Specialized Variety (SV) Lifts:")
        for lift in session["SV"]:
            print(f"    - {lift['Exercise']}: {lift['Sets']}x{lift['Reps']} @ {lift['Weight (lbs)']} lbs")
        print()


def main() -> None:
    """
    Main entry point. Loads TRM data and prints the program.
    """
    trm_data = load_trm("data/trm.csv")
    program = generate_program(trm_data)
    print_program(program)


if __name__ == "__main__":
    main()

"""
Generate a variable load workout program based on StrongFirst principles.
Reads TRM values from data/trm.csv and outputs a 12-session program.
All weights are in pounds (lbs).
"""
import csv
import sqlite3
from typing import Dict, List, Any
from datetime import date, datetime
import os

RM_TO_COL = {
    "1RM": "TRM_1RM",
    "2RM": "TRM_2RM",
    "3RM": "TRM_3RM",
    "4RM": "TRM_4RM",
    "5RM": "TRM_5RM",
    "6RM": "TRM_6RM",
    "7RM": "TRM_7RM",
    "8RM": "TRM_8RM",
    "9RM": "TRM_9RM",
    "10RM": "TRM_10RM",
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


def load_trm_from_db(db_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Load TRM data from the trm table in the SQLite database. Returns a dict mapping exercise name to TRM values.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM trm")
    columns = [desc[0] for desc in cur.description]
    trm_data: Dict[str, Dict[str, Any]] = {}
    for row in cur.fetchall():
        row_dict = dict(zip(columns, row))
        name = row_dict["Exercise"].strip().strip('"')
        trm_data[name] = row_dict
    conn.close()
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


def get_trm_with_rm(row: Dict[str, Any], percent: float = None, rm: str = None) -> str:
    """
    Get TRM for a given row, either by percent of 1RM or by RM column, and return as a string with RM in brackets.
    """
    weight = get_trm(row, percent=percent, rm=rm)
    if rm is not None:
        return f"{weight} lbs [{rm}]"
    elif percent is not None:
        return f"{weight} lbs [1RM x {percent:.0%}]"
    return f"{weight} lbs"


def load_session_plan(db_path: str) -> Dict[str, Dict[str, List[str]]]:
    """
    Load the session plan from the SessionsPlan table in the SQLite database.
    Returns a dict: {SessionName: {"Main": [ex1, ex2, ...], "SV": [ex3, ...]}}
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT SessionName, ExerciseCode, Exercise FROM SessionsPlan")
    plan: Dict[str, Dict[str, List[str]]] = {}
    for session, code, exercise in cur.fetchall():
        if session not in plan:
            plan[session] = {"Main": [], "SV": []}
        if code.startswith("Main-"):
            plan[session]["Main"].append(exercise)
        elif code.startswith("SV-"):
            plan[session]["SV"].append(exercise)
    conn.close()
    return plan


def load_session_progression(db_path: str) -> List[Dict[str, Any]]:
    """
    Load session progression (reps, sets, TRM) from SVRepSetScheme table.
    Returns a list of dicts, one per session.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT Reps, Sets, Number_TRM, TRM FROM SVRepSetScheme ORDER BY Session_Number ASC")
    progression = [
        {"reps": row[0], "sets": row[1], "number_trm": row[2], "trm": row[3]} for row in cur.fetchall()
    ]
    conn.close()
    return progression


def load_main_session_progression(db_path: str) -> List[Dict[str, Any]]:
    """
    Load main lift session progression (reps, sets, TRM) from MainLiftsRepSetScheme table.
    Returns a list of dicts, one per session.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT Reps, Sets, Number_TRM, TRM FROM MainLiftsRepSetScheme ORDER BY Session_Number ASC")
    progression = [
        {"reps": row[0], "sets": row[1], "number_trm": row[2], "trm": row[3]} for row in cur.fetchall()
    ]
    conn.close()
    return progression


def normalize_rm(trm: str) -> str:
    """
    Convert '10TRM' to '10RM', etc., for column lookup.
    """
    if trm.endswith('TRM'):
        return trm.replace('TRM', 'RM')
    return trm


def generate_program(trm_data: Dict[str, Dict[str, Any]], session_plan: Dict[str, Dict[str, List[str]]], main_progression: List[Dict[str, Any]], sv_progression: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate the program as a list of dicts using the session plan and both main/SV progression from the database.
    """
    program: List[Dict[str, Any]] = []
    session_names = list(session_plan.keys())
    for idx in range(min(len(main_progression), len(sv_progression))):
        table = session_names[idx % len(session_names)]
        lifts = session_plan[table]
        main_rm = normalize_rm(main_progression[idx]["trm"])
        sv_rm = normalize_rm(sv_progression[idx]["trm"])
        entry = {"Session": idx + 1, "Table": table, "Main": [], "SV": []}
        # Main lifts
        for ex in lifts["Main"]:
            weight_str = get_trm_with_rm(trm_data.get(ex, {}), rm=main_rm)
            entry["Main"].append({"Exercise": ex, "Sets": main_progression[idx]["sets"], "Reps": main_progression[idx]["reps"], "Weight": weight_str})
        # SV lifts
        for ex in lifts["SV"]:
            weight_str = get_trm_with_rm(trm_data.get(ex, {}), rm=sv_rm)
            entry["SV"].append({"Exercise": ex, "Sets": sv_progression[idx]["sets"], "Reps": sv_progression[idx]["reps"], "Weight": weight_str})
        program.append(entry)
    return program


def print_program(program: List[Dict[str, Any]]) -> None:
    """
    Print the generated program in a readable format.
    """
    for session in program:
        # Map SessionA -> Plan A, SessionB -> Plan B, etc.
        plan_letter = session['Table'].replace('Session', 'Plan ')
        print(f"Session {session['Session']}, ({plan_letter}):")
        print("  Main Lifts:")
        for lift in session["Main"]:
            print(f"    - {lift['Exercise']}: {lift['Sets']}x{lift['Reps']} @ {lift['Weight']}")
        print("  Specialized Variety (SV) Lifts:")
        for lift in session["SV"]:
            print(f"    - {lift['Exercise']}: {lift['Sets']}x{lift['Reps']} @ {lift['Weight']}")
        print()


def export_plan_to_file(plan: List[Dict[str, Any]]) -> None:
    """
    Exports the generated plan to a text file in the data/samples directory.
    The file is named plan-<current_date_and_time>.txt.
    """
    # Ensure the samples directory exists
    samples_dir = "data/samples"
    os.makedirs(samples_dir, exist_ok=True)

    # Generate the filename with the current date and time
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(samples_dir, f"plan-{current_time}.txt")

    # Write the plan to the file
    with open(filename, "w") as file:
        for session in plan:
            plan_letter = session['Table'].replace('Session', 'Plan ')
            file.write(f"Session {session['Session']}, ({plan_letter}):\n")
            file.write("  Main Lifts:\n")
            for lift in session["Main"]:
                file.write(f"    - {lift['Exercise']}: {lift['Sets']}x{lift['Reps']} @ {lift['Weight']}\n")
            file.write("  Specialized Variety (SV) Lifts:\n")
            for lift in session["SV"]:
                file.write(f"    - {lift['Exercise']}: {lift['Sets']}x{lift['Reps']} @ {lift['Weight']}\n")
            file.write("\n")
    print(f"Plan exported to {filename}")


def main() -> None:
    """
    Main entry point. Loads TRM data, session plan, and both main/SV session progression from the database, then prints the program.
    """
    db_path = "data/workout.db"
    trm_data = load_trm_from_db(db_path)
    session_plan = load_session_plan(db_path)
    main_progression = load_main_session_progression(db_path)
    sv_progression = load_session_progression(db_path)
    program = generate_program(trm_data, session_plan, main_progression, sv_progression)
    print_program(program)
    export_plan_to_file(program)


if __name__ == "__main__":
    main()

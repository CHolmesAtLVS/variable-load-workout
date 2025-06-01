"""
Validation script for SessionsPlan table in workout.db.
Checks rules and proposes solutions if validation fails.
"""
import sqlite3
from typing import List, Tuple

def get_session_exercise_counts(db_path: str) -> List[Tuple[str, int]]:
    """
    Returns a list of (SessionName, count) for number of exercises in each session.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT SessionName, COUNT(*) FROM SessionsPlan GROUP BY SessionName;")
    results = cur.fetchall()
    conn.close()
    return results

def validate_sessions_have_8_exercises(db_path: str) -> bool:
    """
    Validates that each session has exactly 8 exercises.
    Returns True if all sessions pass, False otherwise.
    """
    counts = get_session_exercise_counts(db_path)
    failed = [(name, count) for name, count in counts if count != 8]
    if not failed:
        print("PASS: All sessions have exactly 8 exercises.")
        return True
    print("FAIL: The following sessions do not have 8 exercises:")
    for name, count in failed:
        print(f"  - {name}: {count} exercises")
    print("Proposed solution: Ensure each session (SessionA, SessionB, SessionC, etc.) has exactly 8 rows in SessionsPlan.")
    return False

def get_sessionsplan_exercises(db_path: str) -> List[str]:
    """
    Returns a list of unique exercise names from SessionsPlan.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT Exercise FROM SessionsPlan;")
    results = [row[0] for row in cur.fetchall()]
    conn.close()
    return results

def get_trm_exercises(db_path: str) -> List[str]:
    """
    Returns a list of unique exercise names from trm.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT Exercise FROM trm;")
    results = [row[0] for row in cur.fetchall()]
    conn.close()
    return results

def validate_sessionsplan_exercises_in_trm(db_path: str) -> bool:
    """
    Validates that all exercises in SessionsPlan exist in trm.
    Returns True if all pass, False otherwise, and proposes a solution for each missing exercise.
    """
    plan_exs = set(get_sessionsplan_exercises(db_path))
    trm_exs = set(get_trm_exercises(db_path))
    missing = plan_exs - trm_exs
    if not missing:
        print("PASS: All exercises in SessionsPlan exist in trm.")
        return True
    print("FAIL: The following exercises are missing from trm:")
    for ex in missing:
        print(f"  - {ex}")
    print("Proposed solution: For each missing exercise, either add it to the trm table with appropriate TRM values, or update SessionsPlan to use an exercise that exists in trm.")
    return False

def validate_required_exercise_codes(db_path: str) -> bool:
    """
    Validates that each session has all required exercise codes: Main-A1, Main-A2, SV-C1, SV-C2, SV-D1, SV-D2.
    Returns True if all sessions pass, False otherwise, and proposes a solution for each missing code.
    """
    required_codes = {"Main-A1", "Main-A2", "SV-C1", "SV-C2", "SV-D1", "SV-D2"}
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT SessionName, ExerciseCode FROM SessionsPlan;")
    session_codes = {}
    for session, code in cur.fetchall():
        session_codes.setdefault(session, set()).add(code)
    conn.close()
    all_pass = True
    for session, codes in session_codes.items():
        missing = required_codes - codes
        if missing:
            all_pass = False
            print(f"FAIL: {session} is missing required codes: {', '.join(sorted(missing))}")
    if all_pass:
        print("PASS: All sessions have required exercise codes: Main-A1, Main-A2, SV-C1, SV-C2, SV-D1, SV-D2.")
        return True
    print("Proposed solution: Add the missing exercise codes to each session in SessionsPlan.")
    return False

def main():
    db_path = "data/workout.db"
    all_pass = True
    if not validate_sessions_have_8_exercises(db_path):
        all_pass = False
    if not validate_sessionsplan_exercises_in_trm(db_path):
        all_pass = False
    if not validate_required_exercise_codes(db_path):
        all_pass = False
    if all_pass:
        print("All validation rules passed.")

if __name__ == "__main__":
    main()

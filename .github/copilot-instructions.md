# Copilot Python Instructions
- Use type hints for all Python functions.
- Prefer list comprehensions over loops when possible.
- Follow PEP8 style guidelines.
- Use descriptive variable and function names.
- Write docstrings for all public functions and classes.
- After making a change, run the script to ensure it works as expected.  If there are errors, fix them.
- Do not update or change the database from /workspaces/variable-load-workout/generate_program.py.  That script should only generate the workout program and not modify the database.

# Copilot Weight Lifting Instructions
- Use pounds (lbs) for weight measurements.
- The ./docs/workout_description.md file contains the workout program details.  It is a sample, and to be used only for structure and reference.


# Copilot Database Instructions
- Use SQLAlchemy for database interactions.
- The database is SQLite.  The file is located at '/workspaces/variable-load-workout/data/workout.db'.
- The anyquery MCP server can help chat wih data.  It is read-only.  Use it to query because it is faster than using the database directly.

## References
- [GitHub Copilot Custom Instructions Documentation](https://docs.github.com/en/copilot/using-github-copilot/configuring-github-copilot/repository-custom-instructions-for-github-copilot)

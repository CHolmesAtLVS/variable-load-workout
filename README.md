# variable-load-workout
A Python script to generate a variable load workout program based on the StrongFirst principles, focusing on strength, hypertrophy, and body composition.

---

## 💪 Full-Body Strength & Hypertrophy Program (StrongFirst-Inspired)

This project provides a flexible, rotating workout program for strength, muscle mass, and body composition, inspired by StrongFirst principles. The program features:

- 3 rotating training days (Table A, B, C)
- 3 sessions per week, 12 sessions per cycle
- Alternating paired sets, no failure training, and TRM-based progression

For the full program details, including movement patterns, training tables, session rotation, and progression, see [docs/workout_description.md](./docs/workout_description.md).

---

## 🗄️ MCP Server: anyquery (SQLite-backed)

This project can use the [anyquery](https://github.com/julien-c/anyquery) MCP server to provide a lightweight SQL API over your TRM data (or any SQLite database). This enables advanced querying and integration with other tools.

### Installation

Run the following commands to install anyquery on Ubuntu:

```bash
echo "deb [trusted=yes] https://apt.julienc.me/ /" | sudo tee /etc/apt/sources.list.d/anyquery.list
sudo apt update
sudo apt install anyquery
```

### Usage

- By default, anyquery can serve any SQLite database file (such as your TRM data) over HTTP with a simple REST API.
- See the [anyquery documentation](https://github.com/julien-c/anyquery) for details on configuration and usage.

---

# Daily Number Incrementer

A lightweight Python utility that increments a number in `number.txt`, creates Git commits with proper timezone-aware timestamps, and pushes them directly to GitHub.

## Usage

Runs with Python standard library (no extra dependencies required).

### Run Once
Increments the counter by 1, commits the change, and pushes to GitHub:

```bash
python update_number.py
```

### Run Multiple Times
Specify the number of iterations directly:

```bash
# Run 10 times
python update_number.py 10

# Or using the -n flag
python update_number.py -n 25
```

### Optional Modes

- **Conventional Commit Messages**:
  ```bash
  python update_number.py 5 --conventional
  ```
  Generates clean Conventional Commits (e.g. `feat(core): update sequential counter to 665`).

- **Streak Mode**:
  ```bash
  python update_number.py --streak 7
  ```
  Generates commits spanning back the specified number of days to backfill or maintain streaks.

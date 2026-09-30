#!/usr/bin/env python3
"""
Daily Number Incrementer
Updates a sequential counter in number.txt, commits the change to Git,
and pushes directly to GitHub.
"""

import argparse
import os
import random
import subprocess
import sys
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NUMBER_FILE = os.path.join(SCRIPT_DIR, "number.txt")


def read_number() -> int:
    """Read the current counter from number.txt."""
    if not os.path.exists(NUMBER_FILE):
        return 0
    with open(NUMBER_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        return int(content) if content else 0


def write_number(num: int) -> None:
    """Write the updated counter to number.txt."""
    with open(NUMBER_FILE, "w", encoding="utf-8") as f:
        f.write(str(num))


def generate_commit_message(num: int, dt: datetime, style: str = "number") -> str:
    """Generate a clean commit message."""
    date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    if style == "conventional":
        types = ["feat", "fix", "chore", "refactor", "docs", "style"]
        scopes = ["core", "tracker", "deps", "config", "utils", "api"]
        subjects = [
            f"update sequential counter to {num}",
            f"sync latest count {num}",
            f"increment daily tracker to {num}",
            f"record iteration {num}",
        ]
        return f"{random.choice(types)}({random.choice(scopes)}): {random.choice(subjects)}"
    return f"Update number: {num} ({date_str})"


def git_commit(commit_date: datetime, num: int, message_style: str = "number") -> bool:
    """Stage number.txt and create a Git commit with a timezone-aware timestamp."""
    # Ensure number.txt is staged
    subprocess.run(["git", "add", "number.txt"], cwd=SCRIPT_DIR, check=True)

    # Attach local timezone offset
    if commit_date.tzinfo is None:
        commit_date = commit_date.astimezone()

    iso_date = commit_date.isoformat()
    commit_msg = generate_commit_message(num, commit_date, style=message_style)

    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = iso_date
    env["GIT_COMMITTER_DATE"] = iso_date

    res = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=SCRIPT_DIR,
        env=env,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        if "nothing to commit" in res.stdout or "nothing to commit" in res.stderr:
            return False
        print(f"Error during commit: {res.stderr}")
        return False
    return True


def git_push() -> bool:
    """Push local commits to GitHub."""
    print("Pushing commits to GitHub...")
    res = subprocess.run(["git", "push"], cwd=SCRIPT_DIR, capture_output=True, text=True)
    if res.returncode == 0:
        print("Successfully pushed to GitHub!")
        return True
    print(f"Error pushing to GitHub:\n{res.stderr}")
    return False


def run_single(message_style: str = "number") -> None:
    """Run exactly 1 increment, commit, and push."""
    current = read_number()
    new_number = current + 1
    write_number(new_number)
    now = datetime.now().astimezone()

    if git_commit(now, new_number, message_style=message_style):
        print(f"[+] Updated counter: {current} -> {new_number} ({now.strftime('%Y-%m-%d %H:%M:%S')})")
    git_push()


def run_batch(count: int, message_style: str = "number") -> None:
    """Run N increments and commits in sequence, then push."""
    if count <= 0:
        print("Count must be at least 1.")
        return

    start_num = read_number()
    now = datetime.now().astimezone()
    print(f"Running {count} iterations starting from {start_num}...")

    success_count = 0
    for i in range(count):
        current = read_number()
        new_number = current + 1
        write_number(new_number)
        commit_time = now + timedelta(seconds=i)

        if git_commit(commit_time, new_number, message_style=message_style):
            success_count += 1
            print(f"  [{i+1}/{count}] Committed number: {new_number}")

    final_num = read_number()
    print(f"Created {success_count} commits ({start_num} -> {final_num}).")
    git_push()


def run_streak(days: int, message_style: str = "number") -> None:
    """Run streak mode across past N days."""
    if days <= 0:
        print("Days must be at least 1.")
        return

    start_num = read_number()
    now = datetime.now().astimezone()
    start_date = now - timedelta(days=days - 1)
    print(f"Generating a {days}-day streak from {start_date.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}...")

    for i in range(days):
        current_date = (start_date + timedelta(days=i)).replace(
            hour=now.hour, minute=now.minute, second=now.second
        )
        current = read_number()
        new_number = current + 1
        write_number(new_number)
        git_commit(current_date, new_number, message_style=message_style)
        print(f"  Day {i+1}/{days} ({current_date.strftime('%Y-%m-%d')}): number -> {new_number}")

    final_num = read_number()
    print(f"Completed streak ({start_num} -> {final_num}).")
    git_push()


def main():
    parser = argparse.ArgumentParser(
        description="Daily Number Incrementer: Increments number.txt, commits to Git, and pushes to GitHub."
    )
    parser.add_argument(
        "times",
        nargs="?",
        type=int,
        default=None,
        help="Number of times to run (default: 1)",
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=None,
        help="Number of times to run",
    )
    parser.add_argument(
        "--streak",
        type=int,
        default=None,
        metavar="DAYS",
        help="Generate commits spanning past N days for streak",
    )
    parser.add_argument(
        "--conventional",
        action="store_true",
        help="Use Conventional Commits format (e.g. feat(core): ...)",
    )

    args = parser.parse_args()
    style = "conventional" if args.conventional else "number"

    if args.streak is not None:
        run_streak(args.streak, message_style=style)
    else:
        # Determine count
        count = 1
        if args.count is not None:
            count = args.count
        elif args.times is not None:
            count = args.times

        if count == 1:
            run_single(message_style=style)
        else:
            run_batch(count, message_style=style)


if __name__ == "__main__":
    main()

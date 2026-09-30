#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime

import sys
from datetime import datetime, timedelta

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


def read_number():
    with open("number.txt", "r") as f:
        return int(f.read().strip())


def write_number(num):
    with open("number.txt", "w") as f:
        f.write(str(num))


_generator = None


def get_generator():
    global _generator
    if _generator is None:
        from transformers import logging, pipeline
        logging.set_verbosity_error()
        _generator = pipeline(
            "text-generation",
            model="openai-community/gpt2",
        )
    return _generator


def generate_random_commit_message():
    import random
    import re
    try:
        generator = get_generator()
        prompt = (
            "Generate a short Git commit message following Conventional Commits format (e.g., feat(auth): add login endpoint).\n"
            "Commit message: "
        )
        generated = generator(
            prompt,
            max_new_tokens=30,
            num_return_sequences=1,
            temperature=0.8,
            top_k=50,
            top_p=0.9,
            truncation=True,
            return_full_text=False,
        )
        new_text = generated[0]["generated_text"].strip()
        first_line = new_text.splitlines()[0].strip() if new_text else ""
        first_line = re.sub(r'^[-\s*`"\'`]+', '', first_line).strip()
        if len(first_line) > 5:
            return first_line
    except Exception as e:
        pass

    types = ["feat", "fix", "chore", "refactor", "docs", "style"]
    scopes = ["core", "tracker", "deps", "config", "utils", "api"]
    subjects = ["update sequential counter", "increment daily count", "optimize streak calculation", "sync latest number"]
    return f"{random.choice(types)}({random.choice(scopes)}): {random.choice(subjects)}"



def git_commit(commit_date=None, num=None):
    # Stage the changes
    subprocess.run(["git", "add", "number.txt"])
    
    env = os.environ.copy()
    if commit_date is None:
        if "FANCY_JOB_DATE" in os.environ:
            commit_date = datetime.strptime(os.environ["FANCY_JOB_DATE"], "%Y-%m-%d").astimezone()
        else:
            commit_date = datetime.now().astimezone()
    else:
        if commit_date.tzinfo is None:
            commit_date = commit_date.astimezone()

    date_str = commit_date.strftime("%Y-%m-%d %H:%M:%S")
    iso_date = commit_date.isoformat()

    if "FANCY_JOB_USE_LLM" in os.environ:
        commit_message = generate_random_commit_message()
    else:
        if num is not None:
            commit_message = f"Update number: {num} ({date_str})"
        else:
            commit_message = f"Update number: {date_str}"
        
    env["GIT_AUTHOR_DATE"] = iso_date
    env["GIT_COMMITTER_DATE"] = iso_date
    subprocess.run(["git", "commit", "-m", commit_message], env=env)


def git_push():
    # Push the committed changes to GitHub
    result = subprocess.run(["git", "push"], capture_output=True, text=True)
    if result.returncode == 0:
        print("Changes pushed to GitHub successfully.")
    else:
        print("Error pushing to GitHub:")
        print(result.stderr)


def git_gc():
    # Repack loose objects and prune git cache
    subprocess.run(["git", "gc", "--prune=now", "--quiet"])


def main():
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--streak":
            num_days = int(sys.argv[2]) if len(sys.argv) > 2 else 21
            start_date = datetime.now() - timedelta(days=num_days - 1)
            print(f"Generating a {num_days}-day streak from {start_date.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}...")
            for i in range(num_days):
                current_date = start_date + timedelta(days=i)
                current_number = read_number()
                new_number = current_number + 1
                write_number(new_number)
                git_commit(commit_date=current_date, num=new_number)
            git_push()
            git_gc()
        elif len(sys.argv) > 1 and sys.argv[1] in ("--today", "--count"):
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 25
            now = datetime.now()
            print(f"Generating {count} commits for today ({now.strftime('%Y-%m-%d')})...")
            for i in range(count):
                commit_time = now + timedelta(seconds=i)
                current_number = read_number()
                new_number = current_number + 1
                write_number(new_number)
                git_commit(commit_date=commit_time, num=new_number)
            git_push()
            git_gc()
        else:
            current_number = read_number()
            new_number = current_number + 1
            write_number(new_number)
            git_commit(num=new_number)
            git_push()
            git_gc()
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()

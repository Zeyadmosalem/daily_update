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


def generate_random_commit_message():
    from transformers import pipeline

    generator = pipeline(
        "text-generation",
        model="openai-community/gpt2",
    )
    prompt = """
        Generate a Git commit message following the Conventional Commits standard. The message should include a type, an optional scope, and a subject.Please keep it short. Here are some examples:

        - feat(auth): add user authentication module
        - fix(api): resolve null pointer exception in user endpoint
        - docs(readme): update installation instructions
        - chore(deps): upgrade lodash to version 4.17.21
        - refactor(utils): simplify date formatting logic

        Now, generate a new commit message:
    """
    generated = generator(
        prompt,
        max_new_tokens=50,
        num_return_sequences=1,
        temperature=0.9,  # Slightly higher for creativity
        top_k=50,  # Limits sampling to top 50 logits
        top_p=0.9,  # Nucleus sampling for diversity
        truncation=True,
    )
    text = generated[0]["generated_text"]

    if "- " in text:
        return text.rsplit("- ", 1)[-1].strip()
    else:
        raise ValueError(f"Unexpected generated text {text}")


def git_commit(commit_date=None):
    # Stage the changes
    subprocess.run(["git", "add", "number.txt"])
    
    if commit_date is None:
        if "FANCY_JOB_DATE" in os.environ:
            commit_date = datetime.strptime(os.environ["FANCY_JOB_DATE"], "%Y-%m-%d")
        else:
            commit_date = datetime.now()

    date_str = commit_date.strftime("%Y-%m-%d")
    iso_date = commit_date.strftime("%Y-%m-%dT12:00:00")

    if "FANCY_JOB_USE_LLM" in os.environ:
        commit_message = generate_random_commit_message()
    else:
        commit_message = f"Update number: {date_str}"
        
    env = os.environ.copy()
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
                git_commit(commit_date=current_date)
            git_push()
            git_gc()
        else:
            current_number = read_number()
            new_number = current_number + 1
            write_number(new_number)
            git_commit()
            git_push()
            git_gc()
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()

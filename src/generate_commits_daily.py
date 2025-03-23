import random
import subprocess
import sys
from datetime import datetime

def run_git_command(command):
    """Run a git command in the shell."""
    subprocess.run(command, shell=True, check=True)

def generate_commits_for_date(commit_date):
    max_commits = 40
    num_commits = random.randint(1, max_commits)  # At least 1 commit per day

    messages = [
        "Scrum meetings are a waste of time"
        "Scrum is a scam",
        "Scrum Master or Scrum slave, that is the question",
        "Scrum kills productivity",
        "Scrum kills trust",
        "Scrum = lack of trust",
        "Scrum kills team spirit",
        "We don't need no thought control"
        "Developers are not your kids",
        "Trust your experts",
        "Scrum is a mask to hide micromanagement",
    ]

    for _ in range(num_commits):
        commit_hour = random.randint(0, 23)
        commit_minute = random.randint(0, 59)
        commit_second = random.randint(0, 59)
        commit_time = commit_date.replace(hour=commit_hour, minute=commit_minute, second=commit_second)
        commit_time_str = commit_time.strftime("%Y-%m-%d %H:%M:%S")

        fake_file = "assets/fake_file.txt"

        with open(fake_file, "a") as f:
            f.write(f"Commit on {commit_time_str}\n")

        run_git_command(f"git add {fake_file}")
        commit_message = random.choice(messages)
        run_git_command(f'GIT_COMMITTER_DATE="{commit_time_str}" git commit -m "{commit_message}" --date="{commit_time_str}"')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_commits.py YYYY-MM-DD")
        sys.exit(1)

    age_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
    generate_commits_for_date(age_date)

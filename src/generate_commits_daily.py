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
        "Most Scrum meetings are a waste of time",
        "Scrum is a scam?",
        "Scrum Master or Scrum slave, that is the question",
        "A bad Scrum can kill productivity",
        "A bad Scrum kills trust",
        "A bad Scrum == lack of trust",
        "A bad Scrum kills team spirit",
        "We don't need no thought control",
        "Developers are not your kids",
        "Trust your experts",
        "Scrum can be a mask to hide micromanagement",
        "Scrum can boost micromanagement",
        "Scrum can worsen a toxic culture",
        "Scrum is not the answer to life universe and everything",
        "To Scrum or not to Scrum, that is the question",
        "10x developers commit commit commit and pushhhhhhhhh"
        "More lines of code, more commits => 10x devs contribute to KPIs!",
        "More lines of code, more commits => Happy managers!",
        "This is a 10x commit",
        "This is a 10x commit, trust me",
        "This is a 10x commit, believe me",
        "This is a 10x commit, period",
        "This is another 10x commit",
        "We need more 10x commits",
        "10x more commits, 10x more productivity",
        "The more commits you have, the better developer you are!",
        "10x developers love complexity",
        "Another amazing 10x commit",
        "Contributing to 10xness",
        "One more amazing 10x commit",
        "Another 10x commit, another step to greatness",
        "Super 10x commit",
        "Wow, what a 10x commit",
        "OMG, this is a 10x commit",
        "Oh, another 10x commit",
        "Beautiful taste of 10xness",
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

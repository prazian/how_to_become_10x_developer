import os
import random
import subprocess
from datetime import datetime, timedelta

def run_git_command(command):
    """Run a git command in the shell."""
    subprocess.run(command, shell=True, check=True)

def generate_commits(start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        years_since_start = (current_date - start_date).days / 365
        
        if years_since_start < 4:
            max_commits = 5  # Very few commits in the first 4 years
        elif years_since_start < 8:
            max_commits = 15  # Moderate commits in the middle years
        else:
            max_commits = 40  # More commits in the last 4 years

        num_commits = random.randint(0, max_commits)  # Random commits per day
        
        for _ in range(num_commits):
            commit_hour = random.randint(0, 23)
            commit_minute = random.randint(0, 59)
            commit_second = random.randint(0, 59)
            commit_time = datetime(current_date.year, current_date.month, current_date.day, commit_hour, commit_minute, commit_second)
            commit_time_str = commit_time.strftime("%Y-%m-%d %H:%M:%S")
            
            with open("assets/fake_file.txt", "a") as f:
                f.write(f"Commit on {commit_time_str}\n")
            run_git_command("git add fake_file.txt")
            run_git_command(f'GIT_COMMITTER_DATE="{commit_time_str}" git commit -m "Fake commit on {commit_time_str}" --date="{commit_time_str}"')
        
        current_date += timedelta(days=1)

if __name__ == "__main__":
    arg_start_date = datetime(2013, 1, 1)
    arg_end_date = datetime(2025, 3, 21)
    
    # Initialize git repo if not already initialized
    if not os.path.exists(".git"):
        run_git_command("git init")
    
    generate_commits(arg_start_date, arg_end_date)


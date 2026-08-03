#!/usr/bin/env python3
"""Generate fake commits for this repo, for comedic effect.

Two modes are supported:
  - daily:    generate commits for a single day (used by the daily GitHub Action)
  - backfill: generate commits across a date range (used to backfill history)
"""
import argparse
import os
import random
import subprocess
from datetime import datetime, timedelta

FAKE_FILE = "assets/fake_file.txt"

DEFAULT_MIN_COMMITS = 5
DEFAULT_MAX_COMMITS = 45

# Backfill mode ramps the daily ceiling up over time, as a fraction of --max-commits,
# so early history looks sparse and recent history looks (10x) active.
BACKFILL_TIER_YEARS = (4, 8)
BACKFILL_TIER_RATIOS = (5 / 40, 15 / 40, 1.0)

COMMIT_MESSAGES = [
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
    "Still think standups are for status report?",
    "More meetings = less work",
    "Micromanagement in Agile clothing",
    "Estimate-based management lol",
    "Process should serve the team, not the other way round",
    "Fix your broken mindset then process will be fixed",
    "Commit count = productivity? lol",
    "Measuring by the number of PRs and lines of code? lol",
    "Impact beats activity",
    "Still faking quantity? focuse on quality",
    "Fire your Scrum Masters",
    "Burn the burndown chart",
    "Delete the backlog trust your team",
    "Pplanning planning planning? Start shipping",
    "Fire managers to be more productive",
    "Micromanager = zero value",
    "Standup? ship the code!",
    "No more sprints -> focuse on adding real value",
    "Idiot micromanagers can't lead developers",
    "Bad managers = poision",
    "Devs aren't things",
    "Still measuring people like machines?",
    "10x developers commit commit commit and pushhhhhhhhh",
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
    "Another 10x shit",
    "10x commit, 0x brain",
    "Yet another 10x masterpiece",
    "Commit hard, think never",
    "10x commit, 10x nonsense",
    "Quantity over quality, baby",
    "Look ma, another commit",
    "10x commit go brrrr",
    "This one's for the KPIs",
    "10x developer, 10x noise",
]


def run_git_command(args, env=None):
    """Run a git command."""
    subprocess.run(["git", *args], check=True, env=env)


def commit_count_for_day(day, min_commits, max_commits, start_date=None):
    """Return how many fake commits to generate for a given day.

    In backfill mode (start_date given) the ceiling ramps up the further `day`
    is from `start_date`. In daily mode it's a flat random range.
    """
    if start_date is None:
        return random.randint(min_commits, max_commits)

    years_since_start = (day - start_date).days / 365
    if years_since_start < BACKFILL_TIER_YEARS[0]:
        ratio = BACKFILL_TIER_RATIOS[0]
    elif years_since_start < BACKFILL_TIER_YEARS[1]:
        ratio = BACKFILL_TIER_RATIOS[1]
    else:
        ratio = BACKFILL_TIER_RATIOS[2]

    day_max = max(1, round(max_commits * ratio))
    return random.randint(0, day_max)


def random_commit_datetime(day):
    return day.replace(
        hour=random.randint(0, 23),
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
    )


def make_fake_commit(commit_time):
    commit_time_str = commit_time.strftime("%Y-%m-%d %H:%M:%S")
    message = random.choice(COMMIT_MESSAGES)

    with open(FAKE_FILE, "a") as f:
        f.write(f"Commit on {commit_time_str}\n")

    run_git_command(["add", FAKE_FILE])
    env = {**os.environ, "GIT_COMMITTER_DATE": commit_time_str}
    run_git_command(["commit", "-m", message, "--date", commit_time_str], env=env)


def generate_commits_for_day(day, min_commits, max_commits, start_date=None):
    num_commits = commit_count_for_day(day, min_commits, max_commits, start_date)
    for _ in range(num_commits):
        make_fake_commit(random_commit_datetime(day))
    return num_commits


def generate_commits(start_date, end_date, min_commits, max_commits):
    current_date = start_date
    while current_date <= end_date:
        generate_commits_for_day(current_date, min_commits, max_commits, start_date=start_date)
        current_date += timedelta(days=1)


def _parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Generate fake commits.")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    daily = subparsers.add_parser("daily", help="Generate commits for a single day.")
    daily.add_argument("--date", required=True, type=_parse_date, help="Date in YYYY-MM-DD format.")
    daily.add_argument("--min-commits", type=int, default=DEFAULT_MIN_COMMITS)
    daily.add_argument("--max-commits", type=int, default=DEFAULT_MAX_COMMITS)

    backfill = subparsers.add_parser("backfill", help="Generate commits across a date range.")
    backfill.add_argument("--start-date", required=True, type=_parse_date)
    backfill.add_argument("--end-date", required=True, type=_parse_date)
    backfill.add_argument("--max-commits", type=int, default=DEFAULT_MAX_COMMITS)

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if args.mode == "daily":
        if args.min_commits > args.max_commits:
            raise ValueError("--min-commits cannot be greater than --max-commits")
        generate_commits_for_day(args.date, args.min_commits, args.max_commits)
    elif args.mode == "backfill":
        if not os.path.exists(".git"):
            run_git_command(["init"])
        generate_commits(args.start_date, args.end_date, 0, args.max_commits)


if __name__ == "__main__":
    main()

from datetime import datetime

import pytest

import generate_commits as gc


# ---------------------------------------------------------------------------
# run_git_command
# ---------------------------------------------------------------------------

def test_run_git_command_invokes_git_with_args(monkeypatch):
    calls = []
    monkeypatch.setattr(gc.subprocess, "run", lambda argv, check, env: calls.append((argv, check, env)))

    gc.run_git_command(["add", "foo.txt"], env={"FOO": "bar"})

    assert calls == [(["git", "add", "foo.txt"], True, {"FOO": "bar"})]


# ---------------------------------------------------------------------------
# commit_count_for_day
# ---------------------------------------------------------------------------

def test_commit_count_for_day_daily_mode_stays_within_bounds(monkeypatch):
    day = datetime(2026, 1, 1)
    for _ in range(200):
        count = gc.commit_count_for_day(day, min_commits=5, max_commits=45)
        assert 5 <= count <= 45


def test_commit_count_for_day_daily_mode_equal_bounds_is_exact():
    day = datetime(2026, 1, 1)
    assert gc.commit_count_for_day(day, min_commits=10, max_commits=10) == 10


@pytest.mark.parametrize(
    "days_since_start, expected_ratio",
    [
        (0, gc.BACKFILL_TIER_RATIOS[0]),
        (365 * 3, gc.BACKFILL_TIER_RATIOS[0]),
        (365 * 4, gc.BACKFILL_TIER_RATIOS[1]),
        (365 * 7, gc.BACKFILL_TIER_RATIOS[1]),
        (365 * 8, gc.BACKFILL_TIER_RATIOS[2]),
        (365 * 12, gc.BACKFILL_TIER_RATIOS[2]),
    ],
)
def test_commit_count_for_day_backfill_mode_uses_correct_tier(monkeypatch, days_since_start, expected_ratio):
    start_date = datetime(2013, 1, 1)
    day = start_date + gc.timedelta(days=days_since_start)
    max_commits = 40

    captured = {}

    def fake_randint(low, high):
        captured["low"], captured["high"] = low, high
        return high

    monkeypatch.setattr(gc.random, "randint", fake_randint)

    gc.commit_count_for_day(day, min_commits=0, max_commits=max_commits, start_date=start_date)

    assert captured["low"] == 0
    assert captured["high"] == max(1, round(max_commits * expected_ratio))


def test_commit_count_for_day_backfill_mode_day_max_never_zero():
    start_date = datetime(2013, 1, 1)
    day = start_date  # first tier, tiny max_commits would round down to 0 without the floor
    for _ in range(50):
        count = gc.commit_count_for_day(day, min_commits=0, max_commits=1, start_date=start_date)
        assert count >= 0  # randint(0, 1) always valid, i.e. day_max computed without error


# ---------------------------------------------------------------------------
# random_commit_datetime
# ---------------------------------------------------------------------------

def test_random_commit_datetime_keeps_the_same_date():
    day = datetime(2026, 5, 17)
    for _ in range(50):
        commit_time = gc.random_commit_datetime(day)
        assert (commit_time.year, commit_time.month, commit_time.day) == (2026, 5, 17)
        assert 0 <= commit_time.hour <= 23
        assert 0 <= commit_time.minute <= 59
        assert 0 <= commit_time.second <= 59


# ---------------------------------------------------------------------------
# make_fake_commit
# ---------------------------------------------------------------------------

def test_make_fake_commit_writes_file_and_runs_git_commands(tmp_path, monkeypatch):
    fake_file = tmp_path / "fake_file.txt"
    monkeypatch.setattr(gc, "FAKE_FILE", str(fake_file))

    git_calls = []
    monkeypatch.setattr(gc, "run_git_command", lambda args, env=None: git_calls.append((args, env)))

    commit_time = datetime(2026, 3, 4, 10, 20, 30)
    gc.make_fake_commit(commit_time)

    assert fake_file.read_text() == "Commit on 2026-03-04 10:20:30\n"

    assert git_calls[0] == (["add", str(fake_file)], None)

    commit_args, env = git_calls[1]
    assert commit_args[0] == "commit"
    assert commit_args[1] == "-m"
    assert commit_args[2] in gc.COMMIT_MESSAGES
    assert commit_args[3:] == ["--date", "2026-03-04 10:20:30"]
    assert env["GIT_COMMITTER_DATE"] == "2026-03-04 10:20:30"


# ---------------------------------------------------------------------------
# generate_commits_for_day / generate_commits
# ---------------------------------------------------------------------------

def test_generate_commits_for_day_makes_expected_number_of_commits(monkeypatch):
    monkeypatch.setattr(gc, "commit_count_for_day", lambda *a, **k: 3)
    made = []
    monkeypatch.setattr(gc, "make_fake_commit", lambda commit_time: made.append(commit_time))

    result = gc.generate_commits_for_day(datetime(2026, 1, 1), min_commits=1, max_commits=5)

    assert result == 3
    assert len(made) == 3


def test_generate_commits_for_day_zero_commits_makes_no_commits(monkeypatch):
    monkeypatch.setattr(gc, "commit_count_for_day", lambda *a, **k: 0)
    made = []
    monkeypatch.setattr(gc, "make_fake_commit", lambda commit_time: made.append(commit_time))

    result = gc.generate_commits_for_day(datetime(2026, 1, 1), min_commits=0, max_commits=5)

    assert result == 0
    assert made == []


def test_generate_commits_covers_every_day_in_range_inclusive(monkeypatch):
    seen_days = []
    monkeypatch.setattr(
        gc,
        "generate_commits_for_day",
        lambda day, min_commits, max_commits, start_date=None: seen_days.append(day),
    )

    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 4)
    gc.generate_commits(start_date, end_date, min_commits=0, max_commits=10)

    assert seen_days == [
        datetime(2026, 1, 1),
        datetime(2026, 1, 2),
        datetime(2026, 1, 3),
        datetime(2026, 1, 4),
    ]


# ---------------------------------------------------------------------------
# parse_args
# ---------------------------------------------------------------------------

def test_parse_args_daily_defaults():
    args = gc.parse_args(["daily", "--date", "2026-01-01"])
    assert args.mode == "daily"
    assert args.date == datetime(2026, 1, 1)
    assert args.min_commits == gc.DEFAULT_MIN_COMMITS
    assert args.max_commits == gc.DEFAULT_MAX_COMMITS


def test_parse_args_daily_custom_bounds():
    args = gc.parse_args(["daily", "--date", "2026-01-01", "--min-commits", "2", "--max-commits", "8"])
    assert args.min_commits == 2
    assert args.max_commits == 8


def test_parse_args_backfill_requires_start_and_end_date():
    args = gc.parse_args(["backfill", "--start-date", "2013-01-01", "--end-date", "2013-01-31"])
    assert args.mode == "backfill"
    assert args.start_date == datetime(2013, 1, 1)
    assert args.end_date == datetime(2013, 1, 31)
    assert args.max_commits == gc.DEFAULT_MAX_COMMITS


def test_parse_args_daily_requires_date():
    with pytest.raises(SystemExit):
        gc.parse_args(["daily"])


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def test_main_daily_delegates_to_generate_commits_for_day(monkeypatch):
    calls = []
    monkeypatch.setattr(
        gc,
        "generate_commits_for_day",
        lambda day, min_commits, max_commits: calls.append((day, min_commits, max_commits)),
    )

    gc.main(["daily", "--date", "2026-02-02", "--min-commits", "3", "--max-commits", "9"])

    assert calls == [(datetime(2026, 2, 2), 3, 9)]


def test_main_daily_rejects_min_greater_than_max(monkeypatch):
    monkeypatch.setattr(
        gc,
        "generate_commits_for_day",
        lambda *a, **k: pytest.fail("should not generate commits when bounds are invalid"),
    )

    with pytest.raises(ValueError):
        gc.main(["daily", "--date", "2026-02-02", "--min-commits", "9", "--max-commits", "3"])


def test_main_backfill_initializes_git_when_missing(monkeypatch):
    monkeypatch.setattr(gc.os.path, "exists", lambda path: False)
    git_calls = []
    monkeypatch.setattr(gc, "run_git_command", lambda args: git_calls.append(args))
    monkeypatch.setattr(gc, "generate_commits", lambda *a, **k: None)

    gc.main(["backfill", "--start-date", "2013-01-01", "--end-date", "2013-01-02"])

    assert ["init"] in git_calls


def test_main_backfill_skips_init_when_git_already_exists(monkeypatch):
    monkeypatch.setattr(gc.os.path, "exists", lambda path: True)
    git_calls = []
    monkeypatch.setattr(gc, "run_git_command", lambda args: git_calls.append(args))
    monkeypatch.setattr(gc, "generate_commits", lambda *a, **k: None)

    gc.main(["backfill", "--start-date", "2013-01-01", "--end-date", "2013-01-02"])

    assert git_calls == []

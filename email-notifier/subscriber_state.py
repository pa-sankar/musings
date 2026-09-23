"""
subscriber_state.py — shared helpers for the Musings subscriber state DB
==========================================================================
The Google Form export (`Musings Blog Subscribers.csv`, gitignored,
re-downloaded and overwritten wholesale by Sankar on each new signup) is
a raw snapshot, not a tracked list — it has no record of who's already
been welcomed, who asked not to be emailed, or what article was live
when someone signed up.

This module maintains an enriched, append-only state file alongside it:
`email-notifier/subscriber_state.csv` (also gitignored — it's subscriber
PII). One row per subscriber, keyed by email (case-insensitive):

    Email, Name, SubscribedTimestamp, SignupContextTitle, SignupContextUrl,
    WelcomeSentDate, Status, Notes

  - Status is one of: active, do-not-send, bounced
  - SignupContextTitle/Url record whichever article was the latest
    published piece at signup time (best-effort — whatever was passed to
    sync_subscribers.py at the time), so it's later obvious what likely
    drove the subscription.
  - WelcomeSentDate is set automatically by welcome.py once sent.

Use `sync_subscribers.py` to pull in new rows from the raw export, and
`manage_subscriber.py` to change a subscriber's status (e.g. do-not-send
on request). notify.py and welcome.py both read only from this state
file, filtered to Status == active.
"""

import csv
from pathlib import Path

FIELDS = [
    "Email", "Name", "SubscribedTimestamp",
    "SignupContextTitle", "SignupContextUrl",
    "WelcomeSentDate", "Status", "Notes",
]


def load_state(path: Path):
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_state(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in FIELDS})


def find_row(rows, email=None, name=None):
    for row in rows:
        if email and row["Email"].strip().lower() == email.strip().lower():
            return row
        if name and row["Name"].strip().lower() == name.strip().lower():
            return row
    return None


def active_subscribers(rows):
    return [r for r in rows if r.get("Status", "active").strip().lower() == "active"]

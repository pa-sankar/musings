#!/usr/bin/env python3
"""
sync_subscribers.py — pull new signups from the raw form export into the
tracked subscriber state DB
=============================================================================
Run this each time Sankar re-downloads and overwrites
`Musings Blog Subscribers.csv` with a fresh export from the Google Form.
It diffs that raw export against `email-notifier/subscriber_state.csv`
(by email, case-insensitive) and appends any rows it hasn't seen before,
tagged Status=active and an empty WelcomeSentDate.

Usage
-----
  # Just report what's new, don't write anything:
  python sync_subscribers.py --dry-run

  # Sync, and tag new signups with the article that was likely live
  # when they subscribed (shows in their SignupContextTitle/Url):
  python sync_subscribers.py \\
      --current-article-title "Show your work, prove you meant it" \\
      --current-article-url "https://pa-sankar.github.io/musings/show-your-work-prove-you-meant-it/"

After syncing, check the output for subscribers with no WelcomeSentDate
and send them a welcome via welcome.py.
"""

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

from subscriber_state import load_state, save_state, FIELDS

CONFIG_PATH = Path(__file__).parent / "config.json"
REPO_ROOT   = Path(__file__).parent.parent


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_raw_export(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    parser = argparse.ArgumentParser(description="Sync new subscribers from the raw form export into the tracked state DB.")
    parser.add_argument("--current-article-title", default="", help="Article likely live at signup time, for context")
    parser.add_argument("--current-article-url",   default="", help="URL of that article")
    parser.add_argument("--dry-run", action="store_true", help="Report new subscribers without writing state")
    args = parser.parse_args()

    cfg = load_config()
    raw_path   = REPO_ROOT / cfg["subscribers_csv"]
    state_path = REPO_ROOT / cfg["subscriber_state_csv"]

    if not raw_path.exists():
        print(f"ERROR: raw export not found at {raw_path}")
        sys.exit(1)

    raw_rows   = load_raw_export(raw_path)
    state_rows = load_state(state_path)
    known_emails = {r["Email"].strip().lower() for r in state_rows}

    new_rows = []
    for row in raw_rows:
        name  = row.get("Name", "").strip()
        email = row.get("Email", "").strip()
        if not email or email.lower() in known_emails:
            continue
        new_rows.append({
            "Email": email,
            "Name": name,
            "SubscribedTimestamp": row.get("Timestamp", "").strip(),
            "SignupContextTitle": args.current_article_title,
            "SignupContextUrl": args.current_article_url,
            "WelcomeSentDate": "",
            "Status": "active",
            "Notes": row.get("Remarks or comments, if any", "").strip(),
        })
        known_emails.add(email.lower())

    print(f"Raw export: {len(raw_rows)} rows. Tracked state: {len(state_rows)} known.")

    if not new_rows:
        print("No new subscribers.")
        return

    print(f"New subscribers found: {len(new_rows)}")
    for r in new_rows:
        print(f"  {r['Name']} <{r['Email']}>" + (f" — {r['Notes']}" if r["Notes"] else ""))

    if args.dry_run:
        print("Dry run — state not written.")
        return

    save_state(state_path, state_rows + new_rows)
    print(f"\nSaved to {state_path}")
    print("Run welcome.py for each new subscriber above (WelcomeSentDate is empty for all of them).")


if __name__ == "__main__":
    main()

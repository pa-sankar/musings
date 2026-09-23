#!/usr/bin/env python3
"""
manage_subscriber.py — change a tracked subscriber's status
================================================================
Use this to mark a subscriber do-not-send (they asked to stop, or the
address bounced), or to reactivate one. notify.py and welcome.py both
skip anyone whose Status isn't "active".

Usage
-----
  python manage_subscriber.py --email jagan.xbox@gmail.com --status do-not-send --note "Asked to unsubscribe 2026-09-24"
  python manage_subscriber.py --email jagan.xbox@gmail.com --status active
  python manage_subscriber.py --list                     # show everyone and their status
"""

import argparse
import json
import sys
from pathlib import Path

from subscriber_state import load_state, save_state

CONFIG_PATH = Path(__file__).parent / "config.json"
REPO_ROOT   = Path(__file__).parent.parent
VALID_STATUSES = {"active", "do-not-send", "bounced"}


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Change a tracked subscriber's status.")
    parser.add_argument("--email", default=None, help="Subscriber email")
    parser.add_argument("--status", choices=sorted(VALID_STATUSES), default=None)
    parser.add_argument("--note", default=None, help="Optional note to append (e.g. why)")
    parser.add_argument("--list", action="store_true", help="List all tracked subscribers and their status")
    args = parser.parse_args()

    cfg = load_config()
    state_path = REPO_ROOT / cfg["subscriber_state_csv"]
    rows = load_state(state_path)

    if args.list:
        if not rows:
            print("No subscribers tracked yet — run sync_subscribers.py first.")
            return
        for r in rows:
            welcomed = r["WelcomeSentDate"] or "not yet"
            print(f"  [{r['Status']:11}] {r['Name']:20} <{r['Email']}>  welcomed: {welcomed}")
        return

    if not args.email or not args.status:
        print("ERROR: pass --email and --status (or --list).")
        sys.exit(1)

    match = None
    for r in rows:
        if r["Email"].strip().lower() == args.email.strip().lower():
            match = r
            break

    if not match:
        print(f"ERROR: no tracked subscriber with email {args.email!r}. Run sync_subscribers.py first if they're new.")
        sys.exit(1)

    old_status = match["Status"]
    match["Status"] = args.status
    if args.note:
        match["Notes"] = f"{match['Notes']} | {args.note}".strip(" |")

    save_state(state_path, rows)
    print(f"{match['Name']} <{match['Email']}>: {old_status} -> {args.status}")
    if args.note:
        print(f"Note: {match['Notes']}")


if __name__ == "__main__":
    main()

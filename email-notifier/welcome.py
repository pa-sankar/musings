#!/usr/bin/env python3
"""
welcome.py — Musings new-subscriber welcome email
====================================================
Sends a one-off welcome email to a single new subscriber, looked up by
name or email in the tracked subscriber state DB (see
subscriber_state.py). Links to the homepage, not the latest article —
if they just subscribed, they most likely already read whatever piece
brought them here; the welcome email's job is pointing them at
everything else they haven't seen yet.

Run sync_subscribers.py first if the subscriber isn't tracked yet.
On success, this records today's date in the subscriber's
WelcomeSentDate so re-runs don't double-send by accident (it still
will if asked — no hard block — but warns).

Usage
-----
  python welcome.py --name Jagan --dry-run
  python welcome.py --email jagan.xbox@gmail.com
"""

import json
import smtplib
import argparse
import sys
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from subscriber_state import load_state, save_state, find_row

CONFIG_PATH = Path(__file__).parent / "config.json"
REPO_ROOT   = Path(__file__).parent.parent


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def build_message(cfg, recipient):
    sender_email = cfg["sender_email"]
    sender_name  = cfg["sender_name"]
    blog_name    = cfg["blog_name"]
    blog_url     = cfg["blog_url"]
    greeting_name = recipient["Name"] if recipient["Name"] else "there"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Welcome to {blog_name}"
    msg["From"]    = f"{sender_name} <{sender_email}>"
    msg["To"]      = recipient["Email"]

    plain = f"""Hi {greeting_name},

Thanks for subscribing to {blog_name} — writing on organic farming, independent
living, AI, education, and history, by Paa Sankar.

You'll get an email whenever a new piece goes up. No spam, just new articles.

Since you're here, take a look at everything else on the site: {blog_url}

---
To unsubscribe, reply to this email.

— {sender_name}
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#faf8f4;font-family:Georgia,'Times New Roman',serif;color:#2d2a26;">
  <div style="max-width:560px;margin:2.5rem auto;padding:0 1.5rem;">

    <p style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.14em;color:#8b6f47;margin:0 0 2.5rem 0;">
      {blog_name}
    </p>

    <p style="font-size:1rem;color:#4a4540;margin:0 0 1.5rem 0;line-height:1.7;">
      Hi {greeting_name},
    </p>

    <p style="font-size:1rem;color:#4a4540;margin:0 0 1.5rem 0;line-height:1.7;">
      Thanks for subscribing. {blog_name} is Paa Sankar's writing on organic
      farming, independent living, AI, education, and history — not separate
      interests, but the same inquiry approached from different angles.
    </p>

    <p style="font-size:1rem;color:#4a4540;margin:0 0 2.5rem 0;line-height:1.7;">
      You'll get an email whenever a new piece goes up. No spam, just new articles.
      Since you're here, take a look at everything else on the site.
    </p>

    <p style="margin:0 0 2.5rem 0;">
      <a href="{blog_url}"
         style="display:inline-block;padding:0.6rem 1.4rem;background-color:#5b6e3a;color:#ffffff;
                text-decoration:none;font-size:0.9rem;border-radius:2px;font-family:Georgia,serif;">
        Browse the site
      </a>
    </p>

    <hr style="border:none;border-top:1px solid #e5e0da;margin:2rem 0;">

    <p style="font-size:0.78rem;color:#9b9490;margin:0;line-height:1.65;">
      To unsubscribe, reply to this email.
    </p>

  </div>
</body>
</html>"""

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))
    return msg


def main():
    parser = argparse.ArgumentParser(description="Send a welcome email to one tracked Musings subscriber.")
    parser.add_argument("--name",  default=None, help="Subscriber name, as tracked")
    parser.add_argument("--email", default=None, help="Subscriber email, as tracked")
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")
    args = parser.parse_args()

    if not args.name and not args.email:
        print("ERROR: pass --name or --email to identify the subscriber.")
        sys.exit(1)

    cfg = load_config()
    state_path = REPO_ROOT / cfg["subscriber_state_csv"]
    rows = load_state(state_path)

    if not rows:
        print(f"ERROR: no tracked subscribers at {state_path}. Run sync_subscribers.py first.")
        sys.exit(1)

    recipient = find_row(rows, email=args.email, name=args.name)
    if not recipient:
        print(f"ERROR: no tracked subscriber matching name={args.name!r} email={args.email!r}. Run sync_subscribers.py if they're new.")
        sys.exit(1)

    if not recipient["Email"]:
        print(f"ERROR: subscriber {recipient['Name']!r} has no email address tracked.")
        sys.exit(1)

    if recipient["Status"] != "active":
        print(f"ERROR: {recipient['Name']} <{recipient['Email']}> is marked '{recipient['Status']}', not active. Not sending.")
        sys.exit(1)

    if recipient["WelcomeSentDate"]:
        print(f"NOTE: welcome already sent to {recipient['Email']} on {recipient['WelcomeSentDate']}. Re-sending anyway.")

    print(f"Recipient: {recipient['Name']} <{recipient['Email']}>")

    if args.dry_run:
        print("Dry run — no email sent.")
        return

    msg = build_message(cfg, recipient)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(cfg["sender_email"], cfg["app_password"])
        server.sendmail(cfg["sender_email"], recipient["Email"], msg.as_string())

    recipient["WelcomeSentDate"] = date.today().isoformat()
    save_state(state_path, rows)

    print(f"Sent -> {recipient['Name']} <{recipient['Email']}> (WelcomeSentDate recorded)")


if __name__ == "__main__":
    main()

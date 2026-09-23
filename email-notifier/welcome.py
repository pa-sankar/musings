#!/usr/bin/env python3
"""
welcome.py — Musings new-subscriber welcome email
====================================================
Sends a one-off welcome email to a single new subscriber, looked up by
name or email in the subscriber CSV.

Credentials and settings are read from config.json in this folder,
same as notify.py. The subscriber CSV is expected one level up.

Usage
-----
  # Preview without sending:
  python welcome.py --name Jagan --dry-run

  # Send:
  python welcome.py --name Jagan

  # Look up by email instead, and point them at the current series:
  python welcome.py --email jagan.xbox@gmail.com \\
      --highlight-title "AI is killing the curious cat" \\
      --highlight-url "https://pa-sankar.github.io/musings/ai-is-killing-the-curious-cat/" \\
      --highlight-subtitle "Part 1 of a 5-part series on AI, curiosity, and human nature"
"""

import csv
import json
import smtplib
import argparse
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"
REPO_ROOT   = Path(__file__).parent.parent


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def find_subscriber(csv_path, name=None, email=None):
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row_name  = row.get("Name", "").strip()
            row_email = row.get("Email", "").strip()
            if email and row_email.lower() == email.lower():
                return {"name": row_name, "email": row_email}
            if name and row_name.lower() == name.lower():
                return {"name": row_name, "email": row_email}
    return None


def build_message(cfg, recipient, highlight_title=None, highlight_url=None, highlight_subtitle=None):
    sender_email = cfg["sender_email"]
    sender_name  = cfg["sender_name"]
    blog_name    = cfg["blog_name"]
    blog_url     = cfg["blog_url"]
    greeting_name = recipient["name"] if recipient["name"] else "there"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Welcome to {blog_name}"
    msg["From"]    = f"{sender_name} <{sender_email}>"
    msg["To"]      = recipient["email"]

    highlight_plain = ""
    highlight_html = ""
    if highlight_title and highlight_url:
        subtitle_plain = f"{highlight_subtitle}\n" if highlight_subtitle else ""
        highlight_plain = f"\nA good place to start: {highlight_title}\n{subtitle_plain}{highlight_url}\n"

        subtitle_html = (
            f"<p style='font-size:1rem;font-style:italic;color:#6b6560;margin:0 0 1.25rem;line-height:1.5;'>{highlight_subtitle}</p>"
            if highlight_subtitle else ""
        )
        highlight_html = f"""
    <p style="font-size:0.9rem;color:#8b6f47;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 0.75rem;">A good place to start</p>
    <div style="border-left:3px solid #c09a6a;padding:0 0 0 1.25rem;margin:0 0 1.5rem 0;">
      <h2 style="font-size:1.2rem;font-weight:normal;line-height:1.3;color:#2d2a26;margin:0 0 0.5rem 0;">{highlight_title}</h2>
      {subtitle_html}
    </div>
    <p style="margin:0 0 2.5rem 0;">
      <a href="{highlight_url}"
         style="display:inline-block;padding:0.6rem 1.4rem;background-color:#5b6e3a;color:#ffffff;
                text-decoration:none;font-size:0.9rem;border-radius:2px;font-family:Georgia,serif;">
        Read it
      </a>
    </p>
"""

    plain = f"""Hi {greeting_name},

Thanks for subscribing to {blog_name} — writing on organic farming, independent
living, AI, education, and history, by Paa Sankar.

You'll get an email whenever a new piece goes up. No spam, just new articles.
{highlight_plain}
Browse everything here: {blog_url}

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
    </p>

    {highlight_html}

    <p style="margin:0 0 2.5rem 0;">
      <a href="{blog_url}" style="color:#5b6e3a;text-decoration:underline;font-size:0.95rem;">
        Browse everything on the site →
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
    parser = argparse.ArgumentParser(description="Send a welcome email to one new Musings subscriber.")
    parser.add_argument("--name",  default=None, help="Subscriber name, as it appears in the CSV")
    parser.add_argument("--email", default=None, help="Subscriber email, as it appears in the CSV")
    parser.add_argument("--highlight-title",    default=None, help="Optional article title to feature")
    parser.add_argument("--highlight-url",      default=None, help="Optional article URL to feature")
    parser.add_argument("--highlight-subtitle", default="",   help="Optional article subtitle")
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")
    args = parser.parse_args()

    if not args.name and not args.email:
        print("ERROR: pass --name or --email to identify the subscriber.")
        sys.exit(1)

    cfg = load_config()
    csv_path = REPO_ROOT / cfg["subscribers_csv"]

    if not csv_path.exists():
        print(f"ERROR: subscriber CSV not found at {csv_path}")
        sys.exit(1)

    recipient = find_subscriber(csv_path, name=args.name, email=args.email)
    if not recipient:
        print(f"ERROR: no subscriber matching name={args.name!r} email={args.email!r} found in {csv_path}")
        sys.exit(1)

    if not recipient["email"]:
        print(f"ERROR: subscriber {recipient['name']!r} has no email address in the CSV.")
        sys.exit(1)

    print(f"Recipient: {recipient['name']} <{recipient['email']}>")

    if args.dry_run:
        print("Dry run — no email sent.")
        return

    msg = build_message(cfg, recipient, args.highlight_title, args.highlight_url, args.highlight_subtitle)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(cfg["sender_email"], cfg["app_password"])
        server.sendmail(cfg["sender_email"], recipient["email"], msg.as_string())

    print(f"Sent -> {recipient['name']} <{recipient['email']}>")


if __name__ == "__main__":
    main()

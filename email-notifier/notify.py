#!/usr/bin/env python3
"""
notify.py — Musings new-article email notifier
================================================
Sends a notification email to all subscribers in the CSV when a new
article is published on Musings of an Indian.

Credentials and settings are read from config.json in this folder.
The subscriber CSV is expected one level up (repo root).

Usage
-----
  # Preview recipients without sending:
  python notify.py --dry-run --title "Article Title" --url "https://..."

  # Send (add --subtitle for the article subtitle):
  python notify.py --title "Before You Invest a Rupee, Learn the Language" \\
                   --url "https://pa-sankar.github.io/musings/investment-language/" \\
                   --subtitle "A naive investor's notes on tax, inflation, and XIRR"
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


def load_subscribers(csv_path):
    subscribers = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name  = row.get("Name", "").strip()
            email = row.get("Email", "").strip()
            if email:
                subscribers.append({"name": name, "email": email})
    return subscribers


def build_message(cfg, recipient, article_title, article_url, article_subtitle):
    sender_email = cfg["sender_email"]
    sender_name  = cfg["sender_name"]
    blog_name    = cfg["blog_name"]
    blog_url     = cfg["blog_url"]
    first_name   = recipient["name"].split()[0] if recipient["name"] else "Reader"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"New on {blog_name}: {article_title}"
    msg["From"]    = f"{sender_name} <{sender_email}>"
    msg["To"]      = recipient["email"]

    subtitle_line_plain = f"{article_subtitle}\n" if article_subtitle else ""
    subtitle_block_html = (
        f"<p style='font-size:1rem;font-style:italic;color:#6b6560;"
        f"margin:0 0 1.75rem;line-height:1.5;'>{article_subtitle}</p>"
        if article_subtitle else ""
    )

    plain = f"""Hi {first_name},

A new article has just been published on {blog_name}.

{article_title}
{subtitle_line_plain}
Read it here: {article_url}

---
You're receiving this because you subscribed at {blog_url}
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
      Hi {first_name},
    </p>

    <p style="font-size:1rem;color:#4a4540;margin:0 0 2rem 0;line-height:1.7;">
      A new article has just been published.
    </p>

    <div style="border-left:3px solid #c09a6a;padding:0 0 0 1.25rem;margin:0 0 2rem 0;">
      <h1 style="font-size:1.4rem;font-weight:normal;line-height:1.3;color:#2d2a26;margin:0 0 0.6rem 0;">
        {article_title}
      </h1>
      {subtitle_block_html}
    </div>

    <p style="margin:0 0 2.5rem 0;">
      <a href="{article_url}"
         style="display:inline-block;padding:0.6rem 1.4rem;background-color:#5b6e3a;color:#ffffff;
                text-decoration:none;font-size:0.9rem;border-radius:2px;font-family:Georgia,serif;">
        Read the article
      </a>
    </p>

    <hr style="border:none;border-top:1px solid #e5e0da;margin:2rem 0;">

    <p style="font-size:0.78rem;color:#9b9490;margin:0;line-height:1.65;">
      You're receiving this because you subscribed at
      <a href="{blog_url}" style="color:#5b6e3a;text-decoration:underline;">{blog_url}</a>.
      To unsubscribe, reply to this email.
    </p>

  </div>
</body>
</html>"""

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))
    return msg


def main():
    parser = argparse.ArgumentParser(description="Send new-article notification to Musings subscribers.")
    parser.add_argument("--title",    required=True,  help="Article title")
    parser.add_argument("--url",      required=True,  help="Full article URL")
    parser.add_argument("--subtitle", default="",     help="Article subtitle (optional)")
    parser.add_argument("--dry-run",  action="store_true", help="List recipients without sending")
    args = parser.parse_args()

    cfg = load_config()
    csv_path = REPO_ROOT / cfg["subscribers_csv"]

    if not csv_path.exists():
        print(f"ERROR: subscriber CSV not found at {csv_path}")
        sys.exit(1)

    subscribers = load_subscribers(csv_path)
    if not subscribers:
        print("No subscribers found in CSV.")
        sys.exit(1)

    print(f"Subscribers: {len(subscribers)}")

    if args.dry_run:
        print("Dry run — recipients that would be emailed:")
        for s in subscribers:
            print(f"  {s['name']} <{s['email']}>")
        print("No emails sent.")
        return

    sent = failed = 0
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(cfg["sender_email"], cfg["app_password"])
        for sub in subscribers:
            try:
                msg = build_message(cfg, sub, args.title, args.url, args.subtitle)
                server.sendmail(cfg["sender_email"], sub["email"], msg.as_string())
                print(f"  Sent  → {sub['name']} <{sub['email']}>")
                sent += 1
            except Exception as e:
                print(f"  FAIL  → {sub['email']}: {e}")
                failed += 1

    print(f"\nDone. {sent} sent, {failed} failed.")


if __name__ == "__main__":
    main()

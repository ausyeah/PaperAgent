"""
Monitor script for the 8 active Jules sessions.
"""

import os
import json
import requests
from datetime import datetime

JULES_API_KEY = os.environ.get("JULES_API_KEY")
HEADERS = {"x-goog-api-key": JULES_API_KEY}

def monitor():
    if not os.path.exists(".jules/active_sessions.json"):
        print("No active sessions file found.")
        return

    with open(".jules/active_sessions.json", "r", encoding="utf-8") as f:
        tasks = json.load(f)

    print(f"\n{'='*75}")
    print(f"JULES MULTI-SESSION STATUS MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*75}\n")

    summary = []
    for t in tasks:
        sess_id = t.get("session")
        if not sess_id:
            continue
        # Extract numeric id if full name
        raw_id = sess_id.split("/")[-1]
        url = f"https://jules.googleapis.com/v1alpha/sessions/{raw_id}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                data = r.json()
                state = data.get("state", "UNKNOWN")
                outputs = data.get("outputs", {})
                pr = outputs.get("pullRequest", {})
                pr_url = pr.get("url") or pr.get("htmlUrl") or "None"
                
                # Check activities
                act_r = requests.get(f"{url}/activities?pageSize=5", headers=HEADERS, timeout=10)
                acts = act_r.json().get("activities", []) if act_r.status_code == 200 else []

                summary.append({
                    "id": raw_id,
                    "title": t["title"],
                    "state": state,
                    "activities_count": len(acts),
                    "pr": pr_url,
                    "url": data.get("url")
                })
                print(f"[{state}] {t['title']}")
                print(f"   Session ID: {raw_id}")
                print(f"   Jules URL : {data.get('url')}")
                if pr_url != "None":
                    print(f"   Pull Req  : {pr_url}")
                print(f"   Activities: {len(acts)} logged")
                print("-" * 65)
            else:
                print(f"[ERROR {r.status_code}] {t['title']} ({raw_id})")
        except Exception as e:
            print(f"[EXCEPTION] {t['title']}: {e}")

    # Count states
    states = {}
    for s in summary:
        states[s["state"]] = states.get(s["state"], 0) + 1
    print(f"\nSummary of {len(summary)} sessions: {states}\n")

if __name__ == "__main__":
    monitor()

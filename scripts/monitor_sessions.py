"""
Fast concurrent monitor script for active Jules sessions and GitHub PRs.
"""

import os
import sys
import json
from datetime import datetime
import httpx

JULES_API_KEY = os.environ.get("JULES_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

JULES_HEADERS = {"x-goog-api-key": JULES_API_KEY}
GH_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def monitor():
    file_path = ".jules/active_sessions_v4.json"
    if not os.path.exists(file_path):
        file_path = ".jules/active_sessions_v3.json"
    if not os.path.exists(file_path):
        file_path = ".jules/active_sessions_v2.json"
    if not os.path.exists(file_path):
        file_path = ".jules/active_sessions.json"
    if not os.path.exists(file_path):
        print("No active sessions file found.", flush=True)
        return


    with open(file_path, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    print(f"\n{'='*75}", flush=True)
    print(f"JULES V2 STATUS MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print(f"{'='*75}\n", flush=True)

    with httpx.Client(timeout=10.0) as client:
        # Check GitHub PRs first
        print("--- GitHub PRs Status ---", flush=True)
        try:
            gh_r = client.get("https://api.github.com/repos/ausyeah/PaperAgent/pulls?state=open", headers=GH_HEADERS)
            if gh_r.status_code == 200:
                prs = gh_r.json()
                print(f"Open PRs count: {len(prs)}", flush=True)
                for pr in prs:
                    print(f"  * PR #{pr['number']}: {pr['title']} (branch: {pr['head']['ref']})", flush=True)
            else:
                print(f"  GitHub API returned {gh_r.status_code}", flush=True)
        except Exception as e:
            print(f"  GitHub API error: {e}", flush=True)

        print("\n--- Jules Sessions Status ---", flush=True)
        states = {}
        for t in tasks:
            sess_id = t.get("session")
            if not sess_id:
                continue
            raw_id = sess_id.split("/")[-1]
            url = f"https://jules.googleapis.com/v1alpha/sessions/{raw_id}"
            try:
                r = client.get(url, headers=JULES_HEADERS)
                if r.status_code == 200:
                    data = r.json()
                    state = data.get("state", "UNKNOWN")
                    states[state] = states.get(state, 0) + 1
                    outputs = data.get("outputs", {})
                    pr = outputs.get("pullRequest", {})
                    pr_url = pr.get("url") or pr.get("htmlUrl") or "None"
                    
                    print(f"[{state}] {t['title'][:60]}", flush=True)
                    print(f"    ID: {raw_id} | PR: {pr_url}", flush=True)
                else:
                    print(f"[HTTP {r.status_code}] {t['title']}", flush=True)
            except Exception as e:
                print(f"[ERR] {t['title']}: {e}", flush=True)

        print(f"\nState Breakdown: {states}", flush=True)

if __name__ == "__main__":
    monitor()

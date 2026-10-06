import os
import json
import requests

JULES_API_KEY = os.environ.get("JULES_API_KEY")
HEADERS = {"x-goog-api-key": JULES_API_KEY}

with open(".jules/active_sessions.json", "r", encoding="utf-8") as f:
    tasks = json.load(f)

for t in tasks:
    sess_id = t["session"].split("/")[-1]
    url = f"https://jules.googleapis.com/v1alpha/sessions/{sess_id}/activities"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        acts = r.json().get("activities", [])
        print(f"\n=== Session: {t['title']} ({sess_id}) ===")
        print(f"Total activities: {len(acts)}")
        if acts:
            latest = acts[0]
            print(f"Latest activity time: {latest.get('createTime')}")
            for k in latest:
                if k not in ["name", "createTime", "id"]:
                    print(f"  {k}: {str(latest[k])[:200]}")

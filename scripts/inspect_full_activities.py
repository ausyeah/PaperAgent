import os
import requests
import json

key = os.environ.get("JULES_API_KEY")
headers = {"x-goog-api-key": key}

def inspect_session(sess_id):
    url = f"https://jules.googleapis.com/v1alpha/sessions/{sess_id}/activities"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"Error {r.status_code}")
        return
    acts = r.json().get("activities", [])
    print(f"Session {sess_id}: {len(acts)} total activities")
    # Show last 3 activities
    for act in acts[-3:]:
        print(f"Time: {act.get('createTime')} | Originator: {act.get('originator')}")
        for k, v in act.items():
            if k not in ["name", "createTime", "originator", "id"]:
                print(f"  [{k}]: {str(v)[:250]}")

if __name__ == "__main__":
    with open(".jules/active_sessions.json", "r", encoding="utf-8") as f:
        tasks = json.load(f)
    for t in tasks:
        raw_id = t["session"].split("/")[-1]
        print(f"\n--- {t['title']} ({raw_id}) ---")
        inspect_session(raw_id)

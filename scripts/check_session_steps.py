import os
import json
import httpx

JULES_API_KEY = os.environ.get("JULES_API_KEY")
HEADERS = {"x-goog-api-key": JULES_API_KEY}

file_path = ".jules/active_sessions_v5.json" if os.path.exists(".jules/active_sessions_v5.json") else (".jules/active_sessions_v4.json" if os.path.exists(".jules/active_sessions_v4.json") else (".jules/active_sessions_v3.json" if os.path.exists(".jules/active_sessions_v3.json") else (".jules/active_sessions_v2.json" if os.path.exists(".jules/active_sessions_v2.json") else ".jules/active_sessions.json")))
with open(file_path, "r", encoding="utf-8") as f:
    tasks = json.load(f)

with httpx.Client(timeout=10.0) as client:
    for t in tasks:
        sid = t["session"].split("/")[-1]
        tid = t.get("task_id", "task")
        try:
            r = client.get(f"https://jules.googleapis.com/v1alpha/sessions/{sid}/activities?pageSize=5", headers=HEADERS)
            if r.status_code == 200:
                acts = r.json().get("activities", [])
                latest_types = [[k for k in a if k not in ("name", "createTime", "id")] for a in acts[:2]]
                # Extract step description if available
                step_desc = ""
                for a in acts:
                    if "stepStarted" in a:
                        step_desc = a["stepStarted"].get("step", {}).get("description", "")
                        break
                    elif "stepFinished" in a:
                        step_desc = "Finished: " + a["stepFinished"].get("step", {}).get("description", "")
                        break
                    elif "planGenerated" in a:
                        steps = a["planGenerated"].get("plan", {}).get("steps", [])
                        step_desc = f"Plan with {len(steps)} steps generated"
                        break
                print(f"[{sid}] {tid}: {step_desc or latest_types}", flush=True)
            else:
                print(f"[{sid}] {tid}: HTTP {r.status_code}", flush=True)
        except Exception as e:
            print(f"[{sid}] {tid}: {e}", flush=True)


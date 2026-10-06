import os
import json
import httpx

JULES_API_KEY = os.environ.get("JULES_API_KEY")
HEADERS = {"x-goog-api-key": JULES_API_KEY}

with httpx.Client(timeout=10.0) as client:
    for sid, name in [("10318094134643192347", "task_8_library_api"), ("716846158707734357", "task_9_frontend_v2")]:
        r = client.get(f"https://jules.googleapis.com/v1alpha/sessions/{sid}/activities?pageSize=5", headers=HEADERS)
        if r.status_code == 200:
            acts = r.json().get("activities", [])
            print(f"\n=== {name} ({sid}) ===", flush=True)
            for a in acts[:3]:
                time_str = a.get("createTime", "")
                types = [k for k in a if k not in ("name", "createTime", "id")]
                msg = ""
                for t in types:
                    val = a[t]
                    if isinstance(val, dict):
                        desc = val.get("description") or val.get("message", {}).get("text") or val.get("command") or ""
                        if desc:
                            msg += f" | {desc[:80]}"
                print(f"  [{time_str}] {types}{msg}", flush=True)

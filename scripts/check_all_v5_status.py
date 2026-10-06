import os
import json
import httpx

JULES_API_KEY = os.environ.get("JULES_API_KEY")
HEADERS = {"x-goog-api-key": JULES_API_KEY}

with open(".jules/active_sessions_v5.json", "r", encoding="utf-8") as f:
    tasks = json.load(f)

print(f"{'Task ID':<28} | {'Status':<12} | {'Has Patch':<10} | {'Latest Step'}")
print("-" * 80)

with httpx.Client(timeout=15.0) as client:
    for t in tasks:
        sid = t["session_id"]
        tid = t["task_id"]
        
        # Check session status
        s_res = client.get(f"https://jules.googleapis.com/v1alpha/sessions/{sid}", headers=HEADERS)
        state = s_res.json().get("state", "UNKNOWN") if s_res.status_code == 200 else f"ERR_{s_res.status_code}"
        
        # Check activities
        a_res = client.get(f"https://jules.googleapis.com/v1alpha/sessions/{sid}/activities?pageSize=30", headers=HEADERS)
        acts = a_res.json().get("activities", []) if a_res.status_code == 200 else []
        
        has_patch = False
        latest_title = ""
        for a in acts:
            if "artifacts" in a:
                for art in a["artifacts"]:
                    if "changeSet" in art and "gitPatch" in art["changeSet"]:
                        has_patch = True
            if "progressUpdated" in a:
                latest_title = a["progressUpdated"].get("title", "")
            elif "planGenerated" in a and not latest_title:
                plan = a["planGenerated"].get("plan", {})
                latest_title = f"Plan ({len(plan.get('steps', []))} steps)"
                
        print(f"{tid:<28} | {state:<12} | {str(has_patch):<10} | {latest_title}")

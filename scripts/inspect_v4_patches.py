import os
import json
import httpx

JULES_API_KEY = os.environ.get("JULES_API_KEY")
HEADERS = {"x-goog-api-key": JULES_API_KEY}

with open(".jules/active_sessions_v4.json", "r", encoding="utf-8") as f:
    tasks = json.load(f)

with httpx.Client(timeout=15.0) as client:
    for t in tasks:
        sid = t["session_id"]
        tid = t["task_id"]
        
        a_res = client.get(f"https://jules.googleapis.com/v1alpha/sessions/{sid}/activities?pageSize=50", headers=HEADERS)
        acts = a_res.json().get("activities", []) if a_res.status_code == 200 else []
        
        patch_text = None
        for a in reversed(acts):
            if "artifacts" in a:
                for art in a["artifacts"]:
                    if "changeSet" in art and "gitPatch" in art["changeSet"]:
                        patch_text = art["changeSet"]["gitPatch"].get("unidiffPatch")
                        break
            if patch_text:
                break
                
        if patch_text:
            lines = patch_text.strip().split("\n")
            diff_lines = [l for l in lines if l.startswith("diff --git")]
            print(f"[{tid}] ({len(patch_text)} bytes) Diff files:")
            for dl in diff_lines:
                print(f"   {dl}")
        else:
            print(f"[{tid}] No patch yet.")

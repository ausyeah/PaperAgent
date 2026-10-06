import os
import json
import httpx

JULES_API_KEY = os.environ.get("JULES_API_KEY")
HEADERS = {"x-goog-api-key": JULES_API_KEY}

os.makedirs(".jules/patches_v6", exist_ok=True)

with open(".jules/active_sessions_v6.json", "r", encoding="utf-8") as f:
    tasks = json.load(f)

with httpx.Client(timeout=20.0) as client:
    for t in tasks:
        sid = t["session_id"]
        tid = t["task_id"]
        
        patch_text = None
        
        # 1. Try session outputs
        s_res = client.get(f"https://jules.googleapis.com/v1alpha/sessions/{sid}", headers=HEADERS)
        if s_res.status_code == 200:
            s_data = s_res.json()
            outputs = s_data.get("outputs", [])
            for out in outputs:
                if "changeSet" in out and "gitPatch" in out["changeSet"]:
                    patch_text = out["changeSet"]["gitPatch"].get("unidiffPatch")
                    if patch_text:
                        break
                        
        # 2. Try activities artifacts
        if not patch_text:
            a_res = client.get(f"https://jules.googleapis.com/v1alpha/sessions/{sid}/activities?pageSize=50", headers=HEADERS)
            if a_res.status_code == 200:
                acts = a_res.json().get("activities", [])
                for a in reversed(acts):
                    if "artifacts" in a:
                        for art in a["artifacts"]:
                            if "changeSet" in art and "gitPatch" in art["changeSet"]:
                                patch_text = art["changeSet"]["gitPatch"].get("unidiffPatch")
                                if patch_text:
                                    break
                    if patch_text:
                        break
                        
        if patch_text:
            patch_path = f".jules/patches_v6/{tid}.patch"
            with open(patch_path, "w", encoding="utf-8") as f:
                f.write(patch_text)
            print(f"[SAVED] {tid}: {len(patch_text)} bytes -> {patch_path}")
        else:
            print(f"[PENDING] {tid}: No patch yet.")

import os
import httpx

token = os.environ.get("GITHUB_TOKEN")
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json"
}

with httpx.Client(timeout=10.0) as client:
    r_prs = client.get("https://api.github.com/repos/ausyeah/PaperAgent/pulls?state=all", headers=headers)
    if r_prs.status_code == 200:
        prs = r_prs.json()
        print(f"Total Pull Requests on GitHub: {len(prs)}\n", flush=True)
        for pr in prs:
            print(f"PR #{pr['number']}: {pr['title']} [{pr['state'].upper()}]", flush=True)
            print(f"   Branch : {pr['head']['ref']} -> {pr['base']['ref']}", flush=True)
            print(f"   URL    : {pr['html_url']}", flush=True)
            print("-" * 60, flush=True)
    else:
        print("Error:", r_prs.status_code, r_prs.text, flush=True)

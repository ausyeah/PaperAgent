import os
import requests
import json

token = os.environ.get("GITHUB_TOKEN")
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json"
}

r_prs = requests.get("https://api.github.com/repos/ausyeah/PaperAgent/pulls?state=all", headers=headers)
if r_prs.status_code == 200:
    prs = r_prs.json()
    print(f"Total Pull Requests on GitHub: {len(prs)}\n")
    for pr in prs:
        print(f"PR #{pr['number']}: {pr['title']} [{pr['state'].upper()}]")
        print(f"   Author : {pr['user']['login']}")
        print(f"   Branch : {pr['head']['ref']} -> {pr['base']['ref']}")
        print(f"   URL    : {pr['html_url']}")
        print("-" * 60)
else:
    print("Error:", r_prs.status_code, r_prs.text)

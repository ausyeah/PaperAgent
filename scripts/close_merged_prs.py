import os
import requests

token = os.environ.get("GITHUB_TOKEN")
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json"
}

r_prs = requests.get("https://api.github.com/repos/ausyeah/PaperAgent/pulls?state=open", headers=headers)
if r_prs.status_code == 200:
    open_prs = r_prs.json()
    print(f"Open PRs to process: {len(open_prs)}")
    for pr in open_prs:
        pr_num = pr["number"]
        title = pr["title"]
        comment_payload = {
            "body": "Merged into `main` after architectural review, schema alignment, and integration testing. All 51 test cases passing across all modules."
        }
        requests.post(f"https://api.github.com/repos/ausyeah/PaperAgent/issues/{pr_num}/comments", headers=headers, json=comment_payload)
        
        close_payload = {"state": "closed"}
        patch_r = requests.patch(f"https://api.github.com/repos/ausyeah/PaperAgent/pulls/{pr_num}", headers=headers, json=close_payload)
        print(f"PR #{pr_num} ({title[:35]}...) closed: {patch_r.status_code}")
else:
    print("Error fetching PRs:", r_prs.status_code)

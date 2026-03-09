import os
import urllib.request
import json

from utils import normalize_domain, resolve_domain_root, resolve_site_root


def fetch_json(url):
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


# -------------------
# GitHub email search
# -------------------
def github_email_search(domain, base):
    results = []

    url = f"https://api.github.com/search/code?q=%22%40{domain}%22"
    data = fetch_json(url)

    if data and "items" in data:
        for item in data["items"]:
            results.append(item.get("html_url", ""))

    with open(f"{base}/github-email-hits.txt", "w") as f:
        f.write("\n".join(results) if results else "none found")

    return len(results)


# -------------------
# GitHub repo search
# -------------------
def github_repo_search(domain, base):
    repos = []

    data = fetch_json(
        f"https://api.github.com/search/repositories?q={domain}"
    )

    if data and "items" in data:
        for repo in data["items"]:
            repos.append(repo.get("html_url", ""))

    with open(f"{base}/github-repos.txt", "w") as f:
        f.write("\n".join(repos) if repos else "none found")

    return len(repos)


# -------------------
# GitLab search
# -------------------
def gitlab_scan(domain, base):
    repos = []

    data = fetch_json(
        f"https://gitlab.com/api/v4/projects?search={domain}"
    )

    if data:
        for proj in data:
            repos.append(proj.get("web_url", ""))

    with open(f"{base}/gitlab-repos.txt", "w") as f:
        f.write("\n".join(repos) if repos else "none found")

    return len(repos)


# -------------------
# Gitea probing
# -------------------
def gitea_scan(domain, base):
    repos = []
    endpoints = [
        f"https://git.{domain}/api/v1/repos/search",
        f"https://gitea.{domain}/api/v1/repos/search",
    ]

    for url in endpoints:
        data = fetch_json(url)
        if data and "data" in data:
            for r in data["data"]:
                repos.append(r.get("html_url", ""))

    with open(f"{base}/gitea-repos.txt", "w") as f:
        f.write("\n".join(repos) if repos else "none found")

    return len(repos)


def repos_scan(domain):
    domain = normalize_domain(domain)

    base = os.path.join(resolve_domain_root(domain), "repos")
    os.makedirs(base, exist_ok=True)

    print(f"[+] Repo discovery for {domain}")

    gh_email = github_email_search(domain, base)
    gh_repo = github_repo_search(domain, base)
    gl_repo = gitlab_scan(domain, base)
    gt_repo = gitea_scan(domain, base)

    summary = f"""
GitHub email hits: {gh_email}
GitHub repos: {gh_repo}
GitLab repos: {gl_repo}
Gitea repos: {gt_repo}
"""

    with open(f"{base}/summary.txt", "w") as f:
        f.write(summary.strip())

    print("[OK] Repo discovery complete")

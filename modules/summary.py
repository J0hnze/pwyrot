import os
import sys

from utils import normalize_domain, resolve_domain_root, resolve_hosts_root, resolve_site_root


def read_file(path):
    if not os.path.isfile(path):
        return "none found"

    with open(path) as f:
        data = f.read().strip()
        return data if data else "none found"


def count_lines(path):
    if not os.path.isfile(path):
        return 0
    with open(path) as f:
        return len([x for x in f if x.strip()])


def summary_scan(domain=None, site_root_override=None, debug=False):
    site_root, hosts_root, domain_root, domain = resolve_paths(domain, site_root_override, debug)

    summary_file = os.path.join(site_root, "summary.md")

    print(f"[+] Building summary for {domain} (site root: {site_root})")
    if debug:
        _debug_dump_paths(site_root, hosts_root, domain_root, summary_file)

    alive_file = os.path.join(hosts_root, "valid-hosts.txt")
    ssl_summary = os.path.join(domain_root, "ssl-summary.txt")
    repo_summary = os.path.join(domain_root, "repos", "summary.txt")
    provider_file = os.path.join(domain_root, "infra", "provider.txt")
    screenshot_dir = hosts_root
    marker_counts = summarise(hosts_root, debug)
    ssl_findings = summarise_ssl(hosts_root, debug)
    alive_hosts = load_alive(alive_file)
    repo_urls = load_repos(domain_root)

    alive_count = count_lines(alive_file)
    ssl_data = read_file(ssl_summary)
    repo_data = read_file(repo_summary)
    provider = read_file(provider_file)

    screenshot_count = 0
    if os.path.isdir(screenshot_dir):
        for root, _, files in os.walk(screenshot_dir):
            screenshot_count += len([f for f in files if f.endswith(".jpg")])

    report = f"""
# External Assessment Summary

## Domain
{domain}

---

## Infrastructure
Provider: {provider}

---

## Alive Hosts
{alive_count}
{format_list(alive_hosts)}

---

## SSL Findings
{ssl_data}

### Per Host TLS Support
{format_list(ssl_findings)}

---

## Repository Discovery
{repo_data}

### Repositories
{format_list(repo_urls)}

---

## Screenshots Captured
{screenshot_count}

---

## Host Markers

### Redirected
Count: {marker_counts.get('r', 0)}
{format_redirects(marker_counts.get('redirects', []))}

### Inactive
Count: {marker_counts.get('i', 0)}

### Blank
Count: {marker_counts.get('b', 0)}

---
"""

    with open(summary_file, "w") as f:
        f.write(report.strip())

    print("[OK] Summary generated")


def summarise(hosts_root, debug=False):
    """
    Traverse hosts directory and count marker directories with prefixes:
      _r_ -> redirected (optionally read redirected_to file for endpoint)
      _i_ -> inactive / possible forgotten asset
      _b_ -> blank white page
    """
    markers = {"r": 0, "i": 0, "b": 0}
    redirects = []
    if not os.path.isdir(hosts_root):
        markers["redirects"] = []
        if debug:
            print(f"[DEBUG] hosts_root not found: {hosts_root}", file=sys.stderr)
        return markers

    if debug:
        print(f"[DEBUG] walking hosts_root: {hosts_root}", file=sys.stderr)

    for root, dirs, _ in os.walk(hosts_root):
        if debug:
            print(f"[DEBUG] at {root}, dirs={dirs}", file=sys.stderr)
        for d in dirs:
            full = os.path.join(root, d)
            name = d.lower()
            if name.startswith("_r_"):
                markers["r"] += 1
                # Accept several filename variants for redirect target
                candidates = [
                    "redirected_to",
                    "redirects_to",
                    "redirected to",
                    "redirects to",
                    "Redirected to",
                    "Redirects to",
                    "redirect_to",
                    "redirect to",
                    "redirectedto",
                    "redirectsto",
                    "redirect.txt",
                    "redirected.txt",
                    "redirects.txt",
                    "target",
                    "target.txt",
                    "location",
                    "location.txt",
                ]
                target = None
                for cand in candidates:
                    cand_path = os.path.join(full, cand)
                    if os.path.isfile(cand_path):
                        try:
                            with open(cand_path) as f:
                                target = f.read().strip()
                            if target:
                                redirects.append(f"{d}: {target}")
                        except Exception as e:
                            if debug:
                                print(f"[DEBUG] failed reading {cand_path}: {e}", file=sys.stderr)
                        break

                # Heuristic: if still not found, look for any file containing 'redirect'
                if target is None:
                    for fname in os.listdir(full):
                        if "redirect" in fname.lower():
                            cand_path = os.path.join(full, fname)
                            if os.path.isfile(cand_path):
                                try:
                                    with open(cand_path) as f:
                                        target = f.read().strip()
                                    if target:
                                        redirects.append(f"{d}: {target}")
                                except Exception as e:
                                    if debug:
                                        print(f"[DEBUG] failed reading {cand_path}: {e}", file=sys.stderr)
                                break

                if debug and target is None:
                    print(f"[DEBUG] no redirect target file found in {full}", file=sys.stderr)
                if target is None:
                    redirects.append(f"{d}: (no target file)")
            if name.startswith("_i_"):
                markers["i"] += 1
            if name.startswith("_b_"):
                markers["b"] += 1

    markers["redirects"] = redirects
    return markers


def format_redirects(redirects):
    if not redirects:
        return "none found"
    return "\n".join(f"- {entry}" for entry in redirects)


def format_list(items):
    if not items:
        return "none found"
    return "\n".join(f"- {item}" for item in items)


def load_alive(path):
    if not os.path.isfile(path):
        return []
    with open(path) as f:
        return [x.strip() for x in f if x.strip()]


def summarise_ssl(hosts_root, debug=False):
    findings = []
    if not os.path.isdir(hosts_root):
        return findings

    for host_dir in os.listdir(hosts_root):
        host_path = os.path.join(hosts_root, host_dir, "ssl-scanresults")
        if not os.path.isdir(host_path):
            continue
        for file in os.listdir(host_path):
            if not file.endswith(".txt"):
                continue
            fpath = os.path.join(host_path, file)
            try:
                with open(fpath) as f:
                    data = f.read()
                tls13 = "TLSv1.3" in data
                tls12 = "TLSv1.2" in data
                findings.append(f"{host_dir}: TLSv1.3={'yes' if tls13 else 'no'}; TLSv1.2={'yes' if tls12 else 'no'}")
            except Exception as e:
                if debug:
                    print(f"[DEBUG] failed to read ssl file {fpath}: {e}", file=sys.stderr)
    return findings


def load_repos(domain_root):
    repo_dir = os.path.join(domain_root, "repos")
    urls = []
    files = [
        "github-repos.txt",
        "gitlab-repos.txt",
        "gitea-repos.txt",
        "github-email-hits.txt",
    ]
    if not os.path.isdir(repo_dir):
        return urls
    for fname in files:
        fpath = os.path.join(repo_dir, fname)
        if os.path.isfile(fpath):
            with open(fpath) as f:
                urls.extend([x.strip() for x in f if x.strip() and x.strip() != "none found"])
    return urls


def resolve_paths(domain, site_root_override, debug=False):
    """
    Determine site_root, hosts_root, domain_root, and normalized domain based on inputs.
    Allows --dir to point to a site root OR directly to a hosts directory.
    """
    if site_root_override:
        abs_dir = os.path.abspath(site_root_override)
        base = os.path.basename(abs_dir.rstrip("/"))
        parent = os.path.basename(os.path.dirname(abs_dir))
        has_hosts_subdir = os.path.isdir(os.path.join(abs_dir, "hosts"))

        if base == "hosts":
            # path points directly to hosts directory containing host folders
            site_root = os.path.dirname(abs_dir)
            domain = normalize_domain(domain) if domain else os.path.basename(site_root)
            hosts_root = abs_dir
        elif parent == "hosts":
            # path points to a specific host folder; count siblings
            site_root = os.path.dirname(os.path.dirname(abs_dir))
            domain = normalize_domain(domain) if domain else os.path.basename(site_root)
            hosts_root = os.path.dirname(abs_dir)
        elif has_hosts_subdir:
            # path is a site root containing hosts/
            site_root = abs_dir
            domain = normalize_domain(domain) if domain else os.path.basename(site_root)
            hosts_root = os.path.join(site_root, "hosts", domain) if os.path.isdir(os.path.join(site_root, "hosts", domain)) else os.path.join(site_root, "hosts")
        else:
            # fallback: treat abs_dir as hosts_root directly
            site_root = abs_dir
            domain = normalize_domain(domain) if domain else os.path.basename(site_root)
            hosts_root = abs_dir
    else:
        domain = normalize_domain(domain) if domain else ""
        site_root = resolve_site_root(domain) if domain else os.getcwd()
        domain = domain or os.path.basename(site_root)
        hosts_root = resolve_hosts_root(domain)

    if debug:
        print(f"[DEBUG] resolved paths -> site_root: {site_root}, hosts_root: {hosts_root}, domain_root: {os.path.join(site_root, domain)}, domain: {domain}", file=sys.stderr)

    domain_root = os.path.join(site_root, domain)
    return site_root, hosts_root, domain_root, domain

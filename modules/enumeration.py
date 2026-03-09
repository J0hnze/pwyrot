import os
import requests

from utils import normalize_domain, resolve_site_root, resolve_hosts_root


def fetch_subdomains(domain, include_expired=False):
    if include_expired:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
    else:
        url = f"https://crt.sh/?q=%25.{domain}&exclude=expired&output=json"

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        subs = set()

        for entry in data:
            name = entry.get("common_name", "")
            if name:
                subs.add(name.lower())

        return sorted(subs)

    except Exception as e:
        print(f"[!] crt.sh lookup failed: {e}")
        return []


def enum_domain(domain, include_expired=False):
    domain = normalize_domain(domain)

    site_root = resolve_site_root(domain)
    hosts_root = resolve_hosts_root(domain)

    os.makedirs(site_root, exist_ok=True)
    os.makedirs(hosts_root, exist_ok=True)

    hosts_file = os.path.join(hosts_root, "hosts.txt")

    print(f"[+] Enumerating subdomains for {domain}")

    subdomains = fetch_subdomains(domain, include_expired)

    # Always include root domain
    subdomains.append(domain)

    cleaned = sorted(set(subdomains))

    # Write hosts file
    with open(hosts_file, "w") as f:
        f.write("\n".join(cleaned))

    # Create host folders beneath this target domain
    for host in cleaned:
        os.makedirs(os.path.join(hosts_root, host), exist_ok=True)

    print(f"[OK] {len(cleaned)} hosts written to {hosts_file}")
    print(f"[OK] Host folders created under {hosts_root}")

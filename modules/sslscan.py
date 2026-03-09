import os
import subprocess
import shutil
from urllib.parse import urlparse

from utils import normalize_domain, resolve_hosts_root, resolve_site_root, tool_check


def extract_host(url):
    return urlparse(url).hostname


def ssl_scan(domain):
    domain = normalize_domain(domain)

    if not tool_check("sslscan"):
        return

    # -------------------------
    # Detect site root
    # -------------------------
    site_root = resolve_site_root(domain)
    hosts_root = resolve_hosts_root(domain)

    valid_file = os.path.join(hosts_root, "valid-hosts.txt")

    if not os.path.isfile(valid_file):
        print("[!] valid-hosts.txt not found — run alive module first")
        return

    print(f"[+] Running sslscan for {domain}")

    with open(valid_file) as f:
        urls = [x.strip() for x in f if x.strip()]

    for url in urls:
        if not url.startswith("https://"):
            continue

        host = extract_host(url)

        if not host:
            continue

        out_dir = os.path.join(hosts_root, host, "ssl-scanresults")
        os.makedirs(out_dir, exist_ok=True)

        output_file = os.path.join(out_dir, f"{host}-sslscan.txt")

        if os.path.exists(output_file):
            print(f"[+] Skipping existing sslscan: {host}")
            continue

        print(f"[+] Scanning {host}")

        try:
            with open(output_file, "w") as outfile:
                subprocess.run(
                    ["sslscan", "--no-colour", host],
                    stdout=outfile,
                    stderr=subprocess.DEVNULL
                )
        except Exception:
            print(f"[!] sslscan failed for {host}")

    print("[OK] SSL scan module complete")

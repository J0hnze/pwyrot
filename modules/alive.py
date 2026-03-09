import os
import subprocess

from utils import (
    normalize_domain,
    normalize_host,
    resolve_site_root,
    resolve_hosts_root,
    tool_check,
)


def extract_redirect(headers):
    for line in headers.splitlines():
        if line.lower().startswith("location:"):
            return line.split(":", 1)[1].strip()
    return None


def alive_scan(domain=None, input_override=None):

    if not tool_check("curl"):
        return

    if not domain and not input_override:
        print("[!] Provide either a domain (-d) or an input file (-i)")
        return

    if domain:
        domain = normalize_domain(domain)
        site_root = resolve_site_root(domain)
        hosts_dir = resolve_hosts_root(domain)
    else:
        site_root = os.getcwd()
        hosts_dir = os.path.join(site_root, "hosts")

    os.makedirs(hosts_dir, exist_ok=True)

    input_file = input_override or os.path.join(hosts_dir, "hosts.txt")

    if not os.path.isfile(input_file):
        print(f"[!] Missing input file: {input_file}")
        return

    print(f"[+] Cleaning host list from {input_file}")

    with open(input_file) as f:
        cleaned = sorted(
            set(normalize_host(line) for line in f if line.strip())
        )

    clean_file = os.path.join(hosts_dir, "cleaned-hosts.txt")
    with open(clean_file, "w") as f:
        f.write("\n".join(cleaned))

    valid = []
    results = []

    for host in cleaned:
        for proto in ["https://", "http://"]:
            url = proto + host

            try:
                r = subprocess.run(
                    ["curl", "-Is", "--max-time", "3", url],
                    capture_output=True,
                    text=True
                )

                if "HTTP/" in r.stdout:
                    status = r.stdout.split("\n")[0]
                    redirect = extract_redirect(r.stdout)

                    valid.append(url)

                    if redirect:
                        results.append(f"{url} {status} -> {redirect}")
                    else:
                        results.append(f"{url} {status}")

                    break

            except Exception:
                pass

    valid_file = os.path.join(hosts_dir, "valid-hosts.txt")
    results_file = os.path.join(hosts_dir, "alive-results.txt")

    with open(valid_file, "w") as f:
        f.write("\n".join(valid) if valid else "none found")

    with open(results_file, "w") as f:
        f.write("\n".join(results) if results else "none found")

    print("[OK] Alive scan complete")
    print(f"[OK] Valid hosts: {len(valid)}")

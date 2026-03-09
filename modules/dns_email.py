import os
import subprocess
import shutil

from utils import (
    normalize_domain,
    resolve_domain_root,
    resolve_site_root,
    tool_check,
)


def collect_dns_email(domain):
    domain = normalize_domain(domain)

    if not tool_check("dig"):
        return

    site_root = resolve_site_root(domain)
    domain_root = resolve_domain_root(domain)
    dns_dir = os.path.join(domain_root, "dns")
    os.makedirs(dns_dir, exist_ok=True)

    print(f"[+] Collecting DNS + email security records for {domain}")

    # -------------------------
    # SPF
    # -------------------------
    spf_file = os.path.join(dns_dir, "spf.txt")
    spf = subprocess.run(
        ["dig", "+short", "TXT", domain],
        capture_output=True,
        text=True
    )

    with open(spf_file, "w") as f:
        f.write(spf.stdout if spf.stdout else "none found")

    # -------------------------
    # DMARC
    # -------------------------
    dmarc_file = os.path.join(dns_dir, "dmarc.txt")
    dmarc = subprocess.run(
        ["dig", "+short", "TXT", f"_dmarc.{domain}"],
        capture_output=True,
        text=True
    )

    with open(dmarc_file, "w") as f:
        f.write(dmarc.stdout if dmarc.stdout else "none found")

    # -------------------------
    # DKIM selector example
    # -------------------------
    dkim_file = os.path.join(dns_dir, "dkim.txt")
    dkim = subprocess.run(
        ["dig", "+short", "TXT", f"default._domainkey.{domain}"],
        capture_output=True,
        text=True
    )

    with open(dkim_file, "w") as f:
        f.write(dkim.stdout if dkim.stdout else "none found")

    print("[OK] DNS module complete")

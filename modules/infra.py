import os
import subprocess
import shutil

from utils import (
    normalize_domain,
    resolve_domain_root,
    resolve_site_root,
    tool_check,
)


def infra_scan(domain):
    domain = normalize_domain(domain)

    if not tool_check("whois"):
        return

    site_root = resolve_site_root(domain)
    domain_root = resolve_domain_root(domain)
    infra_dir = os.path.join(domain_root, "infra")
    os.makedirs(infra_dir, exist_ok=True)

    print(f"[+] Running infra scan for {domain}")

    # -------------------------
    # WHOIS lookup
    # -------------------------
    whois_file = os.path.join(infra_dir, "whois.txt")

    try:
        result = subprocess.run(
            ["whois", domain],
            capture_output=True,
            text=True
        )

        with open(whois_file, "w") as f:
            f.write(result.stdout)

    except Exception:
        print("[!] WHOIS lookup failed")

    # -------------------------
    # Provider detection
    # -------------------------
    provider_file = os.path.join(infra_dir, "provider.txt")

    provider = "unknown"

    try:
        if "cloudflare" in result.stdout.lower():
            provider = "Cloudflare"
        elif "amazon" in result.stdout.lower():
            provider = "AWS"
        elif "google" in result.stdout.lower():
            provider = "GCP"
    except Exception:
        pass

    with open(provider_file, "w") as f:
        f.write(provider)

    print("[OK] Infra module complete")

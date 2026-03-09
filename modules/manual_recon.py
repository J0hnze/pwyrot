import os
import webbrowser

from utils import normalize_domain, resolve_domain_root


def manual_recon(domain, open_browser=False):
    domain = normalize_domain(domain)

    domain_root = resolve_domain_root(domain)
    output_file = os.path.join(domain_root, "manual-recon-links.txt")

    os.makedirs(domain_root, exist_ok=True)

    links = [
        f"https://buckets.grayhatwarfare.com/?q={domain}",
        f"https://www.google.com/search?q=site:{domain}+password",
        f"https://www.google.com/search?q=site:{domain}+confidential",
        f"https://www.google.com/search?q=\"{domain}\"+leak",
        f"https://www.google.com/search?q=\"{domain}\"+credentials",
        f"https://github.com/search?q={domain}&type=code",
        f"https://github.com/search?q={domain}&type=repositories",
    ]

    with open(output_file, "w") as f:
        for link in links:
            f.write(link + "\n")

    print(f"[OK] Manual recon links saved to {output_file}")

    if open_browser:
        print("[+] Opening recon searches in browser...")
        for link in links:
            webbrowser.open(link)

import os
import subprocess
import shutil
import re

from utils import normalize_domain, resolve_hosts_root, resolve_site_root, tool_check


# Matches:
#   http---api.example.com-80.png
#   https---uat.example.com-443.jpg
#   https---mail.example.com-443.jpeg
# Case-insensitive on extension.
FILE_RE = re.compile(r"^(https?)---(.+)-(\d+)\.(png|jpe?g)$", re.IGNORECASE)


def screenshots_scan(domain, debug=False):
    domain = normalize_domain(domain)

    if not tool_check("gowitness"):
        return

    site_root = resolve_site_root(domain)
    hosts_root = resolve_hosts_root(domain)

    input_file = os.path.join(hosts_root, "cleaned-hosts.txt")
    if not os.path.isfile(input_file):
        print("[!] cleaned-hosts.txt not found — run alive module first")
        print(f"[!] Expected: {input_file}")
        return

    temp_dir = os.path.join(site_root, "_screenshots_tmp")
    os.makedirs(temp_dir, exist_ok=True)

    if debug:
        print("[DEBUG] site_root:", site_root)
        print("[DEBUG] screenshot input:", input_file)
        print("[DEBUG] temp_dir:", temp_dir)

    cmd = [
        "gowitness",
        "scan",
        "file",
        "--file",
        input_file,
        "--screenshot-path",
        temp_dir
    ]

    if debug:
        print("[DEBUG] Running:", " ".join(cmd))

    subprocess.run(cmd, check=False)

    # Some gowitness versions may create subfolders; walk temp_dir to be safe.
    moved = 0
    seen_files = 0
    unmatched = []

    for root, _dirs, files in os.walk(temp_dir):
        for fname in files:
            seen_files += 1
            src = os.path.join(root, fname)

            m = FILE_RE.match(fname)
            if not m:
                unmatched.append(fname)
                continue

            host = m.group(2)
            port = m.group(3)
            ext = m.group(4).lower()

            dest_dir = os.path.join(hosts_root, host, "screenshots")
            os.makedirs(dest_dir, exist_ok=True)

            dest = os.path.join(dest_dir, f"{host}-{port}.{ext}")

            # Skip overwrite
            if os.path.exists(dest):
                try:
                    os.remove(src)
                except Exception:
                    pass
                continue

            try:
                os.rename(src, dest)
                moved += 1
            except OSError:
                # fallback for cross-device moves
                try:
                    shutil.copy2(src, dest)
                    os.remove(src)
                    moved += 1
                except Exception:
                    pass

    if debug:
        print(f"[DEBUG] Files found in temp_dir: {seen_files}")
        print(f"[DEBUG] Files moved: {moved}")
        if unmatched:
            print(f"[DEBUG] Unmatched filenames (first 25): {unmatched[:25]}")

    # If nothing moved and debug is on, keep temp_dir so you can inspect it
    if moved == 0 and debug:
        print(f"[DEBUG] Nothing moved. Leaving temp dir for inspection: {temp_dir}")
        return

    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"[OK] Screenshot module complete ({moved} screenshots moved)")

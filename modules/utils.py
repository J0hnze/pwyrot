import os
import shutil


def normalize_domain(domain):
    domain = domain.strip().lower()
    domain = domain.replace("http://", "").replace("https://", "")
    domain = domain.replace("www.", "")
    return domain.strip("/")


def base_name(domain):
    """Return the left-most label (example.com -> example)."""
    normalized = normalize_domain(domain)
    return normalized.split(".")[0] if normalized else ""


def normalize_host(entry):
    entry = entry.strip().lower()
    entry = entry.replace("http://", "").replace("https://", "")
    entry = entry.replace("www.", "")
    entry = entry.replace("*.", "")
    entry = entry.split("/")[0]
    return entry


def resolve_site_root(domain):
    """Root folder for a family of domains (e.g., example.com -> sites/example)."""
    domain = normalize_domain(domain)
    root = base_name(domain)
    cwd = os.getcwd()

    if cwd.endswith(f"sites/{root}") or cwd.endswith(root):
        return cwd

    return os.path.join("sites", root)


def resolve_hosts_root(domain):
    """Hosts directory for a specific domain under its family root."""
    return os.path.join(resolve_site_root(domain), "hosts", normalize_domain(domain))


def resolve_domain_root(domain):
    """Per-domain data directory under the family root."""
    return os.path.join(resolve_site_root(domain), normalize_domain(domain))


def tool_check(tool):
    if shutil.which(tool) is None:
        print(f"[!] Please make sure '{tool}' is installed")
        return False
    return True

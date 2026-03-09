def show_help():
    print("""
pwyrot — External Assessment Toolkit

Usage:
  pwyrot <command> [options]

Commands:

  start        Create assessment workspace structure
  enum         Discover subdomains using crt.sh
  alive        Validate reachable hosts
  screenshots  Capture screenshots of live hosts
  ssl          Run SSL/TLS scans against HTTPS hosts
  dns          Collect DNS + email security records
  infra        Identify hosting provider / ASN / CDN
  repos        Search public repositories
  recon        Generate manual recon search links
  summary      Build assessment summary report
  all          Run full assessment workflow
  help         Show this help message

Examples:

  pwyrot enum -d example.com
  pwyrot alive -d example.com
  pwyrot all -d example.com
""")

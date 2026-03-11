#!/c/Users/smiller/AppData/Local/Programs/Python/Python312/python.exe
"""
check_security.py — Check website security headers and HTTPS configuration.

Usage:
    python scripts/check_security.py <url>

Output:
    JSON to stdout with security check results.
"""

import argparse
import json
import os
import re
import ssl
import socket
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_page import fetch


SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy",
]


def check_https_redirect(url):
    """Check if HTTP redirects to HTTPS."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme == "https":
        http_url = url.replace("https://", "http://", 1)
    else:
        http_url = url

    try:
        req = urllib.request.Request(http_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        # Don't follow redirects — check the redirect itself
        class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        opener = urllib.request.build_opener(NoRedirectHandler)
        try:
            response = opener.open(req, timeout=10)
            # If we get here, no redirect happened
            return {
                "http_to_https": False,
                "http_status": response.status,
                "note": "HTTP did not redirect to HTTPS",
            }
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 307, 308):
                location = e.headers.get("Location", "")
                redirects_to_https = location.startswith("https://")
                return {
                    "http_to_https": redirects_to_https,
                    "redirect_code": e.code,
                    "redirect_location": location,
                }
            return {
                "http_to_https": False,
                "http_status": e.code,
                "error": str(e),
            }
    except Exception as e:
        return {"http_to_https": None, "error": str(e)}


def check_ssl_cert(hostname):
    """Check SSL certificate details."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

                # Extract fields
                subject = dict(x[0] for x in cert.get("subject", ()))
                issuer = dict(x[0] for x in cert.get("issuer", ()))
                san = [entry[1] for entry in cert.get("subjectAltName", ())]

                return {
                    "valid": True,
                    "subject": subject.get("commonName", ""),
                    "issuer": issuer.get("organizationName", ""),
                    "not_before": cert.get("notBefore", ""),
                    "not_after": cert.get("notAfter", ""),
                    "san": san,
                    "protocol": ssock.version(),
                }
    except ssl.SSLCertVerificationError as e:
        return {"valid": False, "error": f"Certificate verification failed: {e}"}
    except ssl.SSLError as e:
        return {"valid": False, "error": f"SSL error: {e}"}
    except (socket.timeout, socket.gaierror, OSError) as e:
        return {"valid": False, "error": f"Connection error: {e}"}


def check_security_headers(headers):
    """Check for presence of security headers."""
    results = {}
    for header in SECURITY_HEADERS:
        value = None
        # Case-insensitive header lookup
        for k, v in headers.items():
            if k.lower() == header.lower():
                value = v
                break
        results[header] = {
            "present": value is not None,
            "value": value,
        }
    return results


def check_mixed_content(html, base_url):
    """Scan for mixed content (HTTP resources on HTTPS page)."""
    if not base_url.startswith("https://"):
        return {"applicable": False, "note": "Site not on HTTPS"}

    # Find http:// URLs in src and href attributes
    mixed = []
    patterns = [
        (r'src=["\']http://([^"\']+)["\']', "src"),
        (r'href=["\']http://([^"\']+)["\']', "href"),
    ]

    for pattern, attr_type in patterns:
        for match in re.finditer(pattern, html):
            url = f"http://{match.group(1)}"
            # Skip anchors and non-resource hrefs
            if attr_type == "href":
                # Only flag stylesheet/script hrefs, not navigation links
                context_start = max(0, match.start() - 50)
                context = html[context_start:match.start()]
                if 'rel="stylesheet"' not in context and "<script" not in context:
                    continue
            mixed.append({"url": url, "attribute": attr_type})

    return {
        "applicable": True,
        "mixed_content_found": len(mixed),
        "items": mixed[:20],  # Limit output
    }


def run_security_check(url):
    """Run all security checks."""
    parsed = urllib.parse.urlparse(url)
    hostname = parsed.netloc

    result = {
        "url": url,
        "https_redirect": None,
        "ssl_certificate": None,
        "security_headers": None,
        "mixed_content": None,
    }

    # 1. HTTPS redirect check
    print("[security] Checking HTTPS redirect...", file=sys.stderr)
    result["https_redirect"] = check_https_redirect(url)

    # 2. SSL certificate check
    print("[security] Checking SSL certificate...", file=sys.stderr)
    result["ssl_certificate"] = check_ssl_cert(hostname)

    # 3. Fetch page for headers and content
    print("[security] Fetching page for headers...", file=sys.stderr)
    try:
        html, final_url, status, headers = fetch(url)
        result["security_headers"] = check_security_headers(headers)
        result["mixed_content"] = check_mixed_content(html, final_url)
    except RuntimeError as e:
        result["security_headers"] = {"error": str(e)}
        result["mixed_content"] = {"error": str(e)}

    return result


def main():
    parser = argparse.ArgumentParser(description="Check website security")
    parser.add_argument("url", help="URL to check")
    args = parser.parse_args()

    result = run_security_check(args.url)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

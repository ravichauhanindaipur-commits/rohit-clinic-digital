#!/usr/bin/env python3
"""SEO Audit Agent for Rohit Clinic Digital.
Audits a public website and writes a readable report. It does not modify the website.
"""
from urllib.parse import urljoin, urlparse
from datetime import datetime
import sys
import requests
from bs4 import BeautifulSoup

DEFAULT_URL = "https://ravichauhanindaipur-commits.github.io/rohit-clinic-digital/"
TIMEOUT = 20
HEADERS = {"User-Agent": "RohitClinicSEOAuditAgent/1.0 (+public SEO diagnostics)"}

def fetch(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        return response, None
    except requests.RequestException as exc:
        return None, str(exc)

def clean_text(node):
    return " ".join(node.get_text(" ", strip=True).split()) if node else ""

def audit_page(url, lines):
    lines.append(f"TARGET URL: {url}")
    response, error = fetch(url)
    if error:
        lines += [f"ERROR: Page request failed: {error}", ""]
        return
    lines.append(f"HTTP status: {response.status_code}")
    lines.append(f"Final URL after redirects: {response.url}")
    if response.status_code != 200:
        lines.append("ACTION: Investigate the HTTP status/redirect before indexing.")
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = (desc_tag.get("content") or "").strip() if desc_tag else ""
    canonical_tag = soup.find("link", rel=lambda value: value and "canonical" in value)
    canonical = (canonical_tag.get("href") or "").strip() if canonical_tag else ""
    robots_tag = soup.find("meta", attrs={"name": "robots"})
    robots = (robots_tag.get("content") or "").strip() if robots_tag else "(not specified)"
    h1s = [clean_text(x) for x in soup.find_all("h1")]
    h2_count = len(soup.find_all("h2"))
    images = soup.find_all("img")
    missing_alt = [img.get("src", "(no src)") for img in images if not (img.get("alt") or "").strip()]
    links = soup.find_all("a", href=True)
    internal, external, broken_format = [], [], []
    host = urlparse(response.url).netloc.lower()
    for link in links:
        href = (link.get("href") or "").strip()
        if not href or href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        absolute = urljoin(response.url, href)
        parsed = urlparse(absolute)
        if parsed.scheme not in ("http", "https"):
            broken_format.append(href)
        elif parsed.netloc.lower() == host:
            internal.append(absolute)
        else:
            external.append(absolute)
    text = clean_text(soup)
    lines.append("")
    lines.append("ON-PAGE SEO")
    lines.append(f"Title ({len(title)} characters): {title or '(MISSING)'}")
    lines.append(f"Meta description ({len(description)} characters): {description or '(MISSING)'}")
    lines.append(f"Canonical: {canonical or '(MISSING)'}")
    lines.append(f"Meta robots: {robots}")
    lines.append(f"H1 count: {len(h1s)}")
    for i, h in enumerate(h1s, 1):
        lines.append(f"  H1 {i}: {h}")
    lines.append(f"H2 count: {h2_count}")
    lines.append(f"Images: {len(images)} total; {len(missing_alt)} missing alt text")
    for src in missing_alt[:10]:
        lines.append(f"  Missing alt: {src}")
    lines.append(f"Links: {len(internal)} internal, {len(external)} external")
    lines.append(f"Visible text estimate: {len(text)} characters")
    lines.append("")
    lines.append("RECOMMENDED ACTIONS")
    if not title:
        lines.append("- Add a unique, descriptive <title>.")
    elif len(title) < 25 or len(title) > 65:
        lines.append("- Review title length; a practical target is about 30–60 characters, while keeping it natural.")
    else:
        lines.append("- Title is present and within a practical length range.")
    if not description:
        lines.append("- Add a unique meta description.")
    elif len(description) < 70 or len(description) > 170:
        lines.append("- Review meta description length; aim for a concise, useful summary (roughly 120–160 characters).")
    else:
        lines.append("- Meta description is present and a practical length.")
    if not canonical:
        lines.append("- Add a canonical URL pointing to the preferred public page URL.")
    elif urlparse(canonical).netloc != urlparse(DEFAULT_URL).netloc:
        lines.append("- Verify canonical points to the intended live site URL.")
    if len(h1s) == 0:
        lines.append("- Add one clear main H1 heading.")
    elif len(h1s) > 1:
        lines.append("- Review whether multiple H1 headings are intentional; use one clear main page heading where practical.")
    if missing_alt:
        lines.append("- Add meaningful alt text to informative images; use empty alt for decorative images.")
    if not text or len(text) < 300:
        lines.append("- Check that the page contains enough useful, visible, original information for visitors.")
    lines.append("- Keep clinic claims factual; do not add unsupported medical qualifications or promises.")
    lines.append("")

def audit_auxiliary(base_url, lines):
    root = base_url.rstrip("/") + "/"
    for name in ("robots.txt", "sitemap.xml"):
        url = urljoin(root, name)
        lines.append(f"CHECK: {url}")
        response, error = fetch(url)
        if error:
            lines.append(f"  ERROR: {error}")
            continue
        lines.append(f"  HTTP status: {response.status_code}")
        content_type = response.headers.get("content-type", "(not provided)")
        lines.append(f"  Content-Type: {content_type}")
        body = response.text.strip()
        if response.status_code != 200:
            lines.append("  ACTION: This URL did not return HTTP 200; check the deployed file path.")
        elif name == "sitemap.xml":
            soup = BeautifulSoup(body, "xml")
            urls = soup.find_all("loc")
            if not body:
                lines.append("  ACTION: Response body is empty.")
            elif "<urlset" not in body and "<sitemapindex" not in body:
                lines.append("  ACTION: Response does not look like a standard XML sitemap.")
            else:
                lines.append(f"  XML sitemap appears present; URL entries found: {len(urls)}")
                for loc in urls[:10]:
                    lines.append(f"    {loc.get_text(strip=True)}")
                if not urls:
                    lines.append("  ACTION: No <loc> entries detected; validate the XML sitemap.")
        else:
            lines.append("  robots.txt preview:")
            for line in body.splitlines()[:12]:
                lines.append("    " + line)
        lines.append("")

def main():
    url = sys.argv[1].strip() if len(sys.argv) > 1 else DEFAULT_URL
    if not url.startswith(("https://", "http://")):
        url = "https://" + url
    parsed = urlparse(url)
    if not parsed.netloc:
        print("Invalid URL. Example: python main.py https://example.com/")
        raise SystemExit(2)
    report = [
        "ROHIT CLINIC DIGITAL — SEO AUDIT REPORT",
        f"Generated: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "=" * 54,
        "Note: This tool checks publicly accessible HTML and does not edit or publish files.",
        ""
    ]
    audit_page(url, report)
    # GitHub Pages project sites put robots.txt and sitemap.xml at the project root.
    base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    audit_auxiliary(base, report)
    output = "\n".join(report)
    filename = "seo-audit-report.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(output + "\n")
    print(output)
    print(f"\nReport saved to: {filename}")

if __name__ == "__main__":
    main()

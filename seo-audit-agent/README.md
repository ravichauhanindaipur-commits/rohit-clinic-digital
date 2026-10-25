# SEO Audit Agent — Rohit Clinic Digital

This is a safe, read-only SEO audit tool for the public GitHub Pages site. It checks:
- HTTP status and final URL
- title, meta description, canonical, robots meta
- H1/H2 headings, image alt text, internal/external links
- `robots.txt` and `sitemap.xml` HTTP responses and basic sitemap XML structure

It **does not modify website files**, push commits, or submit indexing requests.

## Run in Termux
```bash
cd ~/seo-audit-agent
python -m pip install -r requirements.txt
python main.py
```

To audit another URL:
```bash
python main.py https://example.com/
```

The report is printed in the terminal and saved as `seo-audit-report.txt`.
A successful audit does not guarantee Google indexing; Search Console's sitemap status can take time to update.

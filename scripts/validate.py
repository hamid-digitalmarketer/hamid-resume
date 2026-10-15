# -*- coding: utf-8 -*-
"""Multi-page QA validation for hamid-resume.

Checks across public/**/*.html:
- WhatsApp-only contact: no mailto:/tel:/form anywhere
- Exactly one H1 per page
- Canonical, meta description, title present
- Valid JSON-LD blocks
- Internal links resolve to existing files (same depth-relative)
- Sitemap lists every page, robots.txt and llms.txt exist
- firebase.json is valid JSON
"""
import os
import json
import re
import sys
import glob
import html as html_mod


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    print("Validating hamid-resume in:", root)

    # 1. Required top-level files
    for f in ["firebase.json", ".firebaserc", "public/robots.txt", "public/sitemap.xml", "public/llms.txt",
              "public/css/style.css", "public/js/main.js", "public/favicon.svg",
              "public/images/muhammad-hamid-headshot.webp"]:
        assert os.path.exists(f), f"Missing required file: {f}"
    print("[+] Required config/asset files exist.")

    # 2. firebase.json valid JSON
    with open("firebase.json", "r", encoding="utf-8") as fp:
        fb = json.load(fp)
    assert "hosting" in fb and fb["hosting"].get("public") == "public"
    print("[+] firebase.json is valid JSON with hosting.public='public'.")

    # 3. Sitemap sanity
    with open("public/sitemap.xml", "r", encoding="utf-8") as fp:
        sitemap = fp.read()
    locs = re.findall(r"<loc>(.*?)</loc>", sitemap, re.DOTALL)
    loc_paths = set(l.replace("https://hamid-resume.web.app", "") for l in locs)
    assert len(loc_paths) >= 20, f"sitemap has only {len(loc_paths)} URLs"
    print(f"[+] Sitemap contains {len(loc_paths)} URLs.")

    # 4. Robots
    robots = open("public/robots.txt", "r", encoding="utf-8").read()
    assert "Sitemap: https://hamid-resume.web.app/sitemap.xml" in robots
    print("[+] robots.txt references the sitemap.")

    # 5. llms.txt has project links
    llms = open("public/llms.txt", "r", encoding="utf-8").read()
    assert "hamid-resume.web.app" in llms and "wa.me/923167417135" in llms
    print("[+] llms.txt present with site and WhatsApp references.")

    # 6. Per-page HTML checks
    pages = sorted(set(p.replace("\\", "/") for p in glob.glob("public/**/*.html", recursive=True)))
    if not any(p == "public/404.html" for p in pages):
        pages.append("public/404.html")
    pages = sorted(set(pages))
    assert len(pages) >= 22, f"Expected 22+ pages, found {len(pages)}"
    print(f"[+] Found {len(pages)} HTML pages.")

    errors = []
    for rel in pages:
        rel = rel.replace("\\", "/")
        with open(rel, "r", encoding="utf-8") as fp:
            content = fp.read()
        name = rel.replace("public/", "")
        # WhatsApp-only
        if "mailto:" in content:
            errors.append(f"{name}: mailto: link found")
        if "tel:" in content:
            errors.append(f"{name}: tel: link found")
        if "<form" in content.lower():
            errors.append(f"{name}: form element found")
        if "wa.me/923167417135" not in content:
            errors.append(f"{name}: missing WhatsApp link")
        # One H1
        h1s = re.findall(r"<h1[^>]*>", content)
        if len(h1s) != 1:
            errors.append(f"{name}: {len(h1s)} H1 tags (expected 1)")
        # Title / description / canonical
        if not re.search(r"<title>.*?</title>", content, re.DOTALL):
            errors.append(f"{name}: missing <title>")
        if not re.search(r'<meta name="description" content="[^"]+"', content):
            errors.append(f"{name}: missing meta description")
        if not re.search(r'<link rel="canonical" href="https://hamid-resume\.web\.app/', content):
            errors.append(f"{name}: missing/incorrect canonical")
        # JSON-LD
        schemas = re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
        if not schemas:
            errors.append(f"{name}: no JSON-LD blocks")
        for i, s in enumerate(schemas):
            try:
                parsed = json.loads(s.strip())
                assert "@context" in parsed
                assert parsed.get("@type")
            except Exception as e:
                errors.append(f"{name}: JSON-LD block {i+1} invalid ({e})")
        # Internal link resolution (skip external, anchors, wa, mailto/tel)
        depth = name.count("/")
        prefix = "../" * depth if depth else ""
        for m in re.finditer(r'href="([^"#]+)"', content):
            href = m.group(1)
            if href.startswith(("http", "mailto:", "tel:", "//", "javascript:")):
                continue
            if href.endswith((".png", ".jpg", ".jpeg", ".webp", ".svg", ".css", ".js", ".ico")):
                target = os.path.normpath(os.path.join(os.path.dirname(rel), href)).replace("\\", "/")
                if not os.path.exists(target):
                    errors.append(f"{name}: broken asset link {href} -> {target}")
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(rel), href)).replace("\\", "/")
            if href.endswith("/"):
                target = os.path.join(target, "index.html")
            if not os.path.exists(target):
                errors.append(f"{name}: broken internal link {href} -> {target}")

    # 7. Sitemap coverage
    for rel in pages:
        rel = rel.replace("public/", "")
        url_path = "/" + rel.replace("index.html", "").replace("\\", "/")
        if url_path == "/404.html":
            continue
        if url_path not in loc_paths:
            errors.append(f"sitemap missing {url_path}")
    if errors:
        print("\n[FAIL] %d error(s):" % len(errors))
        for e in errors:
            print("  -", e)
        sys.exit(1)

    print("\n[SUCCESS] All checks passed cleanly with 0 errors!")


if __name__ == "__main__":
    main()

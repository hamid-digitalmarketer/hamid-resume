import os
import json
import re
import sys

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    print("Checking repository files in:", root)

    # 1. Verify required files exist
    required_files = [
        "public/index.html",
        "public/robots.txt",
        "public/sitemap.xml",
        "public/images/muhammad-hamid-headshot.webp",
        "public/images/projects/ppc-waste-detector.png",
        "public/images/projects/conversion-tracking-doctor.png",
        "public/images/projects/meta-lead-quality-analyzer.png",
        "public/images/projects/geo-visibility-lab.png",
        "public/images/projects/seo-doctor.png",
        "firebase.json",
        ".firebaserc",
    ]
    for f in required_files:
        assert os.path.exists(f), f"Missing required file: {f}"
    print("[+] All required files and project preview assets exist.")

    # 2. Check HTML integrity and WhatsApp contact constraint
    with open("public/index.html", "r", encoding="utf-8") as fp:
        content = fp.read()

    assert "mailto:" not in content, "Violated requirement: mailto links found!"
    assert "tel:" not in content, "Violated requirement: tel links found!"
    assert "<form" not in content, "Violated requirement: form found!"
    assert "wa.me/923167417135" in content, "Missing primary WhatsApp link!"
    print("[+] Contact constraint verified: WhatsApp is the exclusive channel.")

    # 3. Extract and validate JSON-LD schemas
    schemas = re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
    assert len(schemas) > 0, "No JSON-LD schemas found in index.html"
    for i, s in enumerate(schemas):
        parsed = json.loads(s.strip())
        assert "@context" in parsed, f"Schema {i} missing @context"
        schema_type = parsed.get("@type", "Graph")
        print(f"[+] JSON-LD Schema {i+1} valid: {schema_type}")

    print("\n[SUCCESS] All checks passed cleanly with 0 errors!")

if __name__ == "__main__":
    main()

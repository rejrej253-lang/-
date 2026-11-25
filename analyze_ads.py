#!/usr/bin/env python3
"""Read-only APKTool Smali scanner. It does not modify the application."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "decoded")
if not root.is_dir():
    raise SystemExit(f"Decoded directory not found: {root}")

sdk_patterns = {
    "Google Mobile Ads / AdMob": re.compile(r"Lcom/google/android/gms/ads/|Lcom/google/ads/"),
    "Meta Audience Network": re.compile(r"Lcom/facebook/ads/"),
    "Pangle / ByteDance": re.compile(r"Lcom/bytedance/sdk/openadsdk/|Lcom/bytedance/adsdk/"),
    "Coocent Promotion": re.compile(r"Lcom/coocent/promotion/ads/"),
    "AppLovin": re.compile(r"Lcom/applovin/"),
}

smali_files = list(root.glob("smali*/**/*.smali"))
if not smali_files:
    raise SystemExit("No Smali source found. APKTool decode may have failed or used --no-src incorrectly.")

print("MAXBOOST AD SDK STATIC ANALYSIS")
print("Mode: READ ONLY — no code is patched")
print(f"Smali files scanned: {len(smali_files)}")

for label, pattern in sdk_patterns.items():
    hits = []
    for file in smali_files:
        try:
            content = file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line_no, line in enumerate(content.splitlines(), 1):
            if pattern.search(line):
                hits.append((file, line_no, line.strip()))
    print(f"\n## {label}: {len(hits)} references")
    for file, line_no, line in hits[:80]:
        print(f"{file}:{line_no}: {line}")
    if len(hits) > 80:
        print(f"... {len(hits) - 80} more references omitted")

print("\nNEXT STEP")
print("Review app-owned call sites and lifecycle methods before writing any patch.")
print("Do not delete SDK packages wholesale: app initialization, mediation, or UI may depend on them.")

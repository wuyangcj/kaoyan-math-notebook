#!/usr/bin/env python3
"""Extract <script> contents from HTML and check JS syntax with node --check."""
import re
import subprocess
import sys
import os
import tempfile

HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(HTML_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"HTML file size: {len(content)} chars")

# Find all <script>...</script> blocks (non-greedy, multiline)
# Also handle <script type="..."> and <script src="...">
script_pattern = re.compile(r'<script(?:\s[^>]*)?>(.*?)</script>', re.DOTALL | re.IGNORECASE)
scripts = script_pattern.findall(content)

print(f"Found {len(scripts)} <script> blocks")

total_inline_size = 0
has_error = False
error_details = []

for i, script in enumerate(scripts):
    script_stripped = script.strip()
    if not script_stripped:
        continue
    # Skip scripts that are just src references (empty inline)
    total_inline_size += len(script_stripped)
    # Write to temp file and check
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as tmp:
        tmp.write(script_stripped)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            ['node', '--check', tmp_path],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            has_error = True
            # Get error location
            error_details.append(f"Script block #{i+1} (size={len(script_stripped)} chars) FAILED:\n{result.stderr}\n")
            # Show first/last 200 chars for context
            preview_start = script_stripped[:200]
            preview_end = script_stripped[-200:]
            error_details.append(f"  Start: {preview_start!r}\n  End: {preview_end!r}\n")
        else:
            print(f"Script block #{i+1}: OK (size={len(script_stripped)} chars)")
    except subprocess.TimeoutExpired:
        has_error = True
        error_details.append(f"Script block #{i+1} TIMEOUT\n")
    finally:
        os.unlink(tmp_path)

print(f"\nTotal inline JS size: {total_inline_size} chars")
if has_error:
    print("\n=== SYNTAX ERRORS FOUND ===")
    for detail in error_details:
        print(detail)
    sys.exit(1)
else:
    print("\n✅ ALL JS SYNTAX OK")
    sys.exit(0)

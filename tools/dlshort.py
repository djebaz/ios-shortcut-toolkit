#!/usr/bin/env python3
"""Download the unsigned plist behind a public iCloud Shortcut link.

Usage:
    python3 dlshort.py <shortcut-id-or-icloud-url> [output-directory]

Outputs:
    <name>.plist        Raw unsigned binary plist
    <name>.xml          Readable XML plist
    <name>.record.json  Raw iCloud record metadata
"""

from __future__ import annotations

import json
import os
import plistlib
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


API = "https://www.icloud.com/shortcuts/api/records/"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/17.0 Safari/605.1.15"
)


def http_get(url: str, timeout: int = 60) -> bytes:
    """Download raw bytes with a Safari-like user agent."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def extract_id(value: str) -> str:
    """Extract a 32-character Shortcut record ID from an ID or iCloud URL."""
    match = re.search(r"([0-9a-fA-F]{32}|[0-9a-fA-F-]{36})", value.strip())
    if not match:
        raise ValueError(f"Could not find a Shortcut ID in: {value!r}")
    return match.group(1).replace("-", "").lower()


def safe_name(value: str) -> str:
    """Convert a shared Shortcut name into a filesystem-safe base name."""
    cleaned = re.sub(r"[^\w\s.-]", "", value, flags=re.UNICODE).strip()
    return re.sub(r"\s+", "_", cleaned) or "shortcut"


def fetch_record(shortcut_id: str) -> dict:
    """Fetch and decode the iCloud Shortcut record."""
    try:
        return json.loads(http_get(API + shortcut_id))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"iCloud API returned HTTP {exc.code}. "
            "The link may be private, deleted, or invalid."
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    try:
        shortcut_id = extract_id(sys.argv[1])
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    outdir = Path(os.path.expanduser(sys.argv[2])) if len(sys.argv) > 2 else Path(".")
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"Querying iCloud record {shortcut_id} ...")

    try:
        record = fetch_record(shortcut_id)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    fields = record.get("fields", {})
    if "shortcut" not in fields:
        print(
            "Error: record does not contain fields.shortcut. "
            f"Available keys: {', '.join(fields)}",
            file=sys.stderr,
        )
        return 1

    name = fields.get("name", {}).get("value", "shortcut")
    asset = fields["shortcut"]["value"]
    expected_size = asset.get("size")
    download_url = asset["downloadURL"].replace("${f}", "s.plist")

    base = outdir / safe_name(name)

    with open(str(base) + ".record.json", "w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"Name: {name}")
    print(f"Signing status: {fields.get('signingStatus', {}).get('value', '?')}")
    print(f"Expected size: {expected_size or '?'} bytes")
    print("Downloading unsigned plist ...")

    try:
        data = http_get(download_url)
    except urllib.error.HTTPError as exc:
        print(
            f"Error: download returned HTTP {exc.code}. "
            "The temporary asset URL may have expired. Run the script again.",
            file=sys.stderr,
        )
        return 1

    if expected_size and len(data) != expected_size:
        print(
            f"Warning: received {len(data)} bytes, expected {expected_size}.",
            file=sys.stderr,
        )

    try:
        workflow = plistlib.loads(data)
    except Exception as exc:
        print(f"Error: downloaded asset is not a valid plist: {exc}", file=sys.stderr)
        return 1

    if not isinstance(workflow, dict):
        print("Error: plist root is not a dictionary.", file=sys.stderr)
        return 1

    with open(str(base) + ".plist", "wb") as handle:
        handle.write(data)

    with open(str(base) + ".xml", "wb") as handle:
        plistlib.dump(workflow, handle, fmt=plistlib.FMT_XML, sort_keys=False)

    actions = workflow.get("WFWorkflowActions", [])
    print(f"Downloaded {len(data)} bytes, {len(actions)} actions.")
    print(f"  {base}.plist")
    print(f"  {base}.xml")
    print(f"  {base}.record.json")

    print("\nActions:")
    for index, action in enumerate(actions, start=1):
        identifier = action.get("WFWorkflowActionIdentifier", "?")
        short = identifier.replace("is.workflow.actions.", "")
        print(f"  {index:3d}. {short}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

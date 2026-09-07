#!/usr/bin/env python3
"""Sign an unsigned Shortcut using RoutineHub's HubSign service (cross-platform).

This provides an alternative to Apple's macOS-only `shortcuts sign` CLI.
The service is maintained by the RoutineHub community.

Usage:
    python3 sign_shortcut_hubsign.py INPUT.shortcut OUTPUT.shortcut

Requirements:
    - Python 3.7+ (standard library only)
    - Active internet connection
    - Compliance with RoutineHub service terms

The signed output will begin with AEA1 magic bytes and can be imported on iOS.
"""

from __future__ import annotations

import argparse
import json
import plistlib
import sys
import urllib.error
import urllib.request
from pathlib import Path

HUBSIGN_API = "https://hubsign.routinehub.services/sign"
USER_AGENT = "ios-shortcut-toolkit/1.0"
AEA1_MAGIC = b"AEA1"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Sign shortcuts using RoutineHub HubSign service"
    )
    parser.add_argument("input", help="Unsigned .shortcut file")
    parser.add_argument("output", help="Output path for signed .shortcut")
    parser.add_argument(
        "--name",
        help="Shortcut name (extracted from plist if not provided)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Request timeout in seconds (default: 60)",
    )
    return parser.parse_args()


def load_shortcut(path: Path) -> tuple[dict, bytes]:
    """Load shortcut plist and return both parsed dict and XML bytes."""
    with open(path, "rb") as handle:
        plist_data = handle.read()
        workflow = plistlib.loads(plist_data)

    if not isinstance(workflow, dict):
        raise ValueError("Shortcut root must be a dictionary.")

    # Convert to XML format for HubSign API
    xml_data = plistlib.dumps(workflow, fmt=plistlib.FMT_XML)
    return workflow, xml_data


def sign_with_hubsign(
    name: str,
    xml_plist: bytes,
    timeout: int = 60,
) -> bytes:
    """Send shortcut to HubSign API and return signed binary."""
    payload = {
        "shortcutName": name,
        "shortcut": xml_plist.decode("utf-8"),
    }

    request = urllib.request.Request(
        HUBSIGN_API,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"HubSign API returned HTTP {exc.code}.\n"
            f"Response: {error_body}\n"
            "The service may be unavailable or the shortcut may be invalid."
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Network error connecting to HubSign: {exc.reason}"
        ) from exc


def verify_signature(data: bytes) -> bool:
    """Check if the signed shortcut begins with AEA1 magic bytes."""
    return data.startswith(AEA1_MAGIC)


def main() -> int:
    """Sign a shortcut using HubSign and verify the result."""
    args = parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file does not exist: {input_path}", file=sys.stderr)
        return 1

    print(f"Loading unsigned shortcut: {input_path}")
    try:
        workflow, xml_data = load_shortcut(input_path)
    except Exception as exc:
        print(f"Error loading shortcut: {exc}", file=sys.stderr)
        return 1

    # Extract or use provided name
    shortcut_name = args.name or workflow.get("WFWorkflowName", input_path.stem)
    print(f"Shortcut name: {shortcut_name}")

    print(f"Sending to HubSign API ({HUBSIGN_API}) ...")
    try:
        signed_data = sign_with_hubsign(shortcut_name, xml_data, args.timeout)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    # Verify signature
    if not verify_signature(signed_data):
        print(
            "Warning: signed shortcut does not begin with AEA1 magic bytes.",
            file=sys.stderr,
        )
        print("The file may not be properly signed.", file=sys.stderr)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(signed_data)

    print(f"Signed shortcut written to: {output_path}")
    print(f"Size: {len(signed_data)} bytes")
    print(f"Header: {signed_data[:4].hex().upper()} ({'valid' if verify_signature(signed_data) else 'INVALID'})")
    print("\nImport on iOS: open the file with the Shortcuts app.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

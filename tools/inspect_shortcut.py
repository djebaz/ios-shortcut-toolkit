#!/usr/bin/env python3
"""Inspect a Shortcut plist and optionally export its action array as a JSON spec."""

from __future__ import annotations

import argparse
from pathlib import Path

from shortcut_plist import dump_json, load_plist


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("shortcut", help="Binary/XML plist or unsigned .shortcut file")
    parser.add_argument(
        "--spec-out",
        help="Write an editable generator spec containing the current action array",
    )
    return parser.parse_args()


def main() -> int:
    """Print workflow information and optionally export a generator spec."""
    args = parse_args()
    workflow = load_plist(args.shortcut)
    actions = workflow.get("WFWorkflowActions", [])

    print(f"File: {Path(args.shortcut)}")
    print(f"Root keys: {len(workflow)}")
    print(f"Actions: {len(actions) if isinstance(actions, list) else 'invalid'}")

    if isinstance(actions, list):
        for index, action in enumerate(actions, start=1):
            if isinstance(action, dict):
                identifier = action.get("WFWorkflowActionIdentifier", "?")
            else:
                identifier = "<invalid action>"
            print(f"{index:3d}. {identifier}")

    if args.spec_out:
        if not isinstance(actions, list):
            raise ValueError("WFWorkflowActions is not a list.")

        spec = {
            "workflow_overrides": {},
            "actions": actions,
        }
        dump_json(spec, args.spec_out)
        print(f"\nWrote editable spec: {args.spec_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

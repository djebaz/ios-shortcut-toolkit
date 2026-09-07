#!/usr/bin/env python3
"""Perform basic structural validation on a Shortcut plist."""

from __future__ import annotations

import argparse

from shortcut_plist import load_plist, validate_workflow


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("shortcut", help="Binary/XML plist or unsigned .shortcut file")
    return parser.parse_args()


def main() -> int:
    """Validate the workflow and print its action identifiers."""
    args = parse_args()

    try:
        workflow = load_plist(args.shortcut)
    except Exception as exc:
        print(f"INVALID: could not parse plist: {exc}")
        return 1

    errors = validate_workflow(workflow)
    if errors:
        print("INVALID:")
        for error in errors:
            print(f"- {error}")
        return 1

    actions = workflow["WFWorkflowActions"]
    print("VALID: basic plist/workflow structure passed.")
    print(f"Actions: {len(actions)}")

    for index, action in enumerate(actions, start=1):
        print(f"{index:3d}. {action['WFWorkflowActionIdentifier']}")

    print(
        "\nNote: this is structural validation only. "
        "Apple signing/import and an execution smoke test are still required."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

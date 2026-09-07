#!/usr/bin/env python3
"""Build an unsigned Shortcut by applying an action spec to a donor workflow.

This tool intentionally requires a donor Shortcut/plist. It preserves the donor's
known-valid workflow-level metadata and replaces only the action graph plus any
explicit root overrides provided by the spec.
"""

from __future__ import annotations

import argparse
import copy
from pathlib import Path

from shortcut_plist import (
    load_json,
    load_plist,
    resolve_uuid_placeholders,
    validate_workflow,
    write_binary_plist,
    write_xml_plist,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--donor", required=True, help="Known-good donor .shortcut/.plist")
    parser.add_argument("--spec", required=True, help="JSON workflow specification")
    parser.add_argument("--output", required=True, help="Unsigned output .shortcut path")
    parser.add_argument(
        "--xml-debug",
        help="Optional readable XML debug copy of the generated workflow",
    )
    return parser.parse_args()


def main() -> int:
    """Build, validate, and serialize the unsigned Shortcut."""
    args = parse_args()

    donor = load_plist(args.donor)
    spec = load_json(args.spec)

    if not isinstance(spec, dict):
        raise ValueError("Spec root must be a JSON object.")

    actions = spec.get("actions")
    if not isinstance(actions, list):
        raise ValueError("Spec must contain an 'actions' array.")

    overrides = spec.get("workflow_overrides", {})
    if not isinstance(overrides, dict):
        raise ValueError("'workflow_overrides' must be an object.")

    workflow = copy.deepcopy(donor)

    for key, value in overrides.items():
        workflow[key] = value

    workflow["WFWorkflowActions"] = actions
    workflow = resolve_uuid_placeholders(workflow)

    errors = validate_workflow(workflow)
    if errors:
        detail = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"Generated workflow failed structural validation:\n{detail}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_binary_plist(workflow, output_path)

    if args.xml_debug:
        xml_path = Path(args.xml_debug)
        xml_path.parent.mkdir(parents=True, exist_ok=True)
        write_xml_plist(workflow, xml_path)

    print(f"Wrote unsigned Shortcut: {output_path}")
    print(f"Actions: {len(workflow['WFWorkflowActions'])}")
    if args.xml_debug:
        print(f"Wrote XML debug copy: {args.xml_debug}")
    print("Next step on macOS: validate, then sign with Apple's shortcuts CLI.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Shared plist helpers for the iOS Shortcut toolkit."""

from __future__ import annotations

import base64
import datetime as dt
import json
import plistlib
import re
import uuid
from pathlib import Path
from typing import Any


UUID_PLACEHOLDER_RE = re.compile(r"\{\{UUID:([A-Za-z0-9_.:-]+)\}\}")


def load_plist(path: str | Path) -> dict[str, Any]:
    """Load a binary or XML plist and require a dictionary root."""
    with open(path, "rb") as handle:
        value = plistlib.load(handle)
    if not isinstance(value, dict):
        raise ValueError("Shortcut plist root must be a dictionary.")
    return value


def write_binary_plist(value: dict[str, Any], path: str | Path) -> None:
    """Write a dictionary as a binary plist."""
    with open(path, "wb") as handle:
        plistlib.dump(value, handle, fmt=plistlib.FMT_BINARY, sort_keys=False)


def write_xml_plist(value: dict[str, Any], path: str | Path) -> None:
    """Write a dictionary as a readable XML plist."""
    with open(path, "wb") as handle:
        plistlib.dump(value, handle, fmt=plistlib.FMT_XML, sort_keys=False)


def encode_json_value(value: Any) -> Any:
    """Encode plist-only value types into explicit JSON wrapper objects."""
    if isinstance(value, bytes):
        return {
            "$plist": "data",
            "base64": base64.b64encode(value).decode("ascii"),
        }
    if isinstance(value, dt.datetime):
        return {
            "$plist": "date",
            "iso8601": value.isoformat(),
        }
    if isinstance(value, dict):
        return {str(key): encode_json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [encode_json_value(item) for item in value]
    if isinstance(value, tuple):
        return [encode_json_value(item) for item in value]
    return value


def decode_json_value(value: Any) -> Any:
    """Decode JSON wrapper objects back to plist-compatible Python values."""
    if isinstance(value, dict):
        marker = value.get("$plist")
        if marker == "data":
            payload = value.get("base64")
            if not isinstance(payload, str):
                raise ValueError("Invalid plist data wrapper.")
            return base64.b64decode(payload)
        if marker == "date":
            payload = value.get("iso8601")
            if not isinstance(payload, str):
                raise ValueError("Invalid plist date wrapper.")
            return dt.datetime.fromisoformat(payload)
        return {key: decode_json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [decode_json_value(item) for item in value]
    return value


def dump_json(value: Any, path: str | Path) -> None:
    """Write a plist-aware JSON representation."""
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(encode_json_value(value), handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def load_json(path: str | Path) -> Any:
    """Load JSON and restore plist-specific wrapped values."""
    with open(path, "r", encoding="utf-8") as handle:
        return decode_json_value(json.load(handle))


def resolve_uuid_placeholders(value: Any) -> Any:
    """Replace {{UUID:name}} placeholders with stable fresh uppercase UUIDs."""
    generated: dict[str, str] = {}

    def get_uuid(name: str) -> str:
        if name not in generated:
            generated[name] = str(uuid.uuid4()).upper()
        return generated[name]

    def walk(node: Any) -> Any:
        if isinstance(node, dict):
            return {key: walk(item) for key, item in node.items()}
        if isinstance(node, list):
            return [walk(item) for item in node]
        if isinstance(node, str):
            full = UUID_PLACEHOLDER_RE.fullmatch(node)
            if full:
                return get_uuid(full.group(1))

            def replace(match: re.Match[str]) -> str:
                return get_uuid(match.group(1))

            return UUID_PLACEHOLDER_RE.sub(replace, node)
        return node

    return walk(value)


def validate_workflow(workflow: dict[str, Any]) -> list[str]:
    """Return structural validation errors for a Shortcut workflow."""
    errors: list[str] = []

    actions = workflow.get("WFWorkflowActions")
    if actions is None:
        errors.append("Missing WFWorkflowActions.")
        return errors
    if not isinstance(actions, list):
        errors.append("WFWorkflowActions must be a list.")
        return errors

    for index, action in enumerate(actions, start=1):
        prefix = f"Action {index}"
        if not isinstance(action, dict):
            errors.append(f"{prefix}: action must be a dictionary.")
            continue

        identifier = action.get("WFWorkflowActionIdentifier")
        if not isinstance(identifier, str) or not identifier.strip():
            errors.append(f"{prefix}: missing or invalid WFWorkflowActionIdentifier.")

        if "WFWorkflowActionParameters" in action:
            parameters = action["WFWorkflowActionParameters"]
            if not isinstance(parameters, dict):
                errors.append(
                    f"{prefix}: WFWorkflowActionParameters must be a dictionary."
                )

    return errors

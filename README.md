# iOS Shortcut Toolkit

Programmatically extract, inspect, generate, validate, and sign iOS Shortcuts using a donor-based approach.

## Quick Start

### Extract a public shortcut
```bash
python3 tools/dlshort.py https://www.icloud.com/shortcuts/<ID> ./output
```

### Inspect shortcut structure
```bash
python3 tools/inspect_shortcut.py output/MyShortcut.shortcut
```

### Generate a new shortcut
```bash
python3 tools/build_shortcut.py \
  --donor Donor.shortcut \
  --spec workflow_spec.json \
  --output Generated.shortcut
```

### Validate structure
```bash
python3 tools/validate_shortcut.py Generated.shortcut
```

### Sign (macOS only)
```bash
./tools/sign_shortcut.sh Generated.shortcut Signed.shortcut
```

## Philosophy

> Don't pretend the complete Apple Shortcut plist format is a stable public authoring API.

Use a known-good exported Shortcut as the donor/template, preserve its valid workflow-level metadata, and replace only the parts you understand.

This makes the workflow much more reliable than inventing an entire `.shortcut` structure from scratch.

## Tools

| Tool | Purpose |
|------|---------|
| `dlshort.py` | Download shortcuts from public iCloud URLs |
| `inspect_shortcut.py` | Inspect action structure and export specs |
| `build_shortcut.py` | Generate shortcuts from donor + spec |
| `validate_shortcut.py` | Structural validation |
| `sign_shortcut.sh` | Sign with Apple's macOS shortcuts CLI |
| `shortcut_plist.py` | Shared plist utilities |

## Workflow

```
Known Working Shortcut
        ↓
Extract with dlshort.py
        ↓
Inspect actions and structure
        ↓
Edit workflow spec JSON
        ↓
Build from donor + spec
        ↓
Validate structure
        ↓
Sign with Apple tooling (macOS)
        ↓
Import and smoke test
```

## Documentation

- **[Toolkit Guide](devdocs/toolkit-guide.md)** - Comprehensive guide covering extraction, plist structure, UUID placeholders, validation, signing, and full end-to-end workflows
- **[AGENTS.md](AGENTS.md)** - Guide for Claude Code agents working with this toolkit

## Requirements

- Python 3.7+ (no external dependencies)
- macOS with `shortcuts` CLI (for signing only)

## License

MIT

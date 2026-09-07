# Agent Guide: iOS Shortcut Toolkit

This guide helps Claude Code agents work effectively with the iOS Shortcut Toolkit.

## Core Philosophy

**CRITICAL:** Apple does not publish the complete Shortcut plist format. This toolkit uses a **donor-based approach**:

1. Extract a known-good shortcut
2. Preserve its valid workflow metadata
3. Replace only the action graph (`WFWorkflowActions`)
4. Validate, sign, and test

**DO NOT** attempt to generate shortcuts from scratch without a donor template.

## Repository Structure

```
ios-shortcut-toolkit/
├── devdocs/
│   └── toolkit-guide.md       Comprehensive reference (689 lines)
├── tools/
│   ├── shortcut_plist.py      Shared utilities (UUID placeholders, plist I/O)
│   ├── dlshort.py             Extract shortcuts from iCloud URLs
│   ├── inspect_shortcut.py    Inspect and export action specs
│   ├── build_shortcut.py      Generate shortcuts from donor + spec
│   ├── validate_shortcut.py   Structural validation
│   └── sign_shortcut.sh       Sign shortcuts (macOS only)
└── examples/
    └── workflow_spec.example.json
```

## Common Tasks

### Task: Extract and analyze an existing shortcut

```bash
# Download from public iCloud URL
python3 tools/dlshort.py https://www.icloud.com/shortcuts/<ID> ./output

# Inspect actions
python3 tools/inspect_shortcut.py output/Shortcut_Name.shortcut

# Export editable spec
python3 tools/inspect_shortcut.py output/Shortcut_Name.shortcut --spec-out spec.json
```

**Output files:**
- `Shortcut_Name.plist` - Binary plist
- `Shortcut_Name.xml` - Readable XML plist
- `Shortcut_Name.record.json` - iCloud metadata

### Task: Generate a new shortcut

```bash
# Build from donor + spec
python3 tools/build_shortcut.py \
  --donor Donor.shortcut \
  --spec workflow_spec.json \
  --output Generated.shortcut \
  --xml-debug Generated.xml

# Validate
python3 tools/validate_shortcut.py Generated.shortcut
```

**Requirements:**
- A donor `.shortcut` file (known-good template)
- A spec JSON with `actions` array and optional `workflow_overrides`

### Task: Sign a shortcut (macOS only)

```bash
# Sign with default mode (anyone)
./tools/sign_shortcut.sh Generated.shortcut Signed.shortcut

# Or specify mode
./tools/sign_shortcut.sh Generated.shortcut Signed.shortcut people-who-know-me
```

**Important:** Signing requires macOS with Apple's `shortcuts` CLI installed.

## Workflow Spec Format

```json
{
  "workflow_overrides": {},
  "actions": [
    {
      "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
      "WFWorkflowActionParameters": {
        "WFTextActionText": "Hello, World!",
        "UUID": "{{UUID:output1}}"
      }
    },
    {
      "WFWorkflowActionIdentifier": "is.workflow.actions.showresult",
      "WFWorkflowActionParameters": {
        "Text": "{{UUID:output1}}"
      }
    }
  ]
}
```

### UUID Placeholders

Use `{{UUID:name}}` to generate and reuse UUIDs across actions:
- All references to `{{UUID:name}}` get the same generated UUID
- UUIDs are uppercase format: `A1B2C3D4-E5F6-7890-ABCD-EF1234567890`
- Useful for connecting action outputs and variable references

## Key Limitations

### 1. No comprehensive action catalog

Apple doesn't publish action schemas. To learn action structures:
1. Create a minimal shortcut in Apple's Shortcuts app with the desired action
2. Export/share it
3. Extract with `dlshort.py`
4. Inspect with `inspect_shortcut.py`
5. Copy the action structure into your spec

### 2. Structural validation only

`validate_shortcut.py` checks:
- File parses as plist
- `WFWorkflowActions` exists and is a list
- Actions have `WFWorkflowActionIdentifier`
- Parameters are dictionaries

**It CANNOT validate:**
- Semantic correctness of parameters
- Variable reference validity
- Whether Apple will accept it during signing
- Whether it will execute successfully

### 3. Signing requires macOS

The `sign_shortcut.sh` wrapper requires:
- macOS operating system
- Apple's `shortcuts` CLI tool
- Apple account authentication

Unsigned shortcuts can be generated on any platform, but final signing requires macOS.

## Action Development Loop

For each new action type:

1. **Create minimal donor** - Build a tiny shortcut in Shortcuts app with just that action
2. **Export and extract** - Share it, download with `dlshort.py`
3. **Inspect structure** - Use `inspect_shortcut.py --spec-out`
4. **Document parameters** - Note required/optional fields
5. **Copy to your spec** - Adapt the action dictionary
6. **Use UUID placeholders** - Replace hardcoded UUIDs with `{{UUID:name}}`
7. **Build and validate** - Generate and check structure
8. **Sign and test** - Sign on macOS, import, smoke test

**Never** reverse-engineer complex shortcuts all at once. Build action knowledge incrementally.

## File Handling

### Python tools expect UTF-8
All Python scripts use UTF-8 encoding for JSON I/O.

### Plist formats
- Binary plist (`.plist`, `.shortcut`) - compact, not human-readable
- XML plist (`.xml`) - readable debug format
- Both are valid input to all tools

### Generated artifacts
`.gitignore` excludes:
- `*.shortcut` (except in `examples/`)
- `*.plist`
- `*.xml`
- `*.record.json`

Committed specs should be JSON only, with donors documented but not necessarily checked in.

## Error Handling

### Common errors

**"Could not find a Shortcut ID"**
- Check the iCloud URL format
- Ensure the shortcut is publicly shared

**"iCloud API returned HTTP 404"**
- Shortcut may be private, deleted, or link expired
- Verify the URL is accessible in a browser

**"Spec must contain an 'actions' array"**
- Workflow spec JSON must have `"actions": [...]` at root level

**"Generated workflow failed structural validation"**
- Check each action has `WFWorkflowActionIdentifier`
- Ensure `WFWorkflowActionParameters` is a dictionary (not array/string)
- Review error details in output

**"Apple Shortcut signing requires macOS"**
- Signing only works on macOS with `shortcuts` CLI
- Generate unsigned shortcuts on any platform, transfer to macOS for signing

## Best Practices for Agents

### 1. Always read the full toolkit guide first
The comprehensive guide is in `devdocs/toolkit-guide.md`. Read it before attempting to:
- Generate shortcuts
- Explain the workflow
- Debug validation errors

### 2. Use donors for everything
Never invent shortcut structure from scratch. Always:
- Start with a real exported shortcut
- Preserve donor metadata
- Only modify `WFWorkflowActions`

### 3. Validate before signing
Always run `validate_shortcut.py` before attempting to sign. Structural errors will cause signing to fail.

### 4. Acknowledge limitations
When users ask about generating shortcuts:
- Explain the donor-based approach
- Note that action schemas aren't publicly documented
- Guide them through the extract → inspect → adapt workflow

### 5. Test incrementally
Build and test one action at a time, not entire complex workflows.

## Documentation References

- **Full workflow:** `devdocs/toolkit-guide.md` §15 (end-to-end diagram)
- **Plist structure:** `devdocs/toolkit-guide.md` §3
- **UUID placeholders:** `devdocs/toolkit-guide.md` §8
- **Donor philosophy:** `devdocs/toolkit-guide.md` §9
- **Action development:** `devdocs/toolkit-guide.md` §10
- **Validation scope:** `devdocs/toolkit-guide.md` §11
- **Signing process:** `devdocs/toolkit-guide.md` §13

## Platform Notes

**Windows:**
- All Python tools work
- Cannot sign shortcuts (macOS only)
- Use WSL or forward unsigned shortcuts to macOS for signing

**Linux:**
- All Python tools work
- Cannot sign shortcuts (macOS only)

**macOS:**
- Full toolkit support including signing
- `shortcuts` CLI available in recent macOS versions
- Check `shortcuts sign --help` for documentation

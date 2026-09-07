# iOS Shortcut Extract

Extract, inspect, and reverse-engineer iOS Shortcuts from public iCloud URLs. Build a library of donor shortcuts and document action structures incrementally.

## When to Use This Skill

Use this skill when you need to:
- Download an iOS Shortcut from a public iCloud URL
- Inspect the structure and actions of an existing shortcut
- Export action specifications for reuse or modification
- Reverse-engineer shortcut actions to learn their parameter schemas
- Build a donor library for future shortcut generation

## Prerequisites

- Python 3.7+ (standard library only, no external dependencies)
- Public iCloud shortcut URL (format: `https://www.icloud.com/shortcuts/<ID>`)
- Output directory for extracted files

## Workflow

### Step 1: Extract from iCloud URL

Download the unsigned shortcut plist from a public iCloud URL:

```bash
python3 tools/dlshort.py https://www.icloud.com/shortcuts/<SHORTCUT_ID> ./output
```

**Output files:**
- `<name>.plist` - Binary plist (unsigned shortcut)
- `<name>.xml` - Readable XML representation
- `<name>.record.json` - iCloud metadata

**Common errors:**
- "Could not find a Shortcut ID" → Invalid URL format or missing ID
- "HTTP 404" → Shortcut is private, deleted, or URL expired
- "Network error" → Check internet connection

### Step 2: Inspect Shortcut Structure

View the action list and workflow structure:

```bash
python3 tools/inspect_shortcut.py output/<name>.shortcut
```

This displays:
- Number of root keys in the workflow
- Total action count
- Ordered list of action identifiers

### Step 3: Export Editable Spec (Optional)

Export the action array as an editable JSON spec:

```bash
python3 tools/inspect_shortcut.py output/<name>.shortcut --spec-out spec.json
```

The exported spec contains:
```json
{
  "workflow_overrides": {},
  "actions": [
    {
      "WFWorkflowActionIdentifier": "...",
      "WFWorkflowActionParameters": { ... }
    }
  ]
}
```

You can now:
- Study action parameter schemas
- Copy action structures into new specs
- Modify parameters for new shortcuts
- Document patterns for the action library

## Understanding Action Identifiers

Action identifiers follow reverse domain name notation:

**Apple workflow actions (most common):**
- `is.workflow.actions.gettext` - Get text
- `is.workflow.actions.showresult` - Show result
- `is.workflow.actions.detect.dictionary` - Get dictionary from input
- `is.workflow.actions.documentpicker.open` - Open file picker
- `is.workflow.actions.runshellscript` - Run shell script

**Third-party app actions:**
- `com.apple.mobilephone.call` - Make phone call
- `com.apple.mobilenotes.SharingExtension` - Save to Notes
- Custom app integrations

## Action Development Strategy

To learn a new action type:

1. **Create minimal donor** - Build a tiny shortcut in Apple's Shortcuts app with just the target action
2. **Share and download** - Export it to iCloud, copy the public URL
3. **Extract** - Use `dlshort.py` to download the unsigned plist
4. **Inspect** - Use `inspect_shortcut.py --spec-out` to export the action structure
5. **Document** - Note the action identifier and required/optional parameters
6. **Build library** - Save the action spec for reuse in future shortcuts

**Never** try to reverse-engineer large complex shortcuts all at once. Build knowledge action-by-action.

## Organizing Donor Library

Recommended structure:

```
donors/
├── basic-actions/
│   ├── get-text.shortcut
│   ├── show-result.shortcut
│   └── set-variable.shortcut
├── file-operations/
│   ├── open-file.shortcut
│   └── save-file.shortcut
└── specs/
    ├── get-text-spec.json
    ├── show-result-spec.json
    └── README.md (document learned patterns)
```

## Key Limitations to Remember

1. **No comprehensive action catalog exists** - Apple doesn't publish action schemas. Every action must be learned by extracting real shortcuts.

2. **Actions can change** - iOS updates may modify action parameters or add new actions. Always extract from current iOS version.

3. **Private shortcuts are inaccessible** - Only public iCloud-shared shortcuts can be downloaded. You cannot extract private shortcuts or shortcuts from other devices.

4. **Parameter schemas are undocumented** - The toolkit shows you what parameters exist in a real shortcut, but cannot tell you all possible parameters or valid value ranges.

## Important Files

- `tools/dlshort.py` - Downloader (157 lines, Python 3.7+)
- `tools/inspect_shortcut.py` - Inspector (56 lines)
- `tools/shortcut_plist.py` - Shared utilities (152 lines)
- `devdocs/toolkit-guide.md` - Comprehensive reference (§2: extraction, §3: plist structure, §10: action development)

## Next Steps After Extraction

After extracting and inspecting a shortcut, you can:

1. **Use as a donor** - Use the extracted shortcut as a template for `ios-shortcut-build` skill
2. **Copy action structures** - Adapt action dictionaries into new workflow specs
3. **Document patterns** - Record learned action schemas for your reference library
4. **Build on knowledge** - Use extracted specs to understand how actions connect via UUIDs

## Example: Complete Extraction Workflow

```bash
# 1. Download from iCloud
python3 tools/dlshort.py \
  https://www.icloud.com/shortcuts/abc123 \
  ./donors/basic-actions

# Output:
# Name: Get Text Example
# Downloaded 1234 bytes, 2 actions.
#   donors/basic-actions/Get_Text_Example.plist
#   donors/basic-actions/Get_Text_Example.xml
#   donors/basic-actions/Get_Text_Example.record.json

# 2. Inspect structure
python3 tools/inspect_shortcut.py \
  donors/basic-actions/Get_Text_Example.shortcut

# Output:
# File: donors/basic-actions/Get_Text_Example.shortcut
# Root keys: 15
# Actions: 2
#   1. is.workflow.actions.gettext
#   2. is.workflow.actions.showresult

# 3. Export editable spec
python3 tools/inspect_shortcut.py \
  donors/basic-actions/Get_Text_Example.shortcut \
  --spec-out donors/specs/get-text-example-spec.json

# Now edit spec.json to adapt or document the action structure
```

## Pro Tips

1. **Start simple** - Extract minimal shortcuts with 1-2 actions to learn individual action structures
2. **Name donors clearly** - Use descriptive names that indicate what action patterns they demonstrate
3. **Document as you go** - Create a reference doc noting which actions you've learned and their key parameters
4. **Version awareness** - Note the iOS version when extracting, as actions may evolve
5. **Backup donors** - Keep extracted donors in version control or backup storage

## References

- Full extraction workflow: `devdocs/toolkit-guide.md` §2
- Plist structure details: `devdocs/toolkit-guide.md` §3
- Action development loop: `devdocs/toolkit-guide.md` §10
- Shortcut as donor template: `devdocs/toolkit-guide.md` §4

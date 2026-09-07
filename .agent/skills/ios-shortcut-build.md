# iOS Shortcut Build

Generate, validate, and sign iOS Shortcuts using the donor-based approach. Build new shortcuts from known-good templates while preserving valid workflow metadata.

## When to Use This Skill

Use this skill when you need to:
- Generate a new shortcut from a donor template + action spec
- Validate shortcut structure before signing
- Sign shortcuts for iOS import (macOS CLI or cross-platform HubSign)
- Test shortcuts through the complete build → sign → import workflow
- Create programmatically-generated shortcuts that iOS will accept

## Prerequisites

- Python 3.7+ (standard library only, no external dependencies)
- A donor `.shortcut` file (known-good template from real iOS export)
- A workflow spec JSON file with action definitions
- For signing:
  - **macOS:** Apple's `shortcuts` CLI tool
  - **Windows/Linux:** Internet connection (RoutineHub HubSign)

## Core Philosophy

**CRITICAL:** Never generate shortcuts from scratch. Always use a donor-based approach:

1. Start with a real exported shortcut (donor template)
2. Preserve its valid workflow-level metadata
3. Replace only the action graph (`WFWorkflowActions`)
4. Validate structure
5. Sign with Apple tooling or HubSign
6. Import and smoke test on iOS

This approach is much more reliable than inventing the entire `.shortcut` plist structure.

## Workflow

### Step 1: Prepare Donor and Spec

**Donor shortcut:**
- Must be a real exported `.shortcut` file from Apple's Shortcuts app
- Should have similar complexity to your target shortcut
- Provides valid workflow metadata that will be preserved

**Workflow spec (JSON):**
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

### Step 2: Build Unsigned Shortcut

Generate the unsigned shortcut from donor + spec:

```bash
python tools/build_shortcut.py \
  --donor donors/basic-donor.shortcut \
  --spec specs/my-workflow.json \
  --output generated/MyShortcut.shortcut \
  --xml-debug generated/MyShortcut.xml
```

**What happens:**
1. Loads donor plist and preserves its workflow metadata
2. Applies optional `workflow_overrides` from spec
3. Replaces `WFWorkflowActions` with spec actions
4. Resolves `{{UUID:name}}` placeholders to consistent UUIDs
5. Validates workflow structure
6. Writes unsigned binary plist
7. Optionally writes XML debug copy

**Output:**
```
Wrote unsigned Shortcut: generated/MyShortcut.shortcut
Actions: 2
Wrote XML debug copy: generated/MyShortcut.xml
Next step on macOS: validate, then sign with Apple's shortcuts CLI.
```

### Step 3: Validate Structure

Run structural validation before signing:

```bash
python tools/validate_shortcut.py generated/MyShortcut.shortcut
```

**What it checks:**
- File parses as plist
- Root is a dictionary
- `WFWorkflowActions` exists and is a list
- Every action is a dictionary
- Every action has non-empty `WFWorkflowActionIdentifier`
- Action parameters (when present) are dictionaries

**Important:** This is structural validation only. It cannot verify:
- Semantic correctness of parameters
- Variable reference validity
- Whether Apple will accept it during signing
- Whether it will execute successfully

**Always validate before signing** - structural errors will cause signing to fail.

### Step 4: Sign the Shortcut

Two signing methods available:

#### Method 1: Apple's macOS CLI (Official, Local)

```bash
# Default mode (anyone can use)
./tools/sign_shortcut.sh \
  generated/MyShortcut.shortcut \
  generated/MyShortcut-signed.shortcut

# Or specify mode (people-who-know-me requires authentication)
./tools/sign_shortcut.sh \
  generated/MyShortcut.shortcut \
  generated/MyShortcut-signed.shortcut \
  people-who-know-me
```

**Requirements:**
- macOS operating system
- Apple's `shortcuts` CLI tool installed
- Apple account authentication

**Advantages:**
- Official Apple signing
- Local (no network required)
- Trusted by all iOS devices

#### Method 2: RoutineHub HubSign (Cross-platform, Remote)

```bash
# Sign via RoutineHub community service
python tools/sign_shortcut_hubsign.py \
  generated/MyShortcut.shortcut \
  generated/MyShortcut-signed.shortcut

# With custom name
python tools/sign_shortcut_hubsign.py \
  generated/MyShortcut.shortcut \
  generated/MyShortcut-signed.shortcut \
  --name "My Custom Name"
```

**Requirements:**
- Python 3.7+ (standard library only)
- Active internet connection
- Compliance with RoutineHub service terms

**How it works:**
1. POSTs unsigned plist to `https://hubsign.routinehub.services/sign`
2. Service signs remotely and returns signed binary
3. Automatic verification of AEA1 magic bytes
4. No macOS required

**Which to use:**
- macOS available → use Apple's official CLI (preferred)
- Windows/Linux or no macOS → use HubSign

**Verify signature:**
```bash
xxd -l 4 generated/MyShortcut-signed.shortcut
```

Expected output:
```
00000000: 4145 4131                             AEA1
```

The AEA1 magic bytes confirm proper signing.

### Step 5: Import and Test on iOS

Transfer the signed shortcut to your iOS device:
- AirDrop
- iCloud Drive
- Email attachment
- Direct USB transfer

Open the file on iOS:
```
Open in → Shortcuts
```

The Shortcuts app should present the import/add flow.

**Test the shortcut:**
1. Run it from the Shortcuts app
2. Verify it executes as expected
3. Check for errors or unexpected behavior
4. Test edge cases and error handling

**Full acceptance sequence:**
```
plist parses
  → structural validator passes
  → Apple/HubSign signer accepts
  → iOS Shortcuts imports
  → Shortcut executes correctly
```

## UUID Placeholder System

Use `{{UUID:name}}` in your spec to generate and reuse consistent UUIDs:

```json
{
  "actions": [
    {
      "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
      "WFWorkflowActionParameters": {
        "UUID": "{{UUID:first_action_output}}"
      }
    },
    {
      "WFWorkflowActionIdentifier": "is.workflow.actions.showresult",
      "WFWorkflowActionParameters": {
        "Text": "{{UUID:first_action_output}}"
      }
    }
  ]
}
```

**How it works:**
- All references to `{{UUID:first_action_output}}` get the same generated UUID
- UUIDs are uppercase format: `A1B2C3D4-E5F6-7890-ABCD-EF1234567890`
- Useful for connecting action outputs, variable references, and control-flow groups
- Placeholder names can contain: `A-Za-z0-9_.:-`

**Important:** The placeholder system only solves identity reuse. It does not tell you which action parameter keys Apple expects. Obtain correct parameter shapes from real extracted donor actions (see `ios-shortcut-extract` skill).

## Finding Action Identifiers and Parameters

### Quick Reference (Use with Caution)

The toolkit includes a community-maintained action catalog in `references/`:
- **`references/actions.md`** - 100+ actions organized by category with key parameters
- **`references/plist-format.md`** - Plist structure and control flow patterns
- **`references/url-schemes-and-cli.md`** - Shortcuts CLI and URL schemes

**Example from `references/actions.md`:**
```markdown
| Action | Identifier | Key Parameters |
|--------|-----------|----------------|
| Text | `is.workflow.actions.gettext` | `WFTextActionText` |
| Ask for Input | `is.workflow.actions.ask` | `WFAskActionPrompt`, `WFAskActionDefaultAnswer` |
```

### Recommended Workflow

**For each new action:**

1. **Check reference** - Look up the action in `references/actions.md` to get the identifier
2. **Create minimal donor** - Build a tiny shortcut in Shortcuts app with just that action
3. **Extract and inspect** - Use `ios-shortcut-extract` skill to get the real structure
4. **Compare** - Verify the reference against the real extracted structure
5. **Use the real structure** - Copy from the extracted shortcut, not the reference

**Why extract real shortcuts even with the reference?**
- Reference may be incomplete or outdated
- Real shortcuts include all Apple internal fields
- Variable references and UUIDs are correctly wired
- Guaranteed iOS compatibility

⚠️ **Use reference as guidance, validate with real shortcuts.**

## Workflow Overrides (Optional)

Use `workflow_overrides` to change root-level workflow metadata:

```json
{
  "workflow_overrides": {
    "WFWorkflowName": "My Custom Shortcut Name",
    "WFWorkflowMinimumClientVersion": 900
  },
  "actions": [ ... ]
}
```

**Use sparingly.** Most donor metadata should remain intact. Only override when you know the specific field is safe to change.

## Common Build Errors

**"Spec must contain an 'actions' array"**
- Workflow spec JSON must have `"actions": [...]` at root level
- Check JSON syntax and structure

**"Generated workflow failed structural validation"**
- Each action must have `WFWorkflowActionIdentifier`
- `WFWorkflowActionParameters` must be a dictionary (not array/string)
- Review detailed error output for specific issues

**"Could not parse plist"**
- Donor file may be corrupted
- Ensure donor is a valid `.shortcut` file
- Try extracting a fresh donor from iCloud

**"Apple Shortcut signing requires macOS"** (when using `sign_shortcut.sh`)
- Apple's official CLI only works on macOS
- Alternative: use `sign_shortcut_hubsign.py` for cross-platform signing

**"HubSign API returned HTTP 4xx/5xx"** (when using `sign_shortcut_hubsign.py`)
- Check internet connection
- Verify shortcut is structurally valid (run `validate_shortcut.py` first)
- RoutineHub service may be temporarily unavailable
- Fallback: use Apple's CLI on macOS if available

## Incremental Development Strategy

Don't try to build complex shortcuts all at once:

1. **Start minimal** - Create a 1-2 action shortcut first
2. **Build and test** - Generate, sign, import, and verify it works
3. **Add one action** - Extend by one action at a time
4. **Validate and test** - Re-sign and test after each addition
5. **Document patterns** - Note what works for future reference

If something breaks, you know it was the last change.

## Example: Complete Build Workflow

```bash
# 1. Build unsigned shortcut
python tools/build_shortcut.py \
  --donor donors/basic-donor.shortcut \
  --spec specs/hello-world.json \
  --output build/HelloWorld.shortcut \
  --xml-debug build/HelloWorld.xml

# Output:
# Wrote unsigned Shortcut: build/HelloWorld.shortcut
# Actions: 2
# Wrote XML debug copy: build/HelloWorld.xml

# 2. Validate structure
python tools/validate_shortcut.py build/HelloWorld.shortcut

# Output:
# VALID: basic plist/workflow structure passed.
# Actions: 2
#   1. is.workflow.actions.gettext
#   2. is.workflow.actions.showresult

# 3a. Sign with macOS CLI (if on macOS)
./tools/sign_shortcut.sh \
  build/HelloWorld.shortcut \
  build/HelloWorld-signed.shortcut

# OR

# 3b. Sign with HubSign (cross-platform)
python tools/sign_shortcut_hubsign.py \
  build/HelloWorld.shortcut \
  build/HelloWorld-signed.shortcut

# Output:
# Signed shortcut written to: build/HelloWorld-signed.shortcut
# Size: 2048 bytes
# Header: 41454131 (valid)

# 4. Verify signature
xxd -l 4 build/HelloWorld-signed.shortcut
# Expected: 00000000: 4145 4131                             AEA1

# 5. Transfer to iOS and import
# AirDrop, iCloud, email, etc.
# Open in Shortcuts app and test
```

## Best Practices

1. **Always use donors** - Never invent shortcut structure from scratch
2. **Validate before signing** - Catch structural errors early
3. **Test incrementally** - Build one action at a time
4. **Keep donors organized** - Maintain a library of tested donor templates
5. **Document what works** - Record successful action patterns for reuse
6. **Use XML debug output** - Helpful for understanding generated structure
7. **Version control specs** - Track spec files in git, not generated binaries

## Important Files

- `tools/build_shortcut.py` - Generator (88 lines)
- `tools/validate_shortcut.py` - Validator (50 lines)
- `tools/sign_shortcut.sh` - macOS signing wrapper (59 lines)
- `tools/sign_shortcut_hubsign.py` - HubSign cross-platform signer (145 lines)
- `tools/shortcut_plist.py` - Shared utilities (152 lines, UUID resolution)
- `devdocs/toolkit-guide.md` - Comprehensive reference (§6: generation, §7: spec format, §8: UUIDs, §9: donor philosophy, §11: validation, §13: signing)

## Platform Compatibility

**Windows:**
- All build/validate tools work
- Signing: use `sign_shortcut_hubsign.py` (HubSign)

**Linux:**
- All build/validate tools work
- Signing: use `sign_shortcut_hubsign.py` (HubSign)

**macOS:**
- Full toolkit support
- Signing: both methods available (Apple CLI preferred, HubSign as backup)

## Next Steps

After successfully building, signing, and testing a shortcut:

1. **Add to donor library** - Save successful shortcuts as future donors
2. **Document action patterns** - Record learned action structures
3. **Build more complex workflows** - Incrementally add actions
4. **Share knowledge** - Document your findings for future reference
5. **Iterate and improve** - Refine specs based on testing results

## References

- Full generation workflow: `devdocs/toolkit-guide.md` §6
- Spec format details: `devdocs/toolkit-guide.md` §7
- UUID placeholder system: `devdocs/toolkit-guide.md` §8
- Donor philosophy: `devdocs/toolkit-guide.md` §9
- Validation scope: `devdocs/toolkit-guide.md` §11
- Signing methods: `devdocs/toolkit-guide.md` §13
- End-to-end diagram: `devdocs/toolkit-guide.md` §15

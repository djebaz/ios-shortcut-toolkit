# iOS Shortcut Extraction, Generation, Validation, and Signing

## Purpose

This toolkit documents and packages the workflow used around the `pworksIphone` project for working with iOS/macOS Shortcuts as plist-based workflow files.

It covers four distinct operations:

1. **Extract** a publicly shared iCloud Shortcut into an unsigned plist.
2. **Inspect** the plist and its `WFWorkflowActions`.
3. **Generate** a new unsigned Shortcut by mutating a known-good donor workflow.
4. **Sign** the generated file with Apple's `shortcuts` CLI on macOS.

The central design rule is important:

> Do not pretend the complete Apple Shortcut plist format is a stable public authoring API. Use a known-good exported Shortcut as the donor/template, preserve its valid workflow-level metadata, and replace only the parts you understand.

That makes the workflow much more reliable than inventing an entire `.shortcut` structure from scratch.

---

# 1. What exists in the `pworksIphone` project

The project currently contains:

```text
tools/shortcuts/dlshort.py
devdocs/shortcut/README.md
devdocs/references/export-public-shortcut-as-json.md
shortcuts/img2video/dist/Run_Img2Video_in_a-Shell.shortcut
```

The existing downloader retrieves the unsigned workflow asset behind a public iCloud Shortcut link.

The project also contains an exact reconstruction of the working:

```text
Run Img2Video in a-Shell
```

Shortcut, including its action order, action identifiers, input behavior, and parameters.

The signed production artifact is stored separately as a binary `.shortcut`.

The current repository does **not** retain a generic Shortcut generator on `main`, so this toolkit adds one.

---

# 2. Extracting an existing public Shortcut

A public iCloud Shortcut URL looks like:

```text
https://www.icloud.com/shortcuts/<SHORTCUT_ID>
```

The iCloud record endpoint is:

```text
https://www.icloud.com/shortcuts/api/records/<SHORTCUT_ID>
```

The response contains metadata for the shared Shortcut and a temporary asset URL for the unsigned workflow plist.

The included extractor is:

```text
tools/dlshort.py
```

Usage:

```bash
python tools/dlshort.py \
  https://www.icloud.com/shortcuts/<SHORTCUT_ID> \
  ./output
```

It produces:

```text
<name>.plist
<name>.xml
<name>.record.json
```

Meaning:

| File | Purpose |
|---|---|
| `.plist` | Raw unsigned binary plist |
| `.xml` | Readable plist representation |
| `.record.json` | Raw iCloud/CloudKit record metadata |

The extractor uses only the Python standard library.

---

# 3. Shortcut plist structure

A Shortcut is fundamentally represented as a property list.

The most important workflow key for generation is:

```text
WFWorkflowActions
```

It contains the ordered action graph.

Conceptually:

```python
{
    "WFWorkflowActions": [
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
            "WFWorkflowActionParameters": {
                # Action-specific fields
            },
        },
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.showresult",
            "WFWorkflowActionParameters": {
                # Action-specific fields
            },
        },
    ],

    # Additional workflow-level metadata...
}
```

Real exported Shortcuts may also contain:

- workflow type information;
- input content classes;
- no-input behavior;
- icon/presentation settings;
- output UUIDs;
- variable references;
- control-flow grouping UUIDs;
- encoded plist data;
- other Apple-internal fields.

Those details are why a donor/template is preferable.

---

# 4. The existing Img2Video Shortcut as a donor/reference

The project documentation reconstructs the latest confirmed version of:

```text
Run Img2Video in a-Shell
```

Its input is conceptually:

```json
{
  "filename": "example.png",
  "cmd": "python ...existing command arguments..."
}
```

The documented workflow contains 14 actions.

Examples of identifiers observed in that workflow include:

```text
is.workflow.actions.detect.dictionary
is.workflow.actions.getvalueforkey
is.workflow.actions.documentpicker.open
```

This makes the existing Shortcut useful in two ways:

1. as the production Shortcut itself;
2. as a known-valid donor for reverse-engineering action structures and workflow metadata.

---

# 5. Inspecting a Shortcut

Use:

```bash
python tools/inspect_shortcut.py path/to/Donor.shortcut
```

or:

```bash
python tools/inspect_shortcut.py path/to/Donor.plist
```

It prints a summary and action identifiers.

To export an editable JSON spec:

```bash
python tools/inspect_shortcut.py \
  path/to/Donor.shortcut \
  --spec-out donor-spec.json
```

The spec contains the donor's action array encoded as JSON.

Some plist value types do not exist natively in JSON, so the helper library uses explicit wrappers for values such as binary data and dates.

---

# 6. Generating a new Shortcut

The included generator is:

```text
tools/build_shortcut.py
```

It deliberately uses a **donor workflow**.

Usage:

```bash
python tools/build_shortcut.py \
  --donor Donor.shortcut \
  --spec workflow_spec.json \
  --output Generated.shortcut \
  --xml-debug Generated.xml
```

The generator:

1. loads the donor plist;
2. preserves donor workflow metadata;
3. applies optional root-level overrides;
4. replaces `WFWorkflowActions` with the actions in the spec;
5. resolves named UUID placeholders;
6. performs basic structural validation;
7. writes an unsigned binary plist with a `.shortcut` filename;
8. optionally writes an XML debug copy.

---

# 7. Workflow specification format

A generation spec looks like:

```json
{
  "workflow_overrides": {},
  "actions": [
    {
      "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
      "WFWorkflowActionParameters": {}
    }
  ]
}
```

`workflow_overrides` is intentionally optional.

Use it only when you know that a specific donor root field should be changed.

By default, donor metadata remains intact.

---

# 8. Named UUID placeholders

Shortcuts frequently use UUIDs to connect outputs, variables, and control-flow groups.

The generator supports this placeholder:

```text
{{UUID:name}}
```

Example:

```json
{
  "WFWorkflowActionIdentifier": "some.action",
  "WFWorkflowActionParameters": {
    "UUID": "{{UUID:first_output}}"
  }
}
```

If another field uses:

```text
{{UUID:first_output}}
```

the same generated uppercase UUID is inserted there.

For example:

```text
A1B2C3D4-E5F6-7890-ABCD-EF1234567890
```

This lets a spec wire related fields together without hard-coding UUIDs.

Important:

> The placeholder system only solves identity reuse. It does not tell you which action parameter keys Apple expects. Obtain the correct parameter shape from a real exported donor action.

---

# 9. Why donor-based generation is safer

The naive approach would be:

```text
invent complete Shortcut plist
→ write .shortcut
→ hope Apple accepts it
```

The recommended approach is:

```text
known-good exported Shortcut
        │
        ▼
extract / inspect plist
        │
        ▼
preserve valid root metadata
        │
        ▼
replace or construct WFWorkflowActions
        │
        ▼
resolve UUIDs / references
        │
        ▼
write unsigned .shortcut
        │
        ▼
validate
        │
        ▼
sign with Apple tooling
```

This reduces the number of undocumented fields that need to be guessed.

---

# 10. Building new actions

For each new action type, the most reliable development loop is:

1. create the smallest possible Shortcut containing that action in Apple's Shortcuts app;
2. export/share it;
3. extract it with `dlshort.py`;
4. inspect it with `inspect_shortcut.py`;
5. identify the exact action identifier;
6. identify its required parameters;
7. copy/adapt the action dictionary into your spec;
8. replace generated identifiers with `{{UUID:name}}` placeholders where useful;
9. build;
10. validate;
11. sign;
12. import and smoke-test.

Do this action-by-action instead of reverse-engineering a large workflow all at once.

---

# 11. Validation

Use:

```bash
python tools/validate_shortcut.py Generated.shortcut
```

The validator checks at least:

- file parses as a plist;
- root is a dictionary;
- `WFWorkflowActions` exists;
- `WFWorkflowActions` is a list;
- every action is a dictionary;
- every action has a non-empty `WFWorkflowActionIdentifier`;
- action parameters, when present, are dictionaries.

It also prints the action list.

This is only **structural validation**.

It cannot prove that:

- every Apple-internal parameter is valid;
- every variable reference is semantically correct;
- the Shortcut will sign;
- the Shortcut will import;
- the Shortcut will execute successfully.

Apple signing/import and an actual smoke test remain necessary.

---

# 12. Unsigned versus signed `.shortcut`

This distinction is essential.

## Unsigned generated workflow

Python can create the plist representation:

```text
Generated.shortcut
```

At this point it should be treated as an unsigned generated workflow.

It is suitable for:

- inspection;
- diffing;
- automated generation;
- validation;
- signing input.

## Signed Shortcut

The final shareable/importable artifact should be signed with Apple's tooling.

The `pworksIphone` repository similarly treats its final production `.shortcut` as a signed binary artifact rather than a file to modify by hand.

---

# 13. Signing Shortcuts

Two signing methods are available:

## Method 1: Apple's macOS CLI (Official)

Apple documents the `shortcuts sign` command on macOS.

Apple states that signing is available for previously exported Shortcuts and that Apple receives a copy for validation during signing.

Two modes are supported:

```text
anyone
people-who-know-me
```

The included helper is:

```text
tools/sign_shortcut.sh
```

Usage:

```bash
./tools/sign_shortcut.sh \
  Generated.shortcut \
  Generated-signed.shortcut
```

Default mode:

```text
anyone
```

Or explicitly:

```bash
./tools/sign_shortcut.sh \
  Generated.shortcut \
  Generated-signed.shortcut \
  people-who-know-me
```

Equivalent direct command:

```bash
shortcuts sign \
  --mode anyone \
  --input Generated.shortcut \
  --output Generated-signed.shortcut
```

Apple's official documentation:

```text
https://support.apple.com/guide/shortcuts-mac/apd455c82f02/mac
```

**Requirements:**
- macOS with Apple's `shortcuts` CLI tool
- Apple account authentication

## Method 2: RoutineHub HubSign (Cross-platform)

For systems without macOS, use the RoutineHub community's HubSign service.

The included helper is:

```text
tools/sign_shortcut_hubsign.py
```

Usage:

```bash
python tools/sign_shortcut_hubsign.py \
  Generated.shortcut \
  Generated-signed.shortcut
```

Optional shortcut name:

```bash
python tools/sign_shortcut_hubsign.py \
  Generated.shortcut \
  Generated-signed.shortcut \
  --name "My Custom Name"
```

**Requirements:**
- Python 3.7+ (standard library only)
- Active internet connection
- Compliance with RoutineHub service terms

**How it works:**

```text
unsigned .shortcut
      ↓
POST plist to https://hubsign.routinehub.services/sign
      ↓
HubSign signs remotely
      ↓
AEA1-prefixed signed .shortcut
      ↓
import on iOS
```

The service is maintained by the RoutineHub community. CMS signatures for `.shortcut` files cannot be generated outside Apple devices, necessitating this external service.

**Validation:**

Signed files must begin with hex `AEA1` to verify successful signing:

```bash
xxd -l 4 Generated-signed.shortcut
```

Expected output:

```text
00000000: 4145 4131                             AEA1
```

The Python script automatically verifies this header.

## Which method to use?

| Method | Platforms | Network | Ownership |
|--------|-----------|---------|-----------|
| `sign_shortcut.sh` | macOS only | Not required | Apple official |
| `sign_shortcut_hubsign.py` | Windows, Linux, macOS | Required | RoutineHub community |

**Recommendation:**
- Use Apple's CLI on macOS when available (official, local)
- Use HubSign for cross-platform development or when macOS is unavailable

## Important limitation

> Apple's documentation describes signing a Shortcut that was previously exported. A programmatically mutated donor plist still has to be accepted by the signer. This is another reason to preserve a real exported donor structure instead of inventing the full file format.

This limitation applies to both signing methods.

---

# 14. Importing and testing

After signing:

```bash
open Generated-signed.shortcut
```

Shortcuts should present the import/add flow.

Then test the Shortcut in the Shortcuts app.

For command-line-capable macOS workflows, the `shortcuts` CLI can also list, view, and run installed Shortcuts.

Examples:

```bash
shortcuts list
```

```bash
shortcuts view "My Shortcut"
```

```bash
shortcuts run "My Shortcut"
```

A successful plist parse is not enough. The real acceptance sequence is:

```text
plist parses
→ structural validator passes
→ Apple signer accepts
→ Shortcuts imports
→ Shortcut executes correctly
```

---

# 15. Full end-to-end workflow

```text
┌─────────────────────────────────┐
│ Known working iOS Shortcut      │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ dlshort.py                      │
│ public iCloud URL → plist/XML   │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ inspect_shortcut.py             │
│ inspect actions / export spec   │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Edit workflow_spec.json         │
│ - actions                       │
│ - parameters                    │
│ - UUID placeholders             │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ build_shortcut.py               │
│ donor + spec → unsigned file    │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ validate_shortcut.py            │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ shortcuts sign (macOS)          │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Signed .shortcut               │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Import and smoke-test           │
└─────────────────────────────────┘
```

---

# 16. Toolkit files

```text
ios_shortcut_toolkit/
├── README.md
├── AGENTS.md
├── devdocs/
│   └── toolkit-guide.md
├── tools/
│   ├── shortcut_plist.py
│   ├── dlshort.py
│   ├── inspect_shortcut.py
│   ├── build_shortcut.py
│   ├── validate_shortcut.py
│   ├── sign_shortcut.sh
│   └── sign_shortcut_hubsign.py
└── examples/
    ├── workflow_spec.example.json
    └── README.md
```

---

# 17. Suggested permanent project layout

If this is merged back into `pworksIphone`, a clean layout would be:

```text
tools/shortcuts/
├── shortcut_plist.py
├── dlshort.py
├── inspect_shortcut.py
├── build_shortcut.py
├── validate_shortcut.py
├── sign_shortcut.sh
└── sign_shortcut_hubsign.py
```

The existing `dlshort.py` can remain the extraction entry point.

The new files would make the reverse path reproducible:

```text
donor Shortcut
→ editable spec
→ generated unsigned Shortcut
→ validation
→ signing (macOS CLI or HubSign)
```

---

# 18. Repository evidence used for this toolkit

Relevant `pworksIphone` material:

```text
tools/shortcuts/dlshort.py
devdocs/shortcut/README.md
devdocs/references/export-public-shortcut-as-json.md
shortcuts/img2video/dist/Run_Img2Video_in_a-Shell.shortcut
```

Relevant historical commit:

```text
dc3bd036de80ffde6355d888e0fe5694a04cc059
Add an example of a workflow to create a shortcut
```

That commit retained an external extraction/reference workflow, rather than a generic generator implementation.

---

# 19. Practical conclusion

Yes, a new Shortcut can be built programmatically.

The reliable approach is not to treat `.shortcut` as an arbitrary JSON-like file and invent every Apple field.

Instead:

```text
extract a known-good donor
→ inspect exact action structures
→ preserve donor metadata
→ replace/build WFWorkflowActions
→ generate/reuse UUIDs correctly
→ serialize using plistlib
→ structurally validate
→ sign using Apple's shortcuts CLI
→ import and smoke-test
```

The scripts in this archive implement that workflow without third-party Python dependencies.

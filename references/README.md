# Action Reference Documentation

This directory contains reference documentation for Apple Shortcuts actions, compiled from community research and reverse engineering.

## Important Caveats

⚠️ **Use as guidance, not gospel**

1. **Actions evolve** - Apple updates iOS regularly. Action parameters may change, new actions may be added, and existing ones deprecated
2. **Not comprehensive** - While extensive (~100+ actions documented), this is not a complete catalog of all Shortcuts actions
3. **No official documentation** - Apple does not publish action schemas. This reference is community-maintained
4. **Donor-based approach recommended** - The most reliable way to learn action structures is to extract real shortcuts using `dlshort.py` and `inspect_shortcut.py`

## When to Use This Reference

✅ **Good for:**
- Quick lookup of common action identifiers
- Understanding general parameter patterns
- Planning what actions you might need
- Learning about action categories and capabilities

❌ **Not sufficient for:**
- Production shortcuts without testing
- Assuming all parameter details are complete
- Relying on without validating against real shortcuts
- Determining iOS version compatibility

## Recommended Workflow

1. **Reference actions.md** - Find the action identifier and key parameters
2. **Extract a real example** - Download a working shortcut that uses that action
3. **Inspect the structure** - Use `inspect_shortcut.py --spec-out` to see the actual parameters
4. **Document what you learn** - The real shortcut is the source of truth
5. **Build incrementally** - Test each action as you add it

## Files

### actions.md (162 lines)

Catalog of action identifiers organized by category:
- Text & String
- User Interaction
- Variables
- Web & HTTP
- Data & Collections
- Date & Time
- Device & System
- Calendar & Reminders
- Media & Photos
- Files & Sharing
- Communication
- Shortcuts
- Detection & Conversion
- Control Flow

Each entry includes:
- Action name
- Identifier (e.g., `is.workflow.actions.gettext`)
- Key parameter names

### plist-format.md (536 lines)

Detailed plist structure documentation covering:
- XML format and structure
- UUID generation and variable references
- Control flow (if/else, loops, menus)
- Magic variables and input/output
- Action grouping and ordering

**Note:** Our toolkit's donor-based approach handles most of this automatically. This document is useful for understanding the underlying structure.

### url-schemes-and-cli.md (98 lines)

Documentation for:
- `shortcuts://` URL scheme
- macOS `shortcuts` CLI commands
- Automation and triggering

## Attribution

This reference documentation is sourced from the [shortcut-agent-skill](https://github.com/owgit/shortcut-agent-skill) project by [owgit](https://github.com/owgit).

**License:** MIT (same as this toolkit)

## Updates

This reference is a snapshot from September 2026. For the latest community-maintained documentation, check the original repository.

**To update:**
```bash
cd /tmp
git clone https://github.com/owgit/shortcut-agent-skill.git
cp shortcut-agent-skill/.claude/skills/shortcut-agent/references/* \
   path/to/ios-shortcut-toolkit/references/
```

## Philosophy: Donor-Based > Reference-Based

This toolkit prioritizes **donor-based generation**:

```
Known-good shortcut → Extract → Inspect → Adapt → Build → Test
```

Over **reference-based generation**:

```
Reference docs → Guess structure → Hope it works
```

**Why?** Because:
1. Real shortcuts are guaranteed to have valid structure
2. Apple's internal fields are preserved correctly
3. Variable references and UUIDs are wired properly
4. No guessing about undocumented parameters
5. iOS version compatibility is implicit

**Use this reference as a starting point, but always validate against real shortcuts.**

## Contributing

Found an error or want to add missing actions? Consider:
1. Extracting a real shortcut that demonstrates the action
2. Documenting the exact structure you observe
3. Contributing back to [shortcut-agent-skill](https://github.com/owgit/shortcut-agent-skill)
4. Opening an issue or PR here with your findings

## See Also

- **Toolkit Guide:** `devdocs/toolkit-guide.md` §10 - Action development loop
- **Extract Skill:** `.agent/skills/ios-shortcut-extract.md` - Learning from real shortcuts
- **Build Skill:** `.agent/skills/ios-shortcut-build.md` - Donor-based generation

# Example workflow spec

`workflow_spec.example.json` is intentionally **not** a claim that the placeholder
actions are valid Apple actions.

It demonstrates only the generator's spec format and UUID reuse syntax.

Recommended use:

1. Export/extract a real donor Shortcut.
2. Run:

   ```bash
   python3 ../tools/inspect_shortcut.py Donor.shortcut --spec-out donor-spec.json
   ```

3. Edit `donor-spec.json`.
4. Keep real action identifiers and parameter shapes from exported actions.
5. Replace UUIDs that should be regenerated/reused with named placeholders:

   ```text
   {{UUID:some_name}}
   ```

6. Build with:

   ```bash
   python3 ../tools/build_shortcut.py \
     --donor Donor.shortcut \
     --spec donor-spec.json \
     --output Generated.shortcut \
     --xml-debug Generated.xml
   ```

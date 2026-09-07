# iOS Shortcut Sign

Sign unsigned iOS Shortcuts for import on iOS devices. Choose between Apple's official macOS CLI or cross-platform RoutineHub HubSign service.

## When to Use This Skill

Use this skill when you need to:
- Sign an unsigned `.shortcut` file for iOS import
- Choose between macOS CLI and HubSign signing methods
- Verify signature correctness (AEA1 magic bytes)
- Troubleshoot signing failures
- Prepare shortcuts for distribution or testing

## Prerequisites

- **Unsigned shortcut file** - generated from `build_shortcut.py` or extracted with `dlshort.py`
- **Validated structure** - run `validate_shortcut.py` first to catch errors early
- **Signing method requirements** (see below)

**Always validate before signing** to avoid wasted signing attempts.

## Signing Method Comparison

| Aspect | Apple macOS CLI | RoutineHub HubSign |
|--------|-----------------|-------------------|
| **Platform** | macOS only | Windows, Linux, macOS |
| **Requirements** | `shortcuts` CLI tool | Python 3.7+, internet |
| **Network** | Not required | Required |
| **Authentication** | Apple account | None (public service) |
| **Ownership** | Apple official | RoutineHub community |
| **Speed** | Fast (local) | Depends on network |
| **Reliability** | Very high | Subject to service availability |
| **Privacy** | Fully local | Plist sent to remote service |

**Recommendation:**
- **macOS available:** Use Apple's CLI (official, local, fastest)
- **Windows/Linux or no macOS:** Use HubSign (cross-platform alternative)

## Method 1: Apple's macOS CLI (Official)

### Requirements

- macOS operating system
- Apple's `shortcuts` CLI tool installed
- Apple account authentication
- No network connection required

### Usage

**Default signing mode (anyone can use):**
```bash
./tools/sign_shortcut.sh \
  Generated.shortcut \
  Generated-signed.shortcut
```

**Specify signing mode:**
```bash
# "anyone" - Public, no authentication required when importing
./tools/sign_shortcut.sh \
  Generated.shortcut \
  Generated-signed.shortcut \
  anyone

# "people-who-know-me" - Requires iCloud authentication when importing
./tools/sign_shortcut.sh \
  Generated.shortcut \
  Generated-signed.shortcut \
  people-who-know-me
```

**Direct command (without wrapper):**
```bash
shortcuts sign \
  --mode anyone \
  --input Generated.shortcut \
  --output Generated-signed.shortcut
```

### Output

```
Signing Shortcut...
  input : Generated.shortcut
  output: Generated-signed.shortcut
  mode  : anyone
Signed Shortcut written to: Generated-signed.shortcut
```

### Common Errors

**"Apple's 'shortcuts' CLI is not available"**
- The `shortcuts` command is not installed or not in PATH
- Available on recent macOS versions (macOS 12+)
- Check with: `shortcuts --help`

**"Error: Apple Shortcut signing requires macOS"**
- You're running on Windows or Linux
- Alternative: use Method 2 (HubSign)

**Signing fails with "invalid shortcut"**
- Run `validate_shortcut.py` first to check structure
- Shortcut may have invalid action parameters
- Try a simpler donor or check action structures

## Method 2: RoutineHub HubSign (Cross-platform)

### Requirements

- Python 3.7+ (standard library only, no external dependencies)
- Active internet connection
- Compliance with RoutineHub service terms
- Works on Windows, Linux, and macOS

### How It Works

```
unsigned .shortcut
      ↓
POST plist to https://hubsign.routinehub.services/sign
      ↓
HubSign signs remotely (Apple CMS signature)
      ↓
AEA1-prefixed signed .shortcut
      ↓
import on iOS
```

CMS signatures for `.shortcut` files cannot be generated outside Apple devices, so HubSign provides remote signing via the RoutineHub community.

### Usage

**Basic signing:**
```bash
python3 tools/sign_shortcut_hubsign.py \
  Generated.shortcut \
  Generated-signed.shortcut
```

**With custom shortcut name:**
```bash
python3 tools/sign_shortcut_hubsign.py \
  Generated.shortcut \
  Generated-signed.shortcut \
  --name "My Custom Shortcut Name"
```

**With custom timeout:**
```bash
python3 tools/sign_shortcut_hubsign.py \
  Generated.shortcut \
  Generated-signed.shortcut \
  --timeout 120
```

### Output

```
Loading unsigned shortcut: Generated.shortcut
Shortcut name: My Shortcut
Sending to HubSign API (https://hubsign.routinehub.services/sign) ...
Signed shortcut written to: Generated-signed.shortcut
Size: 2048 bytes
Header: 41454131 (valid)

Import on iOS: open the file with the Shortcuts app.
```

### Common Errors

**"Network error connecting to HubSign"**
- Check internet connection
- Verify firewall/proxy settings
- Try again after a moment

**"HubSign API returned HTTP 4xx"**
- Shortcut structure may be invalid
- Run `validate_shortcut.py` first
- Check the response message for details

**"HubSign API returned HTTP 5xx"**
- RoutineHub service may be temporarily unavailable
- Wait and try again later
- Fallback: use Apple's CLI on macOS if available

**"Warning: signed shortcut does not begin with AEA1 magic bytes"**
- Signing may have failed silently
- Do not use this shortcut (it won't import)
- Check for error messages in the output
- Try re-signing or use alternative method

## Signature Verification

After signing, verify the signature is valid:

**Using xxd (recommended):**
```bash
xxd -l 4 Generated-signed.shortcut
```

**Expected output:**
```
00000000: 4145 4131                             AEA1
```

The first 4 bytes must be `41 45 41 31` (ASCII: "AEA1").

**Using hexdump (alternative):**
```bash
hexdump -C -n 4 Generated-signed.shortcut
```

**Expected output:**
```
00000000  41 45 41 31                                       |AEA1|
```

**Python verification script:**
```python
with open('Generated-signed.shortcut', 'rb') as f:
    header = f.read(4)
    if header == b'AEA1':
        print("✓ Valid signature")
    else:
        print(f"✗ Invalid signature: {header.hex()}")
```

If the signature is not valid (doesn't start with AEA1), the shortcut will not import on iOS. Re-sign or try the alternative method.

## Import on iOS

After successful signing and verification:

### Transfer Methods

**AirDrop (fastest for nearby devices):**
1. Select the signed `.shortcut` file
2. Right-click → Share → AirDrop
3. Choose your iOS device
4. Accept on iOS device

**iCloud Drive:**
1. Upload signed `.shortcut` to iCloud Drive
2. Open Files app on iOS
3. Navigate to file
4. Tap to open → Open in Shortcuts

**Email:**
1. Attach signed `.shortcut` to email
2. Send to yourself
3. Open email on iOS device
4. Tap attachment → Open in Shortcuts

**Direct USB (via Finder on macOS):**
1. Connect iOS device via USB
2. Open Finder → Select device
3. Drag signed `.shortcut` to Files section
4. Open on device → Open in Shortcuts

### Import Flow

1. **Open file** - Tap the signed `.shortcut` file
2. **iOS prompts** - "Add Shortcut" or "Add Untrusted Shortcut"
3. **Review** - iOS may show shortcut actions for review
4. **Add** - Tap "Add Shortcut" to import
5. **Test** - Run the shortcut from Shortcuts app

### First-Time Import

If this is your first custom shortcut import:
1. iOS may require enabling "Allow Untrusted Shortcuts"
2. Go to Settings → Shortcuts
3. Enable "Allow Untrusted Shortcuts"
4. Enter device passcode if prompted
5. Return to Files app and retry import

## Complete Signing Workflow

### Example 1: macOS CLI Signing

```bash
# 1. Validate structure first
python3 tools/validate_shortcut.py build/MyShortcut.shortcut

# Output:
# VALID: basic plist/workflow structure passed.
# Actions: 5

# 2. Sign with Apple's CLI
./tools/sign_shortcut.sh \
  build/MyShortcut.shortcut \
  build/MyShortcut-signed.shortcut

# Output:
# Signing Shortcut...
# Signed Shortcut written to: build/MyShortcut-signed.shortcut

# 3. Verify signature
xxd -l 4 build/MyShortcut-signed.shortcut

# Output:
# 00000000: 4145 4131                             AEA1

# 4. Transfer to iOS and import (AirDrop, etc.)
```

### Example 2: HubSign Cross-platform Signing

```bash
# 1. Validate structure first
python3 tools/validate_shortcut.py build/MyShortcut.shortcut

# Output:
# VALID: basic plist/workflow structure passed.
# Actions: 5

# 2. Sign with HubSign
python3 tools/sign_shortcut_hubsign.py \
  build/MyShortcut.shortcut \
  build/MyShortcut-signed.shortcut \
  --name "My Shortcut v1.0"

# Output:
# Loading unsigned shortcut: build/MyShortcut.shortcut
# Shortcut name: My Shortcut v1.0
# Sending to HubSign API ...
# Signed shortcut written to: build/MyShortcut-signed.shortcut
# Size: 3072 bytes
# Header: 41454131 (valid)

# 3. Verify signature (automatic, but double-check)
xxd -l 4 build/MyShortcut-signed.shortcut

# Output:
# 00000000: 4145 4131                             AEA1

# 4. Transfer to iOS and import (iCloud, email, etc.)
```

## Platform-Specific Notes

### Windows

- **Signing:** Use `sign_shortcut_hubsign.py` only (HubSign)
- **Transfer:** iCloud Drive, email, or USB via iTunes
- **Verification:** Use `xxd` from Git Bash or WSL, or Python script

### Linux

- **Signing:** Use `sign_shortcut_hubsign.py` only (HubSign)
- **Transfer:** iCloud web, email, or third-party cloud services
- **Verification:** `xxd` typically available by default

### macOS

- **Signing:** Both methods available (prefer Apple CLI)
- **Transfer:** AirDrop (fastest), iCloud Drive, Finder USB
- **Verification:** `xxd` available by default

## Troubleshooting

### Problem: Shortcut imports but doesn't work

**Possible causes:**
1. **Invalid action parameters** - Validation only checks structure, not semantics
2. **Missing variable references** - UUIDs may be incorrectly linked
3. **iOS version incompatibility** - Action may require newer iOS
4. **Permission issues** - Shortcut may need permissions not granted

**Solutions:**
- Test with simpler donor shortcuts first
- Extract working shortcuts to study action patterns
- Add one action at a time to isolate issues
- Check iOS console logs for runtime errors

### Problem: "Untrusted Shortcut" warning on iOS

**This is normal** for custom shortcuts. Options:

1. **Allow Untrusted Shortcuts** (Settings → Shortcuts)
2. **Use "people-who-know-me" mode** when signing (requires authentication)
3. **Accept the warning** and add anyway (safe if you trust the source)

### Problem: Import fails silently

**Possible causes:**
1. **Invalid signature** - Shortcut not properly signed
2. **Corrupted file** - Transfer may have corrupted the file
3. **iOS restriction** - Device management may block shortcuts

**Solutions:**
- Re-verify AEA1 signature
- Re-transfer the file using different method
- Check device restrictions in Settings → Screen Time

## Important Notes

### Privacy and Security

**Apple CLI:**
- Fully local, shortcut never leaves your machine
- Apple account authentication required
- Highest privacy

**HubSign:**
- Shortcut plist is sent to RoutineHub service
- Do not sign shortcuts containing sensitive data
- Service is community-maintained
- Read RoutineHub terms of service

### Service Availability

**Apple CLI:**
- Always available on macOS (offline)
- No rate limits or quotas
- Deterministic and reliable

**HubSign:**
- Requires internet connection
- Subject to service availability
- May have rate limits (respect fair use)
- Community-maintained (not guaranteed uptime)

### Signing Limitations

Both methods require that the unsigned shortcut has valid structure:
- A programmatically mutated donor plist must be structurally valid
- Apple/HubSign signers may reject invalid shortcuts
- This is why preserving donor metadata is critical

## Related Skills

- **ios-shortcut-build** - Generate unsigned shortcuts from donors
- **ios-shortcut-extract** - Extract shortcuts for use as donors

## Important Files

- `tools/sign_shortcut.sh` - macOS CLI wrapper (59 lines)
- `tools/sign_shortcut_hubsign.py` - HubSign cross-platform signer (145 lines)
- `tools/validate_shortcut.py` - Pre-signing validation (50 lines)
- `devdocs/toolkit-guide.md` - Full signing documentation (§13)

## References

- Signing methods comparison: `devdocs/toolkit-guide.md` §13
- Apple's official docs: https://support.apple.com/guide/shortcuts-mac/apd455c82f02/mac
- HubSign implementation: Based on wynx1123/shortcut-signer pattern
- Full acceptance sequence: `devdocs/toolkit-guide.md` §14

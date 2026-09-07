# Signing Shortcuts via iOS Shortcut

## Sign Shortcut File

**Name**: Sign Shortcut File
**RoutineHub ID**: #26044
**URL**: https://routinehub.co/shortcut/26044/

### Overview

This RoutineHub shortcut provides an iOS-native method for signing unsigned shortcuts directly on your iPhone/iPad, without requiring:
- A Mac
- macOS CLI tools
- Developer accounts
- Network API calls to external services

### Usage

**Requirements:**
- iOS device with Shortcuts app
- "Sign Shortcut File" shortcut installed from RoutineHub

**Process:**
1. Install "Sign Shortcut File" from https://routinehub.co/shortcut/26044/
2. Transfer your unsigned `.shortcut` file to your iOS device
   - Via AirDrop from Windows/Mac
   - Via iCloud Drive upload
   - Via email attachment
   - Via any file transfer method
3. Run the "Sign Shortcut File" shortcut
4. Select your unsigned `.shortcut` file from Files app picker
5. The shortcut outputs a **signed `.shortcut` file** ready to import
6. Import the signed shortcut into your Shortcuts library

### Advantages

✅ **Cross-platform preparation**: Create unsigned shortcuts on Windows/Linux, sign on iOS
✅ **No Mac required**: Works entirely on iPhone/iPad
✅ **No external accounts**: No need for RoutineHub membership or authentication
✅ **Simple workflow**: File in → Signed file out
✅ **Quick**: Instant signing on device
✅ **Self-contained**: All processing happens on your device

### Complete Workflow Example

**Windows/Linux → iOS Signing:**

1. **On Windows/Linux**: Build unsigned shortcut
   ```bash
   python3 tools/build_shortcut.py \
     --donor donors/my_donor.shortcut \
     --record my_actions.record.json \
     --output build/MyShortcut.shortcut
   ```

2. **Transfer to iOS**: Upload to iCloud Drive
   ```bash
   cp build/MyShortcut.shortcut ~/iCloud\ Drive/
   ```

3. **On iOS**:
   - Run "Sign Shortcut File" shortcut
   - Select `MyShortcut.shortcut` from Files app
   - Save the signed output
   - Import into Shortcuts app

4. **Done**: Your shortcut is signed and ready to use!

### Related Methods

Compare with:
- **Apple macOS CLI** (`shortcuts sign`) - macOS only, requires iCloud login
- **HubSign API** - Cross-platform, requires internet, RoutineHub membership
- **GitHub Actions** - Requires repository, GitHub account, iCloud authentication
- **iCloud Link sharing** - Requires shortcut already imported on iOS

### Technical Details

**Input Format**: Unsigned `.shortcut` file (binary plist with `bplist00` header)
**Output Format**: Signed `.shortcut` file (AEA1-prefixed encrypted format)
**File Selection**: iOS Files app picker (supports iCloud Drive, local files, etc.)
**Processing**: On-device signing (implementation method unknown)

### Testing Notes

**Successfully tested with:**
- **File**: `Run_splitvids_iOS_Smoke.shortcut`
- **Size**: 14KB (13,571 bytes)
- **Actions**: 86 actions
- **Platform**: iPhone
- **Result**: ✅ Successfully signed and ready to import
- **Date**: 2026-09-07

### Troubleshooting

**Issue**: Files app doesn't show `.shortcut` files
**Solution**: Ensure the file has `.shortcut` extension and is in an accessible location (iCloud Drive, On My iPhone, etc.)

**Issue**: Signed shortcut won't import
**Solution**: Verify the output file starts with `AEA1` magic bytes (use a hex viewer or `xxd` on Mac)

**Issue**: Shortcut not available on RoutineHub
**Solution**: Check the URL is correct: https://routinehub.co/shortcut/26044/

### Comparison with Other Methods

| Method | Platform | Requirements | Speed | Privacy |
|--------|----------|--------------|-------|---------|
| **Sign Shortcut File (iOS)** | iOS only | iOS device, Files app | Instant | Full (on-device) |
| Apple macOS CLI | macOS only | macOS 12+, iCloud login | Fast | Full (local) |
| HubSign API | Cross-platform | Internet, Python | Medium | Low (remote service) |
| GitHub Actions | Any | GitHub account, iCloud | Slow (CI queue) | Medium |
| iCloud Link Share | iOS only | Shortcut already imported | Instant | Full (Apple servers) |

**Recommendation**: For cross-platform workflows, use "Sign Shortcut File" on iOS as the easiest and most private method.

---

*Last updated: 2026-09-07*

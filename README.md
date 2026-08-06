# vivo Backup Decryptor

🔓 Decrypt encrypted files from vivo/iQOO PhoneClone (互传) backups

<div align="center">

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

</div>

## ✨ Features

- 🚀 **Fast & Simple** - Pure Python, no dependencies required
- 📁 **Smart Recovery** - Restores original filenames and folder structure
- 🎯 **Multi-format** - Supports JPEG, WebP, PNG, MP4, and more
- 🖥️ **Web Interface** - Easy-to-use browser-based GUI
- 🔍 **Auto-detection** - Identifies file types automatically

## 📋 Supported Devices

This tool works with backups created by:

- **vivo** phones (X series, S series, Y series, etc.)
- **iQOO** phones (iQOO series, Neo series, Z series, etc.)
- **OPPO** phones (some models with PhoneClone)
- **Realme** phones (some models with PhoneClone)

✅ Tested on backup format version 2 (`backupPackageVer: 2`)

## 🚀 Quick Start

### Command Line

```bash
# Basic usage
python decrypt.py "backup_folder"

# Specify output directory
python decrypt.py "backup_folder" "output_folder"

# Verbose mode
python decrypt.py "backup_folder" -v

# Keep hash filenames
python decrypt.py "backup_folder" --keep-hash-names
```

### Web Interface

```bash
# Start web server
python web.py

# Open browser
# http://localhost:5000
```

Then drag & drop your backup folder or select it using the file picker.

## 📦 Installation

### Requirements

- Python 3.6 or higher
- No external dependencies for CLI tool
- Flask required for web interface (optional)

### Clone Repository

```bash
git clone https://github.com/yourusername/vivo-backup-decryptor.git
cd vivo-backup-decryptor
```

### Install Web Interface Dependencies (Optional)

```bash
pip install flask
```

## 📂 Backup Structure

```
backup_folder/
├── .backup                 # JSON metadata (device model, timestamp)
├── db/                     # LevelDB index (filename mappings)
│   ├── 000005.ldb
│   ├── CURRENT
│   └── MANIFEST-XXXXXX
├── 11fdb14d89dc...         # SHA-1 named encrypted files
├── 00a5097ee4db...
└── ...
```

## 🔐 How It Works

### Encryption Algorithm

vivo backups use a simple XOR cipher with a fixed 8-byte key:

```
Key: 5b 9d 2e f4 7f a3 c8 e1
```

Encryption formula:
```
ciphertext[i] = plaintext[i] XOR key[i % 8]
```

### File Format Types

#### Type 0/1 - JPEG with Magic Header

```
[4 bytes: 80 7b 37 XX] + [XOR encrypted data]
```

- `807b3700` → JPEG with Exif (FFD8FFE1)
- `807b3701` → JPEG with JFIF (FFD8FFE0)

#### No Header - WebP/Other Formats

```
[XOR encrypted data starting from key[4]]
```

Files encrypted with key offset 4, includes WebP, PNG, MP4, etc.

## 📊 Examples

### Example 1: Basic Decryption

```bash
$ python decrypt.py "vivo S16 20260806_202318"

Found 114 file mappings in index

  ✓ IMG_20260720_164053.jpg
  ✓ Screenshot_20240202_184845.webp
  ✓ video_20260115.mp4
  ...

==================================================
Decryption Complete
==================================================
Success: 16 files
Failed:  0 files
Output:  vivo S16 20260806_202318_decrypted
```

### Example 2: Verbose Output

```bash
$ python decrypt.py "backup" "restored" -v

Backup Info:
  Model: HONOR 30
  Version: 2
  Success: False

Found 114 file mappings in index

  ✓ IMG_20260720_164053.jpg
  ...
```

## 🌐 Web Interface

The web interface provides a user-friendly way to decrypt backups:

1. **Upload** - Drag & drop or browse for backup folder
2. **Process** - Automatic decryption with progress tracking
3. **Download** - Get your files back in original structure

### Features

- 📤 Drag & drop upload
- 📊 Real-time progress tracking
- 🎨 Modern dark theme UI
- 📱 Mobile responsive design
- 💾 Batch processing support

## 🛠️ Advanced Usage

### Python API

```python
from decrypt import decrypt_file, parse_file_index

# Decrypt single file
data, ext = decrypt_file('11fdb14d89dc23ae...')
if data:
    with open(f'output{ext}', 'wb') as f:
        f.write(data)

# Parse file index
hash_map = parse_file_index('backup/db')
print(hash_map['11fdb14d89dc23ae...'])
# Output: storage/emulated/0/DCIM/Camera/IMG_20260720.jpg
```

## ❓ FAQ

### Why are some files missing original names?

The backup may have been interrupted (`.backup` shows `"success": false`). Files can still be decrypted but will use hash names.

### Can I decrypt contacts/SMS/app data?

Yes, theoretically. These are stored in SQLite databases using the same encryption. You'll need to identify and parse the database structure after decryption.

### Is this legal?

✅ Decrypting **your own** backup data - Legal  
✅ Data recovery and migration - Legal  
❌ Accessing others' data without permission - Illegal  
❌ Any malicious use - Illegal

### Why does vivo use weak encryption?

Possible reasons:
- **Performance** - XOR is extremely fast for large files
- **Compatibility** - Works on older/low-end devices
- **Use case** - Backups are typically stored on user's own computer
- **Obfuscation** - Prevents casual viewing, not designed for high security

## 🔬 Technical Details

### Security Analysis

The XOR encryption has several weaknesses:

1. **Fixed key** - Same key for all backups
2. **No IV** - Identical plaintext produces identical ciphertext
3. **Known plaintext** - JPEG headers are predictable
4. **Frequency analysis** - Byte distribution patterns visible
5. **Zero padding** - File padding directly reveals the key

### Comparison with Modern Encryption

| Feature | vivo XOR | AES-256-GCM |
|---------|----------|-------------|
| Key space | 2^64 | 2^256 |
| Known plaintext resistant | ❌ | ✅ |
| Authenticated | ❌ | ✅ |
| Speed | Very fast | Fast |
| Security | Low | High |

## 📝 File Type Support

| Format | Extension | Detection |
|--------|-----------|-----------|
| JPEG | `.jpg` | `FFD8FF` |
| PNG | `.png` | `89504E47` |
| GIF | `.gif` | `GIF8` |
| WebP | `.webp` | `RIFF...WEBP` |
| MP4 | `.mp4` | `ftyp` at offset 4 |
| ZIP | `.zip` | `PK\x03\x04` |
| PDF | `.pdf` | `%PDF` |
| MP3 | `.mp3` | `FFFB/FFF3` |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### Development

```bash
# Clone repository
git clone https://github.com/yourusername/vivo-backup-decryptor.git
cd vivo-backup-decryptor

# Run tests (if available)
python -m pytest

# Run linter
python -m pylint decrypt.py
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## ⚠️ Disclaimer

This tool is for educational and personal data recovery purposes only. Users are responsible for ensuring they have the right to decrypt the data. The authors assume no liability for misuse.

## 🙏 Acknowledgments

- Reverse engineering and cryptanalysis community
- vivo/iQOO users who shared backup samples

## 📚 References

- [XOR Cipher - Wikipedia](https://en.wikipedia.org/wiki/XOR_cipher)
- [JPEG File Format](https://en.wikipedia.org/wiki/JPEG)
- [WebP Specification](https://developers.google.com/speed/webp/docs/riff_container)
- [LevelDB Documentation](https://github.com/google/leveldb)

---

<div align="center">

**Made with ❤️ for data recovery**

[Report Bug](https://github.com/yourusername/vivo-backup-decryptor/issues) · [Request Feature](https://github.com/yourusername/vivo-backup-decryptor/issues)

</div>

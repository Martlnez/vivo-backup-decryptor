"""
vivo Backup Decryption Tool
Decrypt encrypted files from vivo PhoneClone/互传 backups

Usage: python decrypt.py <backup_folder> [output_folder]
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Tuple, Dict

# XOR encryption key (fixed for all vivo backups)
XOR_KEY = bytes([0x5b, 0x9d, 0x2e, 0xf4, 0x7f, 0xa3, 0xc8, 0xe1])

# File format signatures
MAGIC_807B37 = b'\x80\x7b\x37'
JPEG_EXIF_PREFIX = b'\xff\xd8\xff\xe1'   # Type 0
JPEG_JFIF_PREFIX = b'\xff\xd8\xff\xe0'   # Type 1

# File type signatures for identification
FILE_SIGNATURES = {
    b'\xff\xd8\xff': '.jpg',
    b'\x89PNG\r\n\x1a\n': '.png',
    b'GIF8': '.gif',
    b'RIFF': '.webp',
    b'PK\x03\x04': '.zip',
    b'%PDF': '.pdf',
    b'\xff\xfb': '.mp3',
    b'\xff\xf3': '.mp3',
}


def xor_decrypt(data: bytes, key_offset: int = 0) -> bytes:
    """
    XOR decrypt data using the fixed vivo backup key.

    Args:
        data: Encrypted data bytes
        key_offset: Starting offset in the key (0 or 4)

    Returns:
        Decrypted data bytes
    """
    result = bytearray(len(data))
    for i in range(len(data)):
        result[i] = data[i] ^ XOR_KEY[(i + key_offset) % 8]
    return bytes(result)


def identify_file_type(data: bytes) -> str:
    """
    Identify file type from decrypted data header.

    Args:
        data: Decrypted file data

    Returns:
        File extension (e.g., '.jpg', '.png')
    """
    # Check for WebP specifically
    if data[:4] == b'RIFF' and len(data) > 12 and data[8:12] == b'WEBP':
        return '.webp'

    # Check MP4 variants
    if len(data) > 12 and data[4:8] == b'ftyp':
        return '.mp4'

    # Check other signatures
    for sig, ext in FILE_SIGNATURES.items():
        if data.startswith(sig):
            return ext

    return '.bin'


def decrypt_file(filepath: str) -> Tuple[Optional[bytes], str]:
    """
    Decrypt a single backup file.

    Args:
        filepath: Path to encrypted file

    Returns:
        Tuple of (decrypted_data, file_extension)
    """
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None, ''

    if len(data) < 4:
        return None, ''

    # Check for magic header (Type 0/1 JPEG)
    if data[:3] == MAGIC_807B37:
        file_type = data[3]
        encrypted = data[4:]
        decrypted = xor_decrypt(encrypted, key_offset=0)

        if file_type == 0:
            return JPEG_EXIF_PREFIX + decrypted, '.jpg'
        elif file_type == 1:
            return JPEG_JFIF_PREFIX + decrypted, '.jpg'
        else:
            # Unknown type, try to identify
            ext = identify_file_type(decrypted)
            return decrypted, ext
    else:
        # No magic header, decrypt with key offset 4 (WebP/other formats)
        decrypted = xor_decrypt(data, key_offset=4)
        ext = identify_file_type(decrypted)
        return decrypted, ext


def parse_file_index(db_path: str) -> Dict[str, str]:
    """
    Extract hash -> original file path mapping from LevelDB.

    Args:
        db_path: Path to db/ directory

    Returns:
        Dictionary mapping hash to original file path
    """
    if not os.path.isdir(db_path):
        return {}

    ldb_files = [f for f in os.listdir(db_path) if f.endswith('.ldb')]
    all_data = b''

    for ldb in ldb_files:
        try:
            with open(os.path.join(db_path, ldb), 'rb') as f:
                all_data += f.read()
        except Exception as e:
            print(f"Warning: Could not read {ldb}: {e}")
            continue

    hash_to_path = {}
    pattern = rb'([0-9a-f]{40}).{0,200}\"filename\":\"([^\"]+)\"'
    matches = re.findall(pattern, all_data)

    for h, fn in matches:
        hash_to_path[h.decode()] = fn.decode('utf-8', errors='replace')

    return hash_to_path


def parse_backup_metadata(backup_dir: str) -> Optional[Dict]:
    """
    Parse .backup metadata file.

    Args:
        backup_dir: Backup directory path

    Returns:
        Metadata dictionary or None
    """
    metadata_path = os.path.join(backup_dir, '.backup')
    if not os.path.isfile(metadata_path):
        return None

    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not parse .backup metadata: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Decrypt vivo PhoneClone/互传 backup files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python decrypt.py "HONOR 30 20260727_061218"
  python decrypt.py backup_folder output_folder
  python decrypt.py backup_folder -v
        '''
    )
    parser.add_argument('backup_dir', help='Backup folder path')
    parser.add_argument('output_dir', nargs='?', help='Output folder (default: <backup_dir>_decrypted)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--keep-hash-names', action='store_true',
                       help='Keep hash filenames instead of original names')

    args = parser.parse_args()

    backup_dir = args.backup_dir
    output_dir = args.output_dir or (backup_dir.rstrip('/\\') + '_decrypted')

    if not os.path.isdir(backup_dir):
        print(f"Error: Backup directory not found: {backup_dir}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    # Parse metadata
    metadata = parse_backup_metadata(backup_dir)
    if metadata and args.verbose:
        print(f"Backup Info:")
        print(f"  Model: {metadata.get('model', 'Unknown')}")
        print(f"  Version: {metadata.get('backupPackageVer', 'Unknown')}")
        print(f"  Success: {metadata.get('success', False)}")
        print()

    # Parse file index
    db_path = os.path.join(backup_dir, 'db')
    hash_to_path =

    if not args.keep_hash_names:
        hash_to_path = parse_file_index(db_path)
        if hash_to_path:
            print(f"Found {len(hash_to_path)} file mappings in index\n")

    # Decrypt files
    success = 0
    failed = 0
    skipped = 0

    for filename in os.listdir(backup_dir):
        filepath = os.path.join(backup_dir, filename)

        # Skip non-files and non-hash files
        if not os.path.isfile(filepath):
            continue
        if filename.startswith('.') or len(filename) != 40:
            skipped += 1
            continue
        if not all(c in '0123456789abcdef' for c in filename):
            skipped += 1
            continue

        # Decrypt file
        decrypted, ext = decrypt_file(filepath)
        if decrypted is None:
            failed += 1
            if args.verbose:
                print(f"  ✗ Failed: {filename}")
            continue

        # Determine output path
        original_path = hash_to_path.get(filename)
        if original_path and not args.keep_hash_names:
            original_name = os.path.basename(original_path)
            rel_dir = os.path.dirname(original_path)

            # Remove Android storage prefix
            if rel_dir.startswith('storage/emulated/0/'):
                rel_dir = rel_dir[len('storage/emulated/0/'):]

            out_subdir = os.path.join(output_dir, rel_dir)
            os.makedirs(out_subdir, exist_ok=True)
            out_path = os.path.join(out_subdir, original_name)
        else:
            out_path = os.path.join(output_dir, filename + ext)

        # Write decrypted file
        try:
            with open(out_path, 'wb') as f:
                f.write(decrypted)
            success += 1
            print(f"  ✓ {os.path.basename(out_path)}")
        except Exception as e:
            failed += 1
            print(f"  ✗ Error writing {out_path}: {e}")

    # Summary
    print(f"\n{'='*50}")
    print(f"Decryption Complete")
    print(f"{'='*50}")
    print(f"Success: {success} files")
    print(f"Failed:  {failed} files")
    if skipped > 0 and args.verbose:
        print(f"Skipped: {skipped} files (metadata/index)")
    print(f"Output:  {output_dir}")


if __name__ == '__main__':
    main()

"""
Web interface for vivo Backup Decryptor
Provides a user-friendly browser-based GUI for decryption
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import tempfile
import shutil
import zipfile
from pathlib import Path
from decrypt import decrypt_file, parse_file_index, parse_backup_metadata

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB max upload
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api/decrypt', methods=['POST'])
def decrypt_backup():
    """
    Decrypt backup files uploaded by user

    Expected: multipart form with backup folder files
    Returns: JSON with status and file list
    """
    if 'files' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'Empty file list'}), 400

    # Create temporary directories
    temp_dir = tempfile.mkdtemp(prefix='vivo_backup_')
    backup_dir = os.path.join(temp_dir, 'backup')
    output_dir = os.path.join(temp_dir, 'decrypted')
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Save uploaded files
        for file in files:
            if file.filename:
                # Reconstruct directory structure
                filepath = os.path.join(backup_dir, file.filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)

        # Parse metadata
        metadata = parse_backup_metadata(backup_dir)

        # Parse file index
        db_path = os.path.join(backup_dir, 'db')
        hash_to_path = parse_file_index(db_path)

        # Decrypt files
        results = []
        success_count = 0
        failed_count = 0

        for filename in os.listdir(backup_dir):
            filepath = os.path.join(backup_dir, filename)

            # Skip non-hash files
            if not os.path.isfile(filepath):
                continue
            if len(filename) != 40 or not all(c in '0123456789abcdef' for c in filename):
                continue

            # Decrypt
            decrypted, ext = decrypt_file(filepath)
            if decrypted is None:
                failed_count += 1
                results.append({
                    'hash': filename,
                    'status': 'failed',
                    'size': 0
                })
                continue

            # Determine output path
            original_path = hash_to_path.get(filename)
            if original_path:
                original_name = os.path.basename(original_path)
                rel_dir = os.path.dirname(original_path)
                if rel_dir.startswith('storage/emulated/0/'):
                    rel_dir = rel_dir[len('storage/emulated/0/'):]
                out_subdir = os.path.join(output_dir, rel_dir)
                os.makedirs(out_subdir, exist_ok=True)
                out_path = os.path.join(out_subdir, original_name)
            else:
                out_path = os.path.join(output_dir, filename + ext)

            # Write decrypted file
            with open(out_path, 'wb') as f:
                f.write(decrypted)

            success_count += 1
            results.append({
                'hash': filename,
                'original_name': original_path or (filename + ext),
                'status': 'success',
                'size': len(decrypted),
                'type': ext
            })

        # Create ZIP archive
        zip_path = os.path.join(temp_dir, 'decrypted_backup.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, output_dir)
                    zipf.write(file_path, arcname)

        # Return results
        return jsonify({
            'success': True,
            'metadata': metadata,
            'stats': {
                'success': success_count,
                'failed': failed_count,
                'total': success_count + failed_count,
                'index_entries': len(hash_to_path)
            },
            'files': results[:100],  # Limit response size
            'download_url': f'/api/download/{os.path.basename(temp_dir)}'
        })

    except Exception as e:
        # Cleanup on error
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<session_id>')
def download_result(session_id):
    """
    Download decrypted files as ZIP

    Args:
        session_id: Temporary directory session ID
    """
    temp_dir = os.path.join(tempfile.gettempdir(), session_id)
    zip_path = os.path.join(temp_dir, 'decrypted_backup.zip')

    if not os.path.exists(zip_path):
        return jsonify({'error': 'File not found or expired'}), 404

    def cleanup():
        """Cleanup after download"""
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

    response = send_file(
        zip_path,
        as_attachment=True,
        download_name='vivo_backup_decrypted.zip',
        mimetype='application/zip'
    )

    # Schedule cleanup (will run after response is sent)
    request.environ.get('werkzeug.server.shutdown')

    return response


@app.route('/api/info')
def info():
    """Return tool information"""
    return jsonify({
        'name': 'vivo Backup Decryptor',
        'version': '1.0.0',
        'encryption': 'XOR with fixed 8-byte key',
        'supported_formats': ['JPEG', 'WebP', 'PNG', 'MP4', 'ZIP', 'PDF', 'MP3'],
        'backup_version': 2
    })


if __name__ == '__main__':
    print('='*50)
    print('vivo Backup Decryptor - Web Interface')
    print('='*50)
    print('Starting server at http://localhost:5000')
    print('Press Ctrl+C to stop')
    print('='*50)
    app.run(debug=True, host='0.0.0.0', port=5000)

// vivo Backup Decryptor - Web Interface JavaScript

let selectedFiles = [];
let downloadUrl = '';

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const fileInfo = document.getElementById('fileInfo');
const fileCount = document.getElementById('fileCount');
const decryptBtn = document.getElementById('decryptBtn');

const uploadSection = document.getElementById('uploadSection');
const progressSection = document.getElementById('progressSection');
const resultsSection = document.getElementById('resultsSection');

const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');

const statSuccess = document.getElementById('statSuccess');
const statFailed = document.getElementById('statFailed');
const statTotal = document.getElementById('statTotal');
const backupInfo = document.getElementById('backupInfo');
const fileList = document.getElementById('fileList');

const downloadBtn = document.getElementById('downloadBtn');
const resetBtn = document.getElementById('resetBtn');

// Event Listeners
browseBtn.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');

    const items = e.dataTransfer.items;
    if (items) {
        handleDroppedItems(items);
    }
});

decryptBtn.addEventListener('click', startDecryption);
downloadBtn.addEventListener('click', downloadFiles);
resetBtn.addEventListener('click', reset);

// Handle file selection
function handleFiles(files) {
    selectedFiles = Array.from(files);

    if (selectedFiles.length === 0) {
        return;
    }

    fileCount.textContent = `${selectedFiles.length} files`;
    fileInfo.style.display = 'block';
}

// Handle dropped items (folders)
async function handleDroppedItems(items) {
    const files = [];

    for (let i = 0; i < items.length; i++) {
        const item = items[i].webkitGetAsEntry();
        if (item) {
            await traverseFileTree(item, '', files);
        }
    }

    handleFiles(files);
}

// Recursively traverse file tree
function traverseFileTree(item, path, files) {
    return new Promise((resolve) => {
        if (item.isFile) {
            item.file((file) => {
                const newFile = new File([file], path + file.name, { type: file.type });
                files.push(newFile);
                resolve();
            });
        } else if (item.isDirectory) {
            const dirReader = item.createReader();
            dirReader.readEntries(async (entries) => {
                for (let entry of entries) {
                    await traverseFileTree(entry, path + item.name + '/', files);
                }
                resolve();
            });
        }
    });
}

// Start decryption process
async function startDecryption() {
    if (selectedFiles.length === 0) {
        alert('Please select backup files first');
        return;
    }

    // Show progress
    uploadSection.style.display = 'none';
    progressSection.style.display = 'block';

    // Prepare form data
    const formData = new FormData();
    selectedFiles.forEach((file) => {
        formData.append('files', file, file.name);
    });

    try {
        // Update progress
        updateProgress(10, 'Uploading files...');

        // Send to server
        const response = await fetch('/api/decrypt', {
            method: 'POST',
            body: formData
        });

        updateProgress(50, 'Processing files...');

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const result = await response.json();

        if (result.error) {
            throw new Error(result.error);
        }

        updateProgress(100, 'Complete!');

        // Show results
        setTimeout(() => {
            showResults(result);
        }, 500);

    } catch (error) {
        console.error('Decryption error:', error);
        alert(`Decryption failed: ${error.message}`);
        reset();
    }
}

// Update progress bar
function updateProgress(percent, text) {
    progressFill.style.width = `${percent}%`;
    progressText.textContent = text;
}

// Show results
function showResults(result) {
    progressSection.style.display = 'none';
    resultsSection.style.display = 'block';

    // Update stats
    statSuccess.textContent = result.stats.success;
    statFailed.textContent = result.stats.failed;
    statTotal.textContent = result.stats.total;

    // Show backup info
    if (result.metadata) {
        const meta = result.metadata;
        backupInfo.innerHTML = `
            <p><strong>Device:</strong> ${meta.model || 'Unknown'}</p>
            <p><strong>Backup Version:</strong> ${meta.backupPackageVer || 'Unknown'}</p>
            <p><strong>Status:</strong> ${meta.success ? '✅ Complete' : '⚠️ Incomplete'}</p>
            <p><strong>Index Entries:</strong> ${result.stats.index_entries}</p>
        `;
    }

    // Show file list
    if (result.files && result.files.length > 0) {
        const fileItems = result.files
            .filter(f => f.status === 'success')
            .slice(0, 50)
            .map(f => {
                const name = f.original_name.split('/').pop();
                return `
                    <div class="file-item">
                        <span class="file-name">${name}</span>
                        <span class="file-type">${f.type}</span>
                    </div>
                `;
            })
            .join('');

        fileList.innerHTML = fileItems;

        if (result.files.length > 50) {
            fileList.innerHTML += `
                <div class="file-item">
                    <span class="file-name">... and ${result.files.length - 50} more files</span>
                </div>
            `;
        }
    }

    // Store download URL
    downloadUrl = result.download_url;
}

// Download files
function downloadFiles() {
    if (!downloadUrl) {
        alert('No files to download');
        return;
    }

    window.location.href = downloadUrl;
}

// Reset to initial state
function reset() {
    selectedFiles = [];
    downloadUrl = '';

    fileInfo.style.display = 'none';
    uploadSection.style.display = 'block';
    progressSection.style.display = 'none';
    resultsSection.style.display = 'none';

    fileInput.value = '';
    progressFill.style.width = '0%';
    progressText.textContent = 'Initializing...';
}

// Load tool info on page load
window.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/info');
        const info = await response.json();
        console.log('vivo Backup Decryptor loaded:', info);
    } catch (error) {
        console.error('Failed to load tool info:', error);
    }
});

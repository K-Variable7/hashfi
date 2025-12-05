// --- Vault Key Mode Toggle ---
function toggleVaultKeyMode() {
    // If unchecked, prompt for password as before. If checked, use messaging key.
}
// --- SECURE MESSAGING & ENCRYPTED VAULT SYNC (Web Crypto API) ---

// --- Utility Functions ---
function buf2hex(buffer) {
    return Array.prototype.map.call(new Uint8Array(buffer), x => ('00' + x.toString(16)).slice(-2)).join('');
}
function hex2buf(hex) {
    const bytes = new Uint8Array(hex.length / 2);
    for (let i = 0; i < bytes.length; i++) {
        bytes[i] = parseInt(hex.substr(i * 2, 2), 16);
    }
    return bytes.buffer;
}
function buf2b64(buffer) {
    return btoa(String.fromCharCode(...new Uint8Array(buffer)));
}
function b642buf(b64) {
    return Uint8Array.from(atob(b64), c => c.charCodeAt(0)).buffer;
}

// --- Key Derivation ---
async function deriveKey(password) {
    const enc = new TextEncoder();
    const salt = enc.encode('hashfi-salt');
    const keyMaterial = await window.crypto.subtle.importKey(
        'raw', enc.encode(password), {name: 'PBKDF2'}, false, ['deriveKey']
    );
    return window.crypto.subtle.deriveKey(
        {name: 'PBKDF2', salt, iterations: 100000, hash: 'SHA-256'},
        keyMaterial,
        {name: 'AES-GCM', length: 256},
        false,
        ['encrypt', 'decrypt']
    );
}

async function importRawKey(hex) {
    return window.crypto.subtle.importKey(
        'raw', hex2buf(hex), 'AES-GCM', false, ['encrypt', 'decrypt']
    );
}

function getMsgKey() {
    const mode = document.querySelector('input[name="msgKeyMode"]:checked').value;
    if (mode === 'password') {
        return deriveKey(document.getElementById('msgPassword').value);
    } else {
        return importRawKey(document.getElementById('msgRandomKey').value);
    }
}

// --- Messaging UI Logic ---
function toggleKeyMode() {
    const mode = document.querySelector('input[name="msgKeyMode"]:checked').value;
    document.getElementById('passwordKeyDiv').style.display = (mode === 'password') ? '' : 'none';
    document.getElementById('randomKeyDiv').style.display = (mode === 'random') ? '' : 'none';
}

function generateRandomKey() {
    const arr = new Uint8Array(32);
    window.crypto.getRandomValues(arr);
    const hex = Array.from(arr).map(b => b.toString(16).padStart(2, '0')).join('');
    document.getElementById('msgRandomKey').value = hex;
    renderMsgKeyQR(hex);
}

function copyRandomKey() {
    const key = document.getElementById('msgRandomKey').value;
    navigator.clipboard.writeText(key);
    alert('Key copied!');
}

function renderMsgKeyQR(hex) {
    if (!window.QRCode) return;
    const canvas = document.getElementById('msgKeyQR');
    const qr = new window.QRCode(canvas, {
        text: hex,
        width: 128,
        height: 128,
        colorDark: '#00ff41',
        colorLight: '#111',
        correctLevel: window.QRCode.CorrectLevel.L
    });
    // Clear previous QR if any
    while (canvas.firstChild) canvas.removeChild(canvas.firstChild);
    qr.makeCode(hex);
}

// --- Encrypt/Decrypt Message ---
async function sendSecureMessage() {
    const msg = document.getElementById('msgInput').value;
    if (!msg) return;
    const key = await getMsgKey();
    const iv = window.crypto.getRandomValues(new Uint8Array(12));
    const enc = new TextEncoder();
    const ciphertext = await window.crypto.subtle.encrypt(
        {name: 'AES-GCM', iv}, key, enc.encode(msg)
    );
    const payload = buf2b64(iv) + ':' + buf2b64(ciphertext);
    document.getElementById('msgOutput').innerText = payload;
}

async function decryptReceivedMessage() {
    const payload = document.getElementById('msgReceiveInput').value;
    if (!payload.includes(':')) return alert('Invalid message format');
    const [ivB64, ctB64] = payload.split(':');
    const key = await getMsgKey();
    const iv = b642buf(ivB64);
    const ct = b642buf(ctB64);
    try {
        const pt = await window.crypto.subtle.decrypt(
            {name: 'AES-GCM', iv: new Uint8Array(iv)}, key, ct
        );
        document.getElementById('msgOutput').innerText = new TextDecoder().decode(pt);
    } catch (e) {
        alert('Decryption failed! Wrong key or corrupted message.');
    }
}

// --- Vault Export/Import ---
async function exportVault() {
    // Fetch secrets from backend
    const response = await fetch('/api/vault');
    const data = await response.json();
    const secrets = data.secrets || [];
    const vault = {};
    for (const name of secrets) {
        const res = await fetch(`/api/vault/${encodeURIComponent(name)}`);
        if (res.ok) {
            const d = await res.json();
            vault[name] = d.content;
        }
    }
    let key;
    if (document.getElementById('vaultUseMsgKey')?.checked) {
        key = await getMsgKey();
    } else {
        const password = prompt('Enter password to encrypt vault:');
        if (!password) return;
        key = await deriveKey(password);
    }
    const iv = window.crypto.getRandomValues(new Uint8Array(12));
    const enc = new TextEncoder();
    const ciphertext = await window.crypto.subtle.encrypt(
        {name: 'AES-GCM', iv}, key, enc.encode(JSON.stringify(vault))
    );
    const payload = buf2b64(iv) + ':' + buf2b64(ciphertext);
    const blob = new Blob([payload], {type: 'text/plain'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'hashfi_vault.enc';
    document.body.appendChild(a);
    a.click();
    a.remove();
}

async function importVaultFile(event) {
    const file = event.target.files[0];
    if (!file) return;
    const payload = await file.text();
    if (!payload.includes(':')) return alert('Invalid vault file');
    let key;
    if (document.getElementById('vaultUseMsgKey')?.checked) {
        key = await getMsgKey();
    } else {
        const password = prompt('Enter password to decrypt vault:');
        if (!password) return;
        key = await deriveKey(password);
    }
    const [ivB64, ctB64] = payload.split(':');
    const iv = b642buf(ivB64);
    const ct = b642buf(ctB64);
    try {
        const pt = await window.crypto.subtle.decrypt(
            {name: 'AES-GCM', iv: new Uint8Array(iv)}, key, ct
        );
        const vault = JSON.parse(new TextDecoder().decode(pt));
        // Restore secrets to backend
        for (const [name, content] of Object.entries(vault)) {
            await fetch('/api/vault', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, content})
            });
        }
        alert('Vault imported!');
        loadSecrets();
    } catch (e) {
        alert('Decryption failed! Wrong password or corrupted file.');
    }
}
async function spreadTheWord() {
    const resultDiv = document.getElementById('spreadResult');
    resultDiv.style.display = 'block';
    resultDiv.innerText = 'Submitting...';
    try {
        const response = await fetch('/api/tools/spread', { method: 'POST' });
        if (response.ok) {
            const data = await response.json();
            resultDiv.innerText = data.message || 'Spread complete!';
        } else {
            const data = await response.json();
            resultDiv.innerText = 'Error: ' + (data.detail || 'Failed to spread.');
        }
    } catch (e) {
        resultDiv.innerText = 'Error: ' + e;
    }
}

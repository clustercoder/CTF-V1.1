require('dotenv').config();
const express = require('express');
const cookieParser = require('cookie-parser');
const fs = require('fs');
const crypto = require('crypto');
const path = require('path');

const app = express();
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

const PORT = process.env.PORT || 3000;
const FLAG_PASSPHRASE = process.env.FLAG_PASSPHRASE || 'dev_passphrase';
const ENC_FLAG_PATH = path.join(__dirname, 'flag.enc');
const ENC_FLAG = fs.existsSync(ENC_FLAG_PATH) ? fs.readFileSync(ENC_FLAG_PATH, 'utf8') : null;

// --- Helpers ---
const dblB64Encode = obj => Buffer.from(Buffer.from(JSON.stringify(obj)).toString('base64')).toString('base64');
const dblB64Decode = str => {
  try {
    return JSON.parse(Buffer.from(Buffer.from(str, 'base64').toString('utf8'), 'base64').toString('utf8'));
  } catch { return null; }
};

const fakeChecksum = obj => crypto.createHash('md5').update(`${obj.user}|${obj.role}|SALT_DO_NOT_USE`).digest('hex');

const decryptFlag = encBase64 => {
  const enc = Buffer.from(encBase64, 'base64');
  const key = crypto.createHash('sha256').update(FLAG_PASSPHRASE).digest();
  const iv = Buffer.alloc(16, 0);
  const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
  return Buffer.concat([decipher.update(enc), decipher.final()]).toString('utf8');
};

// --- Routes ---
app.get('/', (_, res) => res.sendFile(path.join(__dirname, 'public', 'index.html')));

app.post('/login', (req, res) => {
  const user = req.body.username?.trim() || 'guest';

  // nextStep encoded as Base64 hint for /admin/flag
  const payload = { user, role: 'user', nextStep: 'Y29uc3QgcGFydDEgPSAnYWRtJzsKY29uc3QgcGFydDIgPSAnaW4vZic7CmNvbnN0IHBhcnQzID0gJ2xhZyc7CmNvbnNvbGUubG9nKCdNYXliZSB0cnkgdmlzaXRpbmc6IC8nICsgcGFydDEgKyBwYXJ0MiArIHBhcnQzKTs=', checksum: fakeChecksum({ user, role: 'user' }) };
  res.cookie('uid_secure', dblB64Encode(payload), { httpOnly: false, sameSite: 'Lax' });

  res.json({ ok: true, message: 'logged in', next: '/profile' });
});

app.get('/profile', (_, res) => res.sendFile(path.join(__dirname, 'public', 'profile.html')));

app.get('/admin', (_, res) => res.sendFile(path.join(__dirname, 'public', 'admin.html')));

app.get('/admin/flag', (req, res) => {
  const raw = req.cookies['uid_secure'];
  if (!raw) return res.status(401).send('No credentials. Please log in.');

  const payload = dblB64Decode(raw);
  if (!payload) return res.status(400).send('Checksum mismatch.');

  if (payload.role !== 'admin') return res.status(403).send('Access denied. Admins only.');

  if (!ENC_FLAG) return res.status(500).send('Flag not configured.');

  try {
    res.send(`<h2>Admin flag</h2><pre>${decryptFlag(ENC_FLAG)}</pre>`);
  } catch {
    res.status(500).send('Flag decryption error.');
  }
});

app.get('/whoami', (req, res) => {
  const raw = req.cookies['uid_secure'];
  res.json({ cookie_raw: raw || null, parsed: raw ? dblB64Decode(raw) : null });
});

// --- Start server ---
app.listen(PORT, () => console.log(`Challenge running on port ${PORT}`));

require('dotenv').config();
const fs = require('fs');
const crypto = require('crypto');

const flag = fs.readFileSync('flag.txt', 'utf8');
const pass = process.env.FLAG_PASSPHRASE;

// Static IV and key derivation
const iv = Buffer.alloc(16, 0);
const key = crypto.createHash('sha256').update(pass).digest();

// Encrypt
const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
const encrypted = Buffer.concat([cipher.update(flag, 'utf8'), cipher.final()]);

fs.writeFileSync('flag.enc', encrypted.toString('base64'));
console.log('flag.enc created successfully');

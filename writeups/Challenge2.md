# Webbit 🍪 

**Challenge ID:** `webbit`
**Title:** Webbit 🍪
**Points:** 600
**Target:** `http://10.125.160.46:4000`

---


A login page accepts any username and sets a client-side cookie `uid_secure` that contains a **double-Base64-encoded JSON** object. The server authorizes admin-only access by reading the cookie on every request. The cookie contains `role`, and a weak integrity check (MD5 over `user|role|SALT_DO_NOT_USE`) is used. By editing the cookie to set `"role": "admin"`, recomputing the MD5 checksum using the same public salt, and double-Base64-encoding the JSON, we can access `/admin/flag` and retrieve the flag.

**Flag:** `GDG{c00k13_m0nst3r_l1k3s_c00k13s}`

---

# MAD (calculator_pro) — writeup

**Category:** reverse / binary / Android native
**Points:** 600
**Flag:** `GDG{c@1cU15}`

---

## TL;DR

The project in the provided ZIP is an Android app source tree. The Java `MainActivity` contains a short encrypted byte array and calls a native function that returns another byte array. The app concatenates the two arrays and XORs the result with the key `"12345"`. Extracting both arrays (one from the Java source and one from the shipped native library) and performing the XOR yields the flag `GDG{c@1cU15}`.

---

## Steps I took

### 1. Inspect the archive

I opened the uploaded `calculator_pro.zip` and listed files to see what kind of project it was (Android source, not an APK).

Key paths:

```
calculator_pro/app/src/main/java/clustercoder/calculator_pro/MainActivity.java
calculator_pro/app/src/main/jniLibs/armeabi-v7a/libhidden.so
```

### 2. Look at `MainActivity.java`

`MainActivity` has the core logic:

```java
static {
    System.loadLibrary("hidden");
}

private native byte[] getNativeFlagBytes();

protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);

    byte[] javaEncryptedFlag = new byte[]{0x76, 0x76, 0x74, 0x4F, 0x56};
    byte[] nativeEncryptedFlag = getNativeFlagBytes();

    byte[] combined = new byte[javaEncryptedFlag.length + nativeEncryptedFlag.length];
    System.arraycopy(javaEncryptedFlag, 0, combined, 0, javaEncryptedFlag.length);
    System.arraycopy(nativeEncryptedFlag, 0, combined, javaEncryptedFlag.length, nativeEncryptedFlag.length);

    byte[] key = "12345".getBytes();
    byte[] decrypted = new byte[combined.length];
    for (int i = 0; i < combined.length; i++) {
        decrypted[i] = (byte)(combined[i] ^ key[i % key.length]);
    }

    Log.d("HiddenFlag", new String(decrypted));
}
```

Observations:

* The app loads a native library `hidden`.
* It defines a small `javaEncryptedFlag` byte array.
* It appends `nativeEncryptedFlag` returned by the native code.
* It XORs the combined array with `"12345"` and logs the result.

So the flag is produced at runtime by XORing `(java_bytes || native_bytes)` with key `"12345"`.

### 3. Inspect the native library

The project contains a `libhidden.so` under `jniLibs/armeabi-v7a`. Extracting printable strings from the file revealed a `nativeBytes` array in the native code:

```c
jbyte nativeBytes[] = {0x71, 0x03, 0x50, 0x61, 0x04, 0x04, 0x4F};
```

(So the native part is 7 bytes long.)

### 4. Reconstruct and decrypt

Concatenate the Java bytes and native bytes, then XOR with ASCII `"12345"` (which are bytes: `0x31 0x32 0x33 0x34 0x35` repeated).

* Java bytes: `0x76 0x76 0x74 0x4F 0x56`
* Native bytes: `0x71 0x03 0x50 0x61 0x04 0x04 0x4F`
* Combined hex: `76 76 74 4f 56 71 03 50 61 04 04 4f`

Perform XOR with key bytes repeating (`'1' '2' '3' '4' '5'`):

I performed this quickly with Python; the core snippet used was:

```python
java = bytes([0x76,0x76,0x74,0x4F,0x56])
native = bytes([0x71,0x03,0x50,0x61,0x04,0x04,0x4F])
combined = java + native
key = b"12345"
decrypted = bytes([combined[i] ^ key[i % len(key)] for i in range(len(combined))])
print(decrypted.decode())
# -> GDG{c@1cU15}
```

This produced: `GDG{c@1cU15}`.

---

## Evidence / artifacts

* `MainActivity.java` (relevant lines):

  * `byte[] javaEncryptedFlag = new byte[]{0x76, 0x76, 0x74, 0x4F, 0x56};`
  * `byte[] nativeEncryptedFlag = getNativeFlagBytes();`
  * XOR key: `"12345"`

* `libhidden.so` (contained `nativeBytes`):

  * `jbyte nativeBytes[] = {0x71, 0x03, 0x50, 0x61, 0x04, 0x04, 0x4F};`

* Decryption result: `GDG{c@1cU15}`

---

## Final flag

```
GDG{c@1cU15}
```



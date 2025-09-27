# Challenge: Mosaic Pixels

**ID:** `mosaicpixels`  
**Title:** *Mosaic Pixels*  
**Points:** `600`

---

## Description
You've intercepted a classified transmission from a secret cyber lab. Buried inside is a digital message containing a highly sensitive secret. But the lab's AI security has scrambled the signal: the message has been fragmented into hundreds of pieces and camouflaged with the lab's signature emblem.  

Some fragments overlap, some hide beneath the emblem, and others appear incomplete. To make sense of the transmission, you'll need to observe patterns across the pieces and identify how the signal emerges when the fragments interact.  

Careful observation will reveal that the darkest marks carry the truth, while distractions in the background may mislead. Only by leveraging the collective behavior of the pieces will the hidden information become readable.  

This isn't just a puzzle — it's a test of precision, patience, and ingenuity. One misstep, one overlooked fragment, and the secret could remain hidden indefinitely.  

🔗 [Transmission Files](https://drive.google.com/drive/folders/1WoSBU00z35MbBBJJIigpkfDy-rCFCIt_?usp=sharing)

---

## Flag Hash
`hash_flag("GDG{Fr46M3N73D_P1X315_r3UN173D_6D6_25}")`



# Mosaic Pixels - CTF Writeup (Python/PIL Solution)

**Challenge:** Mosaic Pixels  
**Category:** Miscellaneous
**Difficulty:** Medium  
**Flag:** `GDG{Fr46M3N73D_P1X315_r3UN173D_6D6_25}`

## Challenge Description
We're given 100 image fragments, each containing partial QR code data overlaid with a club logo. The task is to reconstruct the complete QR code to obtain the flag.

## Analysis

Upon examining the fragments, several key observations emerge:
- Each fragment shows only portions of a QR code
- Black pixels represent actual QR data modules
- Club logo serves as visual noise/distraction  
- No single fragment contains complete information

The fragmentation pattern suggests we need to combine all pieces to reconstruct the original QR code.

## Solution Approach

The core insight is that QR reconstruction requires preserving **all black pixels** from **every fragment**. This can be achieved through logical OR operations or pixel-wise minimum functions.

### Method 1: Grayscale Reconstruction

```python
from PIL import Image
import glob
import numpy as np

pieces = sorted(glob.glob("piece_*.png"))
base = np.array(Image.open(pieces[0]).convert("L"))

for piece_path in pieces[1:]:
    img = np.array(Image.open(piece_path).convert("L"))
    base = np.minimum(base, img)  # Preserve darkest pixels

reconstructed = Image.fromarray(base)
reconstructed.save("reconstructed.png")
```

### Method 2: Color-Preserving Reconstruction

```python
from PIL import Image
import glob
import numpy as np

pieces = sorted(glob.glob("piece_*.png"))
base = np.array(Image.open(pieces[0]).convert("RGBA"))

for piece_path in pieces[1:]:
    img = np.array(Image.open(piece_path).convert("RGBA"))
    black_mask = np.all(img[:, :, :3] < 128, axis=2)
    base[black_mask] = [0, 0, 0, 255]  # Force black pixels

reconstructed = Image.fromarray(base)
reconstructed.save("reconstructed_color.png")
```

## Execution

Running either script produces a scannable QR code. Using any QR scanner on the reconstructed image reveals:

**Flag:** `GDG{Fr46M3N73D_P1X315_r3UN173D_6D6_25}`

## Challenge Design Notes

The puzzle incorporates several anti-trivial measures:
- **QR Version 13** (69x69 modules) for increased complexity
- **Low error correction** prevents partial reconstruction
- **Random patch overlays** ensure no single fragment is sufficient
- **Logo noise** requires signal separation skills

## Alternative Solutions

- **GIMP/Photoshop:** Layer all fragments with "Darken" blend mode
- **ImageMagick:** `convert piece_*.png -evaluate-sequence Min output.png`
- **Manual analysis:** Identify overlapping regions and trace QR patterns


# Mosaic Pixels - CTF Writeup (ImageMagick Solution)

**Challenge:** Mosaic Pixels  
**Category:** Miscellaneous  
**Difficulty:** Medium  
**Flag:** `GDG{Fr46M3N73D_P1X315_r3UN173D_6D6_25}`

## Challenge Description

We're presented with 100 fragmented images containing partial QR code data overlaid with a club logo. The objective is to reconstruct the complete QR code to extract the flag.

## Analysis

Initial examination reveals:

- Each fragment displays portions of a larger QR code
- Black pixels represent QR data modules
- Semi-transparent logo overlay creates visual interference
- Fragment distribution suggests complete reconstruction requires all pieces

The challenge centers on **pixel-level composition** where black pixels from any fragment must dominate in the final image.

## Solution: ImageMagick Approach

### Rationale

ImageMagick's `Darken` composition mode is ideal for this task - it preserves the darkest pixel value across all layers, ensuring black QR modules remain visible while filtering out lighter noise.

### Prerequisites

```bash
sudo apt update && sudo apt install imagemagick -y
convert -version  # Verify installation
```

### Execution

```bash
convert piece_*.png -compose Darken -flatten reconstructed.png
```

**Command breakdown:**

- `piece_*.png` - Wildcard matches all fragment files
- `-compose Darken` - Pixel-wise minimum operation across layers
- `-flatten` - Merges composition into single output image

### Verification

Scanning the reconstructed QR code yields:

**Flag:** `GDG{Fr46M3N73D_P1X315_r3UN173D_6D6_25}`

## Challenge Analysis

The puzzle incorporates several complexity factors:

- **QR Version 13** (69×69 modules) increases data density
- **Low error correction** prevents partial reconstruction success
- **100-fragment distribution** ensures comprehensive combination requirement
- **Logo overlay** tests noise filtering capabilities

## Edge Cases Handled

- **File ordering**: Glob pattern ensures consistent processing
- **Mixed formats**: ImageMagick handles format variations automatically
- **Memory constraints**: Stream processing prevents memory overflow
- **Output optimization**: PNG compression maintains quality

## Alternative Solutions

- **GIMP/Photoshop:** Layer all fragments with "Darken" blend mode
- **Python/PIL:** Pixel-wise minimum operations with NumPy arrays
- **Manual analysis:** Identify overlapping regions and trace QR patterns

---

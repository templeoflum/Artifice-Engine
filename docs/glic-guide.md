# GLIC Guide: Understanding Lossy Compression for Glitch Art

This guide explains how GLIC (GLitch Image Codec) works and how to use it for creative glitch art in Artifice.

## Table of Contents

- [What is GLIC?](#what-is-glic)
- [The Compression Pipeline](#the-compression-pipeline)
- [Quick Start](#quick-start)
- [Understanding Each Stage](#understanding-each-stage)
- [Glitch Techniques](#glitch-techniques)
- [Advanced Workflows](#advanced-workflows)
- [Troubleshooting](#troubleshooting)

---

## What is GLIC?

GLIC is a lossy image codec inspired by formats like JPEG, but designed specifically for glitch art. Unlike codecs optimized for quality, GLIC exposes every compression stage so you can intentionally introduce artifacts.

**Key concept:** All lossy compression works by:
1. Transforming data into a more compressible form
2. Throwing away "unimportant" information
3. Reconstructing an approximation of the original

The "glitch" comes from step 2 - by controlling *what* gets thrown away and *how much*, you create predictable visual artifacts.

---

## The Compression Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GLIC ENCODE                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Image → Color Space → Segment → Predict → Residual → Quantize        │
│             (YCbCr)     (Quadtree)  (PAETH)   (subtract)  (reduce)     │
│                                                                         │
│   "Make it      "Divide into   "Guess what   "Store the   "Round off   │
│    easier to     variable-size   each block    error"       the error"  │
│    compress"     blocks"         should be"                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                            [Quantized Data]
                            [Segment Map]
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         GLIC DECODE                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Dequantize → Predict → Reconstruct → Color Space                     │
│    (expand)    (same)    (add back)     (RGB)                          │
│                                                                         │
│   "Restore the  "Make the     "Combine      "Convert back              │
│    rounded       same guess"   guess+error"  to display"               │
│    values"                                                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Minimal Setup

1. Create these nodes and connect them:
   ```
   Test Card → GLIC Encode ──┬──(quantized_int)──→ GLIC Decode → (preview)
                             └──(segments)────────→
   ```

2. Connect both `quantized_int` AND `segments` from Encode to Decode

3. Press **Shift+E** to execute

4. You should see the test card reconstructed (with default settings, nearly identical)

### First Glitch

1. Select the **GLIC Encode** node
2. In the Inspector, change **Quantization Bits** from 8 to **3**
3. Press **Shift+E**
4. Notice the posterization/banding - this is quantization error!

### More Glitch

1. Change **Predictor** from PAETH to **BSAD (Worst)**
2. Press **Shift+E**
3. The image should look significantly more corrupted

---

## Understanding Each Stage

### 1. Color Space Conversion

**What it does:** Converts RGB to YCbCr (or other color spaces)

**Why it matters:** YCbCr separates brightness (Y) from color (Cb, Cr). Human eyes are more sensitive to brightness than color, so:
- Glitches in Y channel are very visible
- Glitches in Cb/Cr channels affect color but preserve structure

**Parameters:**
- **RGB** - No separation, uniform glitching
- **YCbCr** - Classic JPEG-style artifacts
- **LAB** - Perceptually uniform, interesting color glitches

### 2. Segmentation (Quadtree)

**What it does:** Divides the image into variable-sized blocks

**Why it matters:** Large uniform areas get big blocks (efficient). Detailed areas get small blocks (preserve edges).

**Parameters:**
- **Min Segment Size (4-64)** - Smallest allowed block
- **Max Segment Size (64-512)** - Largest allowed block
- **Threshold (0.1-100)** - How much variance triggers subdivision

**Glitch effects:**
- Low threshold → many small blocks → fine detail preserved
- High threshold → few large blocks → blocky, compressed look
- Very high threshold + low min size → visible block boundaries

### 3. Prediction

**What it does:** For each block, *guesses* what the pixels should be based on neighboring pixels.

**Why it matters:** If the guess is good, the actual values are similar to the guess. Storing the small *difference* (residual) takes less data than storing the full values.

**Predictors ranked by quality:**

| Predictor | Quality | Glitch Potential |
|-----------|---------|------------------|
| SAD (Best) | Excellent | Low - auto-selects best |
| PAETH | Very Good | Low - PNG algorithm |
| MEDIAN | Good | Low |
| H, V, AVG | Moderate | Medium |
| NONE | Poor | High - no prediction |
| BSAD (Worst) | Terrible | Very High - auto-selects worst |

**BSAD** is specifically designed for glitch art - it deliberately picks the worst predictor for each block, maximizing residual values and thus maximizing quantization error.

### 4. Residual Calculation

**What it does:** `residual = actual_image - predicted_image`

**Why it matters:** If prediction is good, residuals are small (close to zero). If prediction is bad, residuals are large (similar to original image).

**Clamp methods:**
- **NONE** - Keep full range (-1.0 to 1.0), standard for lossless roundtrip
- **MOD256** - Wrap to 0-1 range, different visual aesthetic

### 5. Quantization

**What it does:** Reduces precision by rounding values to discrete levels.

**Why it matters:** This is where information is permanently lost. The fewer bits, the fewer levels, the more rounding error.

**Bit depth effects:**

| Bits | Levels | Visual Effect |
|------|--------|---------------|
| 8 | 256 | Near-invisible loss |
| 6 | 64 | Subtle banding in gradients |
| 4 | 16 | Visible posterization |
| 3 | 8 | Heavy posterization |
| 2 | 4 | Extreme color reduction |
| 1 | 2 | Binary (black/white + midtones) |

---

## Glitch Techniques

### Technique 1: Posterization

**Goal:** Banding and color reduction

**Settings:**
- Predictor: SAD (Best) or PAETH
- Quantization Bits: 2-4
- Color Space: YCbCr or LAB

**Why it works:** Good prediction means small residuals. Aggressive quantization rounds these small values, creating visible steps.

### Technique 2: Prediction Failure

**Goal:** Chaotic, unpredictable artifacts

**Settings:**
- Predictor: BSAD (Worst) or RANDOM
- Quantization Bits: 4-6
- Color Space: YCbCr

**Why it works:** Bad prediction means large residuals. Quantization error on large values creates dramatic color shifts and block artifacts.

### Technique 3: Block Boundaries

**Goal:** Visible grid/mosaic effect

**Settings:**
- Min Segment Size: 16-32
- Max Segment Size: 32-64
- Segment Threshold: 50-100
- Quantization Bits: 4-6

**Why it works:** Large, uniform blocks make prediction work differently at boundaries, creating visible edges between blocks.

### Technique 4: Channel-Specific Glitching

**Goal:** Preserve structure, corrupt color (or vice versa)

**Workflow:**
1. GLIC Encode with YCbCr
2. Use individual Prediction/Residual/Quantize nodes
3. Apply different quantization to each channel
4. Reconstruct

**Example:** Quantize Y at 8 bits (clean), Cb/Cr at 2 bits (corrupted color, clean edges)

### Technique 5: Data Corruption

**Goal:** Random artifacts and glitches

**Workflow:**
1. GLIC Encode
2. Connect `quantized_int` through a corruption node (Bit Flip, XOR Noise, etc.)
3. Connect corrupted output to GLIC Decode

**Why it works:** Corrupting quantized data creates unpredictable values that decode into unexpected colors and patterns.

---

## Advanced Workflows

### Workflow A: Intentional Mismatch

Use different settings for encode vs decode:

```
GLIC Encode (PAETH, 8 bits) → GLIC Decode (BSAD, 4 bits)
```

The decoder reconstructs with wrong parameters, creating unique artifacts.

### Workflow B: Iterative Encoding

Run the image through GLIC multiple times:

```
Image → GLIC Encode/Decode → GLIC Encode/Decode → GLIC Encode/Decode → Output
```

Each pass accumulates more quantization error, like generation loss in analog video.

### Workflow C: Selective Processing

Use the intermediate outputs:

```
GLIC Encode ──→ residuals ──→ Pixel Sort ──→ (manual reconstruction)
           └──→ predicted ──→ Color Space ──→ (use as mask or blend)
```

### Workflow D: Hybrid Glitching

Combine GLIC with other transforms:

```
Image → Wavelet Transform → Wavelet Compress → Inverse Wavelet → GLIC Encode/Decode
```

or

```
Image → GLIC Encode → (corrupt data) → GLIC Decode → DCT → (modify) → Inverse DCT
```

---

## Troubleshooting

### Image looks unchanged

- Quantization bits may be too high (8 is nearly lossless)
- Try lowering to 4-5 bits
- Or switch predictor to BSAD

### Image is completely destroyed

- Quantization bits too low (1-2 is extreme)
- Try 4-6 bits for usable glitches
- Or use a better predictor (PAETH, SAD)

### Decode produces wrong colors

- Check that Encode and Decode have matching:
  - Colorspace
  - Predictor
  - Quantization Bits
- Intentional mismatch creates glitches, but unintentional mismatch creates garbage

### Processing is slow

- Decrease image size while experimenting
- Increase Min Segment Size (fewer blocks to process)
- Increase Segment Threshold (larger blocks, fewer total)

### Artifacts are too uniform/boring

- Try RANDOM predictor for variety
- Add corruption nodes between encode/decode
- Use different settings per channel

---

## Parameter Cheat Sheet

| Goal | Colorspace | Predictor | Bits | Threshold |
|------|------------|-----------|------|-----------|
| Subtle banding | YCbCr | PAETH | 5-6 | 10 |
| Heavy posterization | RGB | SAD | 2-3 | 10 |
| Block artifacts | YCbCr | BSAD | 4-5 | 50+ |
| Color corruption | LAB | BSAD | 3-4 | 10 |
| Maximum chaos | RGB | RANDOM | 2 | 100 |
| Clean preview | YCbCr | SAD | 8 | 10 |

---

*For complete node documentation, see [Node Reference](node-reference.md).*

*Converse with Chaos, Sculpt Emergence.*

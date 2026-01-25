# Artifice Node Specifications

Complete reference for all nodes in Artifice, including parameters, inputs, outputs, and usage notes.

---

## Table of Contents

- [I/O Nodes](#io-nodes)
- [Generator Nodes](#generator-nodes)
- [Color Nodes](#color-nodes)
- [GLIC Nodes](#glic-nodes)
- [Quantization Nodes](#quantization-nodes)
- [Transform Nodes](#transform-nodes)
- [Corruption Nodes](#corruption-nodes)

---

## I/O Nodes

### Image Loader

Load images from disk.

| Property | Value |
|----------|-------|
| **Inputs** | None |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `path` | filepath | - | - | Path to image file (PNG, JPG, TIFF, WebP, BMP, GIF) |

---

### Image Saver

Save images to disk.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | None |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `path` | filepath | - | - | Output path |
| `format` | enum | PNG | PNG, JPG, TIFF, WebP, BMP | Output format |
| `quality` | int | 95 | 1-100 | JPEG quality (only for JPG) |

---

## Generator Nodes

### Test Card

Procedural calibration image for testing effects.

| Property | Value |
|----------|-------|
| **Inputs** | None |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `width` | int | 1024 | 64-4096 | Output width |
| `height` | int | 1024 | 64-4096 | Output height |
| `pattern` | enum | Full | Full, Bars, Checkerboard, Gradient, ZonePlate, Noise | Pattern type |

**Test Card Regions:**
- Color bars (RGBCMYK) - test color/channel operations
- Checkerboard (8×8, 16×16) - test frequency/DCT/FFT effects
- Diagonal lines - test directional operations
- Zone plate - test frequency response/aliasing
- Step wedge - test quantization
- Radial gradient - test circular operations
- Perlin noise - test segmentation
- Rainbow hue sweep - test color space conversions
- Grayscale gradient - test tonal response

---

### Noise

Generate procedural noise patterns.

| Property | Value |
|----------|-------|
| **Inputs** | None |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `width` | int | 1024 | 64-4096 | Output width |
| `height` | int | 1024 | 64-4096 | Output height |
| `noise_type` | enum | Perlin | Perlin, Simplex, White, Value | Noise algorithm |
| `scale` | float | 1.0 | 0.01-100.0 | Noise scale/frequency |
| `octaves` | int | 4 | 1-8 | Fractal octaves |
| `persistence` | float | 0.5 | 0.0-1.0 | Amplitude decay per octave |
| `seed` | int | 0 | 0-999999 | Random seed |

---

## Color Nodes

### Color Space

Convert between all 16 GLIC color spaces.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `from_space` | enum | RGB | Source color space |
| `to_space` | enum | YCbCr | Target color space |

**Available Color Spaces:**

| ID | Name | Category | Description |
|----|------|----------|-------------|
| 0 | RGB | Standard | Red, Green, Blue |
| 1 | HSV | Artist | Hue, Saturation, Value |
| 2 | HSL | Artist | Hue, Saturation, Lightness |
| 3 | YCbCr | Video | JPEG/MPEG luma-chroma |
| 4 | YUV | Video | Analog video standard |
| 5 | LAB | Perceptual | CIE L*a*b* (perceptually uniform) |
| 6 | XYZ | Scientific | CIE 1931 device-independent |
| 7 | LUV | Perceptual | CIE L*u*v* |
| 8 | HCL | Perceptual | Cylindrical LAB (Hue-Chroma-Luma) |
| 9 | CMY | Special | Cyan-Magenta-Yellow (subtractive) |
| 10 | HWB | Artist | Hue-Whiteness-Blackness (CSS) |
| 11 | YPbPr | Video | Component video |
| 12 | YDbDr | Video | SECAM standard |
| 13 | OHTA | Special | Optimal color features |
| 14 | YXY | Scientific | CIE chromaticity coordinates |
| 15 | GREY | Special | Grayscale (luma only) |

**Usage Notes:**
- YCbCr, LAB, LUV separate luma from chroma - ideal for glitch effects
- Corrupt chroma channels while preserving luma for structured glitches
- HSV/HSL provide intuitive artistic control

---

### Channel Split

Separate image into individual color channels.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `channel_r`, `channel_g`, `channel_b`, `channel_a` |

**Parameters:** None

---

### Channel Merge

Combine separate channels into a single image.

| Property | Value |
|----------|-------|
| **Inputs** | `channel_r`, `channel_g`, `channel_b`, `channel_a` (optional) |
| **Outputs** | `image` |

**Parameters:** None

---

### Channel Swap

Reorder color channels.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Options | Description |
|------|------|---------|---------|-------------|
| `red_source` | enum | Red | Red, Green, Blue, Alpha, Zero, One | Source for red channel |
| `green_source` | enum | Green | Red, Green, Blue, Alpha, Zero, One | Source for green channel |
| `blue_source` | enum | Blue | Red, Green, Blue, Alpha, Zero, One | Source for blue channel |
| `alpha_source` | enum | Alpha | Red, Green, Blue, Alpha, Zero, One | Source for alpha channel |

---

### Blend

Blend two images together.

| Property | Value |
|----------|-------|
| **Inputs** | `image_a`, `image_b` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `mode` | enum | Normal | Normal, Add, Multiply, Screen, Overlay, Difference, Exclusion | Blend mode |
| `opacity` | float | 1.0 | 0.0-1.0 | Blend opacity |

---

### Invert

Invert image colors.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `invert_r` | bool | true | Invert red channel |
| `invert_g` | bool | true | Invert green channel |
| `invert_b` | bool | true | Invert blue channel |
| `invert_a` | bool | false | Invert alpha channel |

---

### Brightness/Contrast

Adjust image brightness and contrast.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `brightness` | float | 0.0 | -1.0-1.0 | Brightness adjustment |
| `contrast` | float | 1.0 | 0.0-3.0 | Contrast multiplier |

---

### Threshold

Convert to binary or multi-level threshold.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `threshold` | float | 0.5 | 0.0-1.0 | Threshold level |
| `smoothness` | float | 0.0 | 0.0-0.5 | Edge smoothness |

---

### Posterize

Reduce color levels.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `levels` | int | 4 | 2-256 | Number of color levels |

---

## GLIC Nodes

The GLIC (Glitch Codec) nodes implement a predictive coding system that can be deliberately "broken" to create structured glitch effects.

### GLIC Predict

Generate predictions using GLIC predictors.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` (prediction) |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `block_size` | int | 16 | 4, 8, 16, 32, 64 | Prediction block size |
| `predictor_mode` | enum | Paeth | See below | Predictor algorithm |
| `border_value` | float | 0.5 | 0.0-1.0 | Value for pixels outside image |
| `seed` | int | 0 | 0-999999 | Random seed (for Random mode) |

**Predictor Modes:**

| ID | Name | Description |
|----|------|-------------|
| 0 | None | No prediction (outputs zeros) |
| 1 | Corner | Uses top-left corner pixel |
| 2 | Horizontal | Uses pixel to the left |
| 3 | Vertical | Uses pixel above |
| 4 | DC Mean | Average of surrounding pixels |
| 5 | DC Median | Median of surrounding pixels |
| 6 | Median | Median of left, top, top-left |
| 7 | Average | Average of left and top |
| 8 | TrueMotion | Left + top - top-left |
| 9 | Paeth | PNG-style adaptive predictor |
| 10 | Linear Diag | Linear interpolation on diagonal |
| 11 | H/V Position | Horizontal or vertical based on position |
| 12 | JPEG-LS | JPEG-LS MED predictor |
| 13 | Difference | Difference between neighbors |
| 14 | **SAD (Best)** | Auto-select BEST predictor per block |
| 15 | **BSAD (Worst)** | Auto-select WORST predictor per block (glitch!) |
| 16 | Random | Random predictor per block |

**Usage Notes:**
- **BSAD mode** is the key to GLIC-style glitches - it deliberately picks the predictor that produces MAXIMUM error
- Combine with Quantize (signed mode) and GLIC Reconstruct for full effect

---

### GLIC Residual

Calculate residuals (difference between image and prediction).

| Property | Value |
|----------|-------|
| **Inputs** | `image`, `prediction` |
| **Outputs** | `image` (residual) |

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `method` | enum | Subtract | Residual calculation method |

**Residual Methods:**

| Name | Description |
|------|-------------|
| Subtract | Simple subtraction: image - prediction |
| Clamp | Clamped subtraction (0-1 range) |
| Wrap | Wrapped subtraction (wraps around) |
| CLAMP_MOD256 | GLIC-style: clamp then mod 256 (creates color shifts) |

---

### GLIC Reconstruct

Reconstruct image from prediction and residuals.

| Property | Value |
|----------|-------|
| **Inputs** | `prediction`, `residual` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `method` | enum | Add | Reconstruction method (should match residual method) |

---

## Quantization Nodes

### Quantize

Reduce color precision with optional dithering.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `bits` | int | 8 | 1-16 | Bit depth (1=binary, 8=256 levels) |
| `signed` | enum | Unsigned | Unsigned, Signed | Range mode |
| `mode` | enum | Uniform | Uniform, Adaptive | Quantization distribution |
| `dither` | enum | Off | Off, Bayer, Blue Noise | Dithering algorithm |
| `dither_strength` | float | 1.0 | 0.0-2.0 | Dithering intensity |

**Usage Notes:**
- **Signed mode** is essential for GLIC residual encoding (-1 to 1 range)
- **Adaptive mode** places more levels near common values
- **Blue Noise dither** produces the most aesthetically pleasing results
- Low bit depths (1-4) create dramatic posterization
- Use with GLIC Predict/Reconstruct for codec-style glitches

---

## Transform Nodes

### Pixel Sort

Sort pixels within rows or columns.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `threshold_mode` | enum | Brightness | Brightness, Random, None | How to determine sortable regions |
| `threshold_low` | float | 0.25 | 0.0-1.0 | Lower threshold bound |
| `threshold_high` | float | 0.8 | 0.0-1.0 | Upper threshold bound |
| `sort_by` | enum | Brightness | Brightness, Hue, Saturation, Red, Green, Blue | Sort criterion |
| `direction` | enum | Horizontal | Horizontal, Vertical | Sort direction |
| `reverse_sort` | enum | Ascending | Ascending, Descending | Sort order |
| `seed` | int | 0 | 0-999999 | Random seed (for Random threshold mode) |

**Threshold Modes:**
- **Brightness**: Sort pixels within brightness threshold range
- **Random**: Randomly determine segment boundaries
- **None**: Sort entire rows/columns

---

### DCT

Discrete Cosine Transform (JPEG-style).

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `block_size` | int | 8 | 4, 8, 16, 32 | DCT block size |
| `quality` | float | 1.0 | 0.0-2.0 | Quality factor (affects coefficient scaling) |
| `inverse` | bool | false | - | Apply inverse DCT |

---

### FFT

Fast Fourier Transform for frequency domain manipulation.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `inverse` | bool | false | - | Apply inverse FFT |
| `shift` | bool | true | - | Center zero frequency |
| `log_scale` | bool | true | - | Logarithmic magnitude display |

---

### Wavelet

Wavelet transform decomposition.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `wavelet` | enum | Haar | Haar, Daubechies | Wavelet type |
| `levels` | int | 3 | 1-6 | Decomposition levels |
| `inverse` | bool | false | - | Apply inverse transform |
| `threshold` | float | 0.0 | 0.0-1.0 | Coefficient threshold (compression) |

---

### Mirror

Mirror/flip image.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `axis` | enum | Horizontal | Horizontal, Vertical, Both | Mirror axis |

---

### Rotate

Rotate image.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `angle` | float | 0.0 | 0-360 | Rotation angle (degrees) |
| `expand` | bool | false | - | Expand canvas to fit rotated image |

---

### Blur

Apply blur effect.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `radius` | float | 2.0 | 0.0-50.0 | Blur radius |
| `type` | enum | Gaussian | Gaussian, Box, Bilateral | Blur type |

---

### Sharpen

Apply sharpening effect.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `amount` | float | 1.0 | 0.0-5.0 | Sharpening strength |
| `radius` | float | 1.0 | 0.5-10.0 | Effect radius |

---

### Edge Detect

Detect edges in image.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `method` | enum | Sobel | Sobel, Prewitt, Laplacian, Canny | Edge detection algorithm |
| `threshold` | float | 0.1 | Edge threshold (for Canny) |

---

## Corruption Nodes

### Bit Flip

Toggle specific bits in pixel data.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `bit_position` | int | 7 | 0-7 | Which bit to flip (0=LSB, 7=MSB) |
| `probability` | float | 0.5 | 0.0-1.0 | Probability of flipping each pixel |
| `channel_mask` | int | 7 | 0-15 | Channels to affect (bitfield: 1=R, 2=G, 4=B, 8=A) |
| `seed` | int | 0 | 0-999999 | Random seed |

**Usage Notes:**
- High bits (7, 6) create dramatic changes
- Low bits (0, 1) create subtle noise
- Combine with color space conversion for interesting effects

---

### Bit Shift

Shift bits left or right.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `shift_amount` | int | 1 | -7 to 7 | Bits to shift (negative=left, positive=right) |
| `rotate` | bool | false | - | Rotate bits instead of truncating |
| `channel_mask` | int | 7 | 0-15 | Channels to affect |

---

### XOR Noise

XOR pixel data with noise patterns.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `noise_scale` | float | 1.0 | 0.01-100.0 | Noise pattern scale |
| `intensity` | float | 1.0 | 0.0-1.0 | Effect intensity |
| `seed` | int | 0 | 0-999999 | Random seed |

---

### Data Repeat

Repeat rows or columns of data.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `repeat_size` | int | 8 | 1-128 | Size of repeated segment |
| `direction` | enum | Horizontal | Horizontal, Vertical | Repeat direction |
| `offset` | int | 0 | 0-256 | Starting offset |

---

### Data Drop

Skip/drop rows or columns of data.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `drop_size` | int | 4 | 1-64 | Size of dropped segment |
| `keep_size` | int | 12 | 1-64 | Size of kept segment |
| `direction` | enum | Horizontal | Horizontal, Vertical | Drop direction |

---

### Data Scramble

Shuffle data segments.

| Property | Value |
|----------|-------|
| **Inputs** | `image` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `block_size` | int | 16 | 4-128 | Scramble block size |
| `direction` | enum | Horizontal | Horizontal, Vertical, Both | Scramble direction |
| `seed` | int | 0 | 0-999999 | Random seed |

---

### Data Weave

Interleave two images.

| Property | Value |
|----------|-------|
| **Inputs** | `image`, `image_b` |
| **Outputs** | `image` |

**Parameters:**

| Name | Type | Default | Range | Description |
|------|------|---------|-------|-------------|
| `weave_size` | int | 4 | 1-128 | Width of weave stripes |
| `direction` | enum | Horizontal | Horizontal, Vertical, Checker | Weave pattern |
| `blend_width` | float | 0.0 | 0.0-1.0 | Edge blend smoothness |
| `mix_amount` | float | 0.5 | 0.0-1.0 | Balance between images |
| `offset` | int | 0 | 0-256 | Pattern offset |

**Usage Notes:**
- Interleave different processed versions of the same image
- Create scanline effects with small weave_size
- Checker pattern creates pixel-level mixing

---

## Pipeline Examples

### Classic GLIC Glitch

```
Test Card → Color Space (RGB→YCbCr) → GLIC Predict (BSAD) →
GLIC Residual → Quantize (4 bits, Signed) → GLIC Reconstruct →
Color Space (YCbCr→RGB)
```

### Pixel Sort with Threshold

```
Image Loader → Color Space (RGB→HSV) → Pixel Sort (Brightness, 0.2-0.7) →
Color Space (HSV→RGB) → Image Saver
```

### Bit Corruption Chain

```
Test Card → Bit Flip (bit 6, prob 0.3) → Bit Shift (2, rotate) →
XOR Noise (scale 5.0) → Quantize (6 bits, Bayer dither)
```

### Dual Image Weave

```
Image A ─┬→ Bit Flip ─┬→ Data Weave (Checker, size 8) → Output
         │            │
Image B ─┴→ Blur ─────┘
```

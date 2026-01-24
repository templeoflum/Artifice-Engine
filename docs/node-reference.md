# Node Reference

Complete documentation for all 33 nodes in Artifice, organized by category.

---

## Table of Contents

- [I/O](#io)
- [Generator](#generator)
- [Color](#color)
- [Segmentation](#segmentation)
- [Prediction](#prediction)
- [Quantization](#quantization)
- [Transform](#transform)
- [Corruption](#corruption)
- [Pipeline](#pipeline)
- [Utility](#utility)

---

## I/O

Nodes for loading and saving images.

### Image Loader

Load an image file from disk.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Output | IMAGE | Loaded image data |

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| file_path | FILEPATH | (empty) | Path to image file |

**Supported formats:** PNG, JPG, JPEG, TIFF, TIF, WebP, BMP, GIF

**Notes:**
- RGBA images are composited over black to produce RGB
- Grayscale images are converted to 3-channel RGB
- Default browse location is the user's Pictures directory

---

### Image Saver

Save an image to disk.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Image to save |

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| file_path | FILEPATH | (empty) | Output file path |
| format | ENUM | PNG | Output format (PNG, JPG, TIFF, WebP, BMP) |

**Notes:**
- Creates parent directories if they don't exist
- Default save location is the project's `output/` folder
- JPG quality is fixed at 95%

---

## Generator

Nodes that create images procedurally.

### Test Card

Generate a procedural test card for calibration and effect visualization.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Output | IMAGE | Generated test card |

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| width | INT | 512 | 16-4096 | Image width in pixels |
| height | INT | 512 | 16-4096 | Image height in pixels |

**Test card sections (from top to bottom, left to right):**

1. **Color bars (RGBCMYWK)** - Test color/channel operations
2. **Checkerboard 8x8** - Test frequency/DCT/FFT effects
3. **Checkerboard 16x16** - Test frequency response
4. **Diagonal lines** - Test directional operations (pixel sort, wavelets)
5. **Zone plate** - Concentric sine rings for frequency response/aliasing
6. **Step wedge** - Discrete gray levels for quantization testing
7. **Radial gradient** - Test smooth gradients and circular operations
8. **Perlin noise** - Test segmentation and texture effects
9. **Rainbow hue sweep** - Test color space conversions
10. **Grayscale gradient** - Test tonal response

---

## Color

Nodes for color space conversion and channel manipulation.

### Color Space

Convert between color spaces.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| image | Output | IMAGE | Converted image |

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| target | ENUM | RGB | Target color space |

**Supported color spaces:**

| Color Space | Description | Use Case |
|-------------|-------------|----------|
| RGB | Red, Green, Blue | Default, display |
| HSB | Hue, Saturation, Brightness | Color manipulation |
| YCbCr | Luma + Chroma | JPEG-style compression, glitch art |
| YUV | Luma + Chroma (analog) | Video processing |
| LAB | Perceptual lightness + color | Perceptual effects |
| XYZ | CIE 1931 color space | Color science |
| LUV | Perceptual uniform | Color analysis |
| HCL | Hue, Chroma, Lightness | Perceptual color picking |
| CMY | Cyan, Magenta, Yellow | Print simulation |
| HWB | Hue, Whiteness, Blackness | Intuitive color |
| YDbDr | SECAM color space | Broadcast simulation |
| YXY | CIE xyY | Chromaticity |
| YPbPr | Component video | Analog video |
| OHTA | I1, I2, I3 opponent colors | Image analysis |
| R-GGB-G | Red, G-GB, G-B difference | Research |
| GREY | Grayscale | Luma extraction |

**Notes:**
- YCbCr is recommended for GLIC-style glitching (separates brightness from color)
- LAB produces interesting perceptual color glitches
- GREY is lossy (discards color information)

---

### Channel Split

Split an image into separate single-channel images.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| channel_0 | Output | IMAGE | First channel (R, H, Y, etc.) |
| channel_1 | Output | IMAGE | Second channel (G, S, Cb, etc.) |
| channel_2 | Output | IMAGE | Third channel (B, V/B, Cr, etc.) |

**Notes:**
- Output channels are single-channel (grayscale) images
- Useful for processing channels independently

---

### Channel Merge

Combine separate channels into a single image.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| channel_0 | Input | IMAGE | First channel |
| channel_1 | Input | IMAGE | Second channel |
| channel_2 | Input | IMAGE | Third channel |
| image | Output | IMAGE | Combined image |

**Notes:**
- Input channels should be single-channel images
- Channels are combined in order (0, 1, 2)

---

### Channel Swap

Rearrange image channels.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| image | Output | IMAGE | Swapped image |

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| channel_0 | ENUM | R | Source for output channel 0 |
| channel_1 | ENUM | G | Source for output channel 1 |
| channel_2 | ENUM | B | Source for output channel 2 |

**Channel options:** R, G, B

**Example uses:**
- `R, B, G` - Swap green and blue
- `B, G, R` - Reverse channel order
- `R, R, R` - Convert to grayscale (red channel only)

---

## Segmentation

Nodes that divide images into regions.

### Quadtree Segment

Content-adaptive quadtree segmentation.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| segments | Output | SEGMENTS | Segment list |
| visualization | Output | IMAGE | Segmentation visualization |

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| min_size | INT | 4 | 2-64 | Minimum segment size |
| max_size | INT | 64 | 4-512 | Maximum segment size |
| threshold | FLOAT | 10.0 | 0.1-100 | Variance threshold for subdivision |
| criterion | ENUM | variance | | Subdivision criterion |

**Criteria options:**
- **variance** - Subdivide if pixel variance exceeds threshold
- **edge** - Subdivide if edge content exceeds threshold
- **gradient** - Subdivide if gradient magnitude exceeds threshold

**How it works:**
1. Start with the whole image as one segment
2. Calculate criterion (variance/edge/gradient) for each segment
3. If criterion exceeds threshold and segment > min_size, subdivide into 4
4. Repeat until all segments are below threshold or at min_size

**Tips:**
- Lower threshold = more segments = finer detail preserved
- Higher threshold = fewer segments = blockier, more compressed
- The visualization output shows segment boundaries

---

## Prediction

GLIC-style prediction nodes for lossy compression and glitch art.

### Predict

Generate predictions for image segments based on neighboring pixels.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| segments | Input | SEGMENTS | Segment list from Quadtree |
| predicted | Output | IMAGE | Predicted image |

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| predictor | ENUM | PAETH | Prediction algorithm |

**Core Predictors (16 types):**

| Predictor | Description | Glitch Potential |
|-----------|-------------|------------------|
| NONE | No prediction (all zeros) | High - raw quantization |
| CORNER | Top-left corner pixel | Medium |
| H | Horizontal (left neighbor) | Low - good for horizontal gradients |
| V | Vertical (top neighbor) | Low - good for vertical gradients |
| DC | Average of all border pixels | Low - good for uniform areas |
| DCMEDIAN | Median of DC predictions | Low |
| MEDIAN | Median of H, V, corner | Low |
| AVG | Average of H and V | Low |
| TRUEMOTION | Motion-compensated | Medium |
| PAETH | PNG-style adaptive | Very Low - best general predictor |
| LDIAG | Left diagonal | Medium |
| HV | Horizontal or vertical (adaptive) | Low |
| JPEGLS | JPEG-LS predictor | Low |
| DIFF | Difference-based | Medium |
| REF | Reference-based | Medium |
| ANGLE | Angle-based prediction | Medium |

**Meta Predictors (3 types):**

| Predictor | Description | Use Case |
|-----------|-------------|----------|
| SAD (Best) | Auto-select best predictor per block | Clean compression |
| BSAD (Worst) | Auto-select worst predictor per block | Intentional glitch |
| RANDOM | Random predictor per block | Chaotic glitch |

**Tips:**
- **PAETH** or **SAD** for clean results
- **BSAD** for intentional visual glitching
- **NONE** for maximum quantization artifacts

---

### Residual

Calculate the difference between actual image and prediction.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| actual | Input | IMAGE | Original image |
| predicted | Input | IMAGE | Predicted image |
| residual | Output | IMAGE | Residual (actual - predicted) |

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| clamp_method | ENUM | NONE | How to handle residual range |

**Clamp methods:**
- **NONE** - Keep full range (-1.0 to 1.0). Standard for lossless roundtrip.
- **MOD256** - Wrap to 0-1 range using modulo. Creates different glitch aesthetic.

**Notes:**
- Good predictions produce small residuals (close to zero)
- Bad predictions produce large residuals (similar to original image)
- Residuals are what get quantized and stored in GLIC compression

---

### Reconstruct

Reconstruct image from residuals and predictions.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| residual | Input | IMAGE | Residual image |
| predicted | Input | IMAGE | Predicted image |
| reconstructed | Output | IMAGE | Reconstructed image |

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| clamp_method | ENUM | NONE | Must match Residual node setting |

**Notes:**
- reconstructed = predicted + residual
- Use matching clamp_method as the Residual node for proper reconstruction

---

## Quantization

Nodes for reducing precision (lossy compression).

### Quantize

Reduce values to a limited number of discrete levels.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| quantized | Output | IMAGE | Quantized image |
| quantized_int | Output | ARRAY | Integer quantized values |

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| bit_depth | INT | 8 | 1-16 | Number of bits (2^n levels) |
| signed | BOOL | False | | Use signed quantization |

**Bit depth effects:**
- **8 bits** = 256 levels (near-lossless)
- **6 bits** = 64 levels (subtle banding)
- **4 bits** = 16 levels (visible posterization)
- **2 bits** = 4 levels (extreme posterization)
- **1 bit** = 2 levels (binary/threshold)

**Notes:**
- Lower bit depth = more data loss = more glitch potential
- Use `signed=True` when quantizing residuals (which can be negative)

---

### Dequantize

Restore values from quantized form.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| quantized_int | Input | ARRAY | Integer quantized values |
| image | Output | IMAGE | Reconstructed image |

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| bit_depth | INT | 8 | Must match Quantize node |
| signed | BOOL | False | Must match Quantize node |

---

## Transform

Frequency-domain and sorting transforms.

### DCT

Discrete Cosine Transform (used in JPEG).

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| coefficients | Output | IMAGE | DCT coefficients |

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| block_size | INT | 8 | Block size (8 = JPEG-style) |

**Notes:**
- Transforms image into frequency coefficients
- Low frequencies (top-left) = overall color/brightness
- High frequencies (bottom-right) = edges/detail
- Set block_size to 0 for full-image DCT

---

### Inverse DCT

Convert DCT coefficients back to image.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| coefficients | Input | IMAGE | DCT coefficients |
| image | Output | IMAGE | Reconstructed image |

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| block_size | INT | 8 | Must match DCT node |

---

### FFT

Fast Fourier Transform.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| magnitude | Output | IMAGE | Frequency magnitudes |
| phase | Output | IMAGE | Frequency phases |

**Notes:**
- Separates image into magnitude (strength) and phase (position)
- Magnitude shows frequency content
- Phase contains structural information
- Both are needed for reconstruction

---

### Inverse FFT

Reconstruct image from FFT components.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| magnitude | Input | IMAGE | Frequency magnitudes |
| phase | Input | IMAGE | Frequency phases |
| image | Output | IMAGE | Reconstructed image |

---

### FFT Filter

Apply frequency-domain filtering.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| image | Output | IMAGE | Filtered image |

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| filter_type | ENUM | low_pass | | Filter type |
| cutoff | FLOAT | 0.5 | 0.0-1.0 | Cutoff frequency |

**Filter types:**
- **low_pass** - Keep low frequencies, blur
- **high_pass** - Keep high frequencies, edge detection
- **band_pass** - Keep middle frequencies

---

### Wavelet Transform

Forward wavelet decomposition.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| coefficients | Output | ARRAY | Wavelet coefficients |

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| wavelet | ENUM | haar | Wavelet type |
| level | INT | 3 | Decomposition levels |
| mode | ENUM | fwt | Transform mode |

**Wavelet types:**
- **haar** - Simple, blocky artifacts (good for glitch)
- **db2-db10** - Daubechies wavelets (smoother)
- **sym2-sym10** - Symlets (symmetric)
- **bior** - Biorthogonal wavelets

**Modes:**
- **fwt** - Full wavelet transform
- **wpt** - Wavelet packet transform

---

### Inverse Wavelet

Reconstruct image from wavelet coefficients.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| coefficients | Input | ARRAY | Wavelet coefficients |
| image | Output | IMAGE | Reconstructed image |

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| wavelet | ENUM | haar | Must match Wavelet Transform |
| mode | ENUM | fwt | Must match Wavelet Transform |

---

### Wavelet Compress

Threshold wavelet coefficients for compression/glitching.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| coefficients | Input | ARRAY | Wavelet coefficients |
| coefficients | Output | ARRAY | Thresholded coefficients |

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| threshold | FLOAT | 0.1 | 0.0-1.0 | Coefficient threshold |
| mode | ENUM | soft | | Thresholding mode |

**Modes:**
- **soft** - Shrink coefficients toward zero
- **hard** - Zero out coefficients below threshold

**Notes:**
- Higher threshold = more coefficients zeroed = more glitch
- Affects high-frequency details first

---

### Pixel Sort

Classic glitch art pixel sorting effect.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| image | Output | IMAGE | Sorted image |

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| direction | ENUM | horizontal | | Sort direction |
| sort_by | ENUM | brightness | | Sort criterion |
| threshold_low | FLOAT | 0.25 | 0.0-1.0 | Lower threshold |
| threshold_high | FLOAT | 0.75 | 0.0-1.0 | Upper threshold |
| reverse | BOOL | False | | Reverse sort order |

**Directions:** horizontal, vertical, diagonal_down, diagonal_up

**Sort criteria:** brightness, hue, saturation, red, green, blue

**How it works:**
1. Find pixels between threshold_low and threshold_high
2. Sort those pixels by the chosen criterion
3. Pixels outside thresholds remain in place

**Tips:**
- Narrow threshold range (0.4-0.6) = minimal sorting
- Wide threshold range (0.0-1.0) = maximum sorting
- Try different sort_by options for different effects

---

## Corruption

Low-level data manipulation nodes.

### Bit Shift

Shift bits in pixel values.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| image | Output | IMAGE | Corrupted image |

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| amount | INT | 1 | -7 to 7 | Shift amount (+ = left, - = right) |
| wrap | BOOL | True | | Wrap bits around |

**Notes:**
- Left shift multiplies values (brightens, can overflow)
- Right shift divides values (darkens, loses precision)
- Wrap mode rotates bits instead of losing them

---

### Bit Flip

Randomly flip bits in pixel values.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| image | Output | IMAGE | Corrupted image |

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| probability | FLOAT | 0.01 | 0.0-1.0 | Flip probability per bit |
| seed | INT | 0 | | Random seed (0 = random) |

---

### Byte Swap

Swap bytes in image data.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| image | Output | IMAGE | Corrupted image |

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| mode | ENUM | adjacent | Swap mode |

**Modes:**
- **adjacent** - Swap neighboring bytes
- **reverse** - Reverse byte order
- **shuffle** - Random shuffle

---

### XOR Noise

XOR image data with noise pattern.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| image | Output | IMAGE | Corrupted image |

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| intensity | FLOAT | 0.5 | 0.0-1.0 | Noise intensity |
| seed | INT | 0 | | Random seed |
| pattern | ENUM | random | | Noise pattern |

**Patterns:** random, horizontal, vertical, checker

---

### Data Repeat

Repeat sections of image data.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| image | Output | IMAGE | Corrupted image |

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| start | FLOAT | 0.25 | 0.0-1.0 | Start position (fraction of image) |
| length | FLOAT | 0.1 | 0.0-0.5 | Section length to repeat |
| repeats | INT | 3 | 1-10 | Number of repetitions |

---

### Data Drop

Remove sections of image data.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| image | Output | IMAGE | Corrupted image |

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| start | FLOAT | 0.25 | 0.0-1.0 | Start position |
| length | FLOAT | 0.1 | 0.0-0.5 | Length to drop |
| fill | ENUM | zero | | Fill mode for dropped section |

**Fill modes:** zero, repeat, previous

---

### Data Weave

Interleave rows/columns from two images.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image_a | Input | IMAGE | First image |
| image_b | Input | IMAGE | Second image |
| image | Output | IMAGE | Woven image |

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| direction | ENUM | horizontal | | Weave direction |
| interval | INT | 2 | 1-32 | Weave interval (pixels) |

---

### Data Scramble

Scramble blocks of image data.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| image | Output | IMAGE | Scrambled image |

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| block_size | INT | 8 | 1-64 | Block size |
| seed | INT | 0 | | Random seed |
| intensity | FLOAT | 0.5 | 0.0-1.0 | Scramble probability |

---

## Pipeline

High-level macro nodes that combine multiple processing stages.

### GLIC Encode

Complete GLIC encoding pipeline: Color Space → Segment → Predict → Residual → Quantize

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| residuals | Output | IMAGE | Quantized residuals (visual) |
| segments | Output | SEGMENTS | Segment list (for decode) |
| predicted | Output | IMAGE | Predicted image (for visualization) |
| quantized_int | Output | ARRAY | Quantized data (for decode) |

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| colorspace | ENUM | YCbCr | | Working color space |
| min_segment_size | INT | 4 | 2-64 | Minimum segment size |
| max_segment_size | INT | 64 | 4-512 | Maximum segment size |
| segment_threshold | FLOAT | 10.0 | 0.1-100 | Segmentation threshold |
| predictor | ENUM | PAETH | | Prediction algorithm |
| quantization_bits | INT | 8 | 1-16 | Quantization bit depth |

**Quick glitch settings:**
- **Mild:** bits=6, predictor=PAETH
- **Medium:** bits=4, predictor=SAD
- **Heavy:** bits=2, predictor=BSAD
- **Extreme:** bits=1, predictor=NONE

---

### GLIC Decode

Complete GLIC decoding pipeline: Dequantize → Predict → Reconstruct → Color Space

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| quantized_int | Input | ARRAY | Quantized data from Encode |
| segments | Input | SEGMENTS | Segment list from Encode |
| reference | Input | IMAGE | Optional reference for metadata |
| image | Output | IMAGE | Reconstructed image |

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| colorspace | ENUM | YCbCr | Must match Encode |
| predictor | ENUM | PAETH | Must match Encode |
| quantization_bits | INT | 8 | Must match Encode |
| output_colorspace | ENUM | RGB | Final output color space |

**Notes:**
- Parameters must match the Encode node for proper reconstruction
- Intentionally mismatching parameters creates glitch effects

---

## Utility

Helper and debugging nodes.

### Null

Pass image through without modification.

| Port | Direction | Type | Description |
|------|-----------|------|-------------|
| image | Input | IMAGE | Input image |
| image | Output | IMAGE | Same image (unchanged) |

**Uses:**
- Debugging - inspect values at a point in the pipeline
- Organization - create visual breaks in complex graphs
- Future expansion - placeholder for planned processing

---

## Common Workflows

### Basic GLIC Compression/Glitch

```
Image Loader → GLIC Encode → GLIC Decode → Image Saver
                   ↓              ↑
              quantized_int ──────┘
              segments ───────────┘
```

### Pixel Sorting in YCbCr

```
Image Loader → Color Space (YCbCr) → Pixel Sort → Color Space (RGB) → Image Saver
```

### Wavelet Glitching

```
Image Loader → Wavelet Transform → Wavelet Compress → Inverse Wavelet → Image Saver
```

### Corrupt GLIC Data

```
Image Loader → GLIC Encode → Bit Flip (on quantized_int) → GLIC Decode → Image Saver
```

### Channel-Selective Processing

```
                         ┌→ Pixel Sort ──┐
Image Loader → Split ────┼→ (unchanged) ─┼→ Merge → Image Saver
                         └→ (unchanged) ─┘
```

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Execute Graph | Shift+E |
| New Project | Ctrl+N |
| Open Project | Ctrl+O |
| Save Project | Ctrl+S |
| Undo | Ctrl+Z |
| Redo | Ctrl+Y |
| Delete Selection | Delete |
| Select All | Ctrl+A |
| Zoom In | Ctrl++ |
| Zoom Out | Ctrl+- |
| Reset Zoom | Ctrl+0 |

---

*For more information, see [Getting Started](getting-started.md) and [Architecture](architecture.md).*

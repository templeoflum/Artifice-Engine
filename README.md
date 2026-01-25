# Artifice

**Converse with Chaos, Sculpt Emergence.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GPU Accelerated](https://img.shields.io/badge/GPU-OpenGL%204.3-green.svg)]()

A real-time GPU-accelerated glitch art environment built on a node-based architecture. Create GLIC-style codec glitches, pixel sorting, data corruption, and color space manipulations at 60fps.

![Artifice Screenshot](docs/images/screenshot.png)

## What It Does

Artifice is a visual programming environment for real-time glitch art. You build processing pipelines by connecting nodes - each node executes on the GPU via compute shaders, enabling instant feedback as you tweak parameters. The node-based approach lets you:

- **Experiment in real-time** - See results instantly at 60fps as you adjust parameters
- **Chain complex effects** - Build sophisticated processing pipelines by connecting nodes
- **Explore the GLIC codec** - Full implementation of GLIC prediction, residuals, and reconstruction
- **Work in any color space** - 16 color spaces for different glitch characteristics
- **Save and share workflows** - Export your node graphs to recreate or share effects

### Architecture Evolution

Artifice exists in two forms:

| Version | Architecture | Use Case |
|---------|-------------|----------|
| **v1** (this repo) | CPU/NumPy pipeline | Batch processing, maximum quality, full feature set |
| **v2** (realtime branch) | GPU compute shaders | Real-time preview, live performance, interactive exploration |

The GPU architecture achieves 60fps on 1080p images where v1 takes 50-500ms per frame, making it ideal for live experimentation and performance contexts.

## Core Capabilities

### GLIC Codec (Glitch Codec)

Full implementation of the GLIC image codec for structured glitch art:

- **16 Predictors** - None, Corner, Horizontal, Vertical, DC Mean, DC Median, Median, Average, TrueMotion, Paeth, Linear Diagonal, H/V Position, JPEG-LS, Difference
- **Predictor Selection Modes**:
  - **SAD (Best)** - Automatically selects the predictor with minimum error per block
  - **BSAD (Worst)** - Selects the WORST predictor for maximum glitch effect
  - **Random** - Random predictor per block for chaotic results
- **Residual Methods** - Subtract, Clamp, Wrap, CLAMP_MOD256 (GLIC-style color shifts)
- **Signed Quantization** - Proper residual encoding for reconstruction

### Color Space Processing

All 16 GLIC color spaces for different glitch characteristics:

| Category | Spaces | Best For |
|----------|--------|----------|
| **Perceptual** | LAB, LUV, HCL | Smooth gradients, perceptually uniform manipulation |
| **Video** | YCbCr, YUV, YPbPr, YDbDr | Classic video glitch aesthetic, luma/chroma separation |
| **Artist** | HSV, HSL, HWB | Intuitive hue/saturation control |
| **Scientific** | XYZ, YXY | Color science, chromaticity diagrams |
| **Special** | CMY, OHTA, GREY | Subtractive color, feature extraction, grayscale |

**Tip:** Glitch effects work best by converting to a luma-chroma space (YCbCr, LAB), corrupting the chroma channels, then converting back. This preserves image structure while creating dramatic color shifts.

### Data Corruption

GPU-accelerated bit and byte manipulation:

- **Bit Flip** - Toggle specific bits with configurable probability and channel targeting
- **Bit Shift** - Shift bits left/right with rotation or truncation
- **XOR Noise** - XOR pixel data with noise patterns
- **Data Repeat/Drop** - Duplicate or skip rows/columns of data
- **Data Scramble** - Shuffle data segments based on block patterns
- **Data Weave** - Interleave two images in horizontal, vertical, or checker patterns

### Transforms

- **Pixel Sort** - Sort by brightness, hue, saturation, or RGB channels with threshold modes
- **DCT** - Discrete Cosine Transform for JPEG-style block effects
- **FFT** - Frequency domain manipulation
- **Wavelet** - Multi-level wavelet decomposition

### Quantization

- **Uniform/Adaptive** - Equal bins or concentrated near common values
- **Signed Mode** - For proper residual encoding (-1 to 1 range)
- **Dithering** - Bayer and Blue Noise dither patterns
- **1-16 bit depth** - From binary to near-lossless

## Installation

### Prerequisites

- Python 3.10 or higher
- OpenGL 4.3 compatible GPU (for real-time mode)
- pip package manager

### Quick Install

```bash
# Clone the repository
git clone https://github.com/templeoflum/Artifice.git
cd Artifice

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### GPU Backend Requirements

For real-time GPU rendering (v2/realtime branch):

```bash
pip install moderngl PyOpenGL
```

## Quick Start

### Launch the Application

```bash
python -m artifice
```

### Basic Workflow

1. **Add nodes** - Drag from the palette onto the canvas
2. **Connect nodes** - Click output port, then input port
3. **Adjust parameters** - Select a node to edit in the inspector
4. **Preview updates in real-time** - GPU nodes render at 60fps

### Example: GLIC-Style Color Glitch

```
[Test Card] → [Color Space: RGB→YCbCr] → [GLIC Predict: BSAD] → [Quantize: 4 bits, Signed] → [GLIC Reconstruct] → [Color Space: YCbCr→RGB]
```

This pipeline:
1. Converts to YCbCr (separates luma from chroma)
2. Generates predictions using the WORST predictor (BSAD mode)
3. Quantizes residuals to 4 bits (destroys subtle information)
4. Reconstructs with quantized residuals (creates color shifts)
5. Converts back to RGB for display

## Node Reference

See [NODES.md](NODES.md) for complete node specifications with all parameters.

### Quick Reference

| Category | Nodes |
|----------|-------|
| **I/O** | Image Loader, Image Saver |
| **Generators** | Test Card, Noise |
| **Color** | Color Space, Channel Split/Merge/Swap, Blend, Invert, Brightness/Contrast, Threshold, Posterize |
| **GLIC** | GLIC Predict, GLIC Residual, GLIC Reconstruct |
| **Quantization** | Quantize |
| **Transform** | Pixel Sort, DCT, FFT, Wavelet, Mirror, Rotate, Blur, Sharpen, Edge Detect |
| **Corruption** | Bit Flip, Bit Shift, XOR Noise, Data Repeat, Data Drop, Data Scramble, Data Weave |

## Project Structure

```
Artifice/
├── src/artifice/
│   ├── core/           # Node system, graph, ports (v1)
│   ├── engine/         # GPU backend, pipeline, textures (v2)
│   ├── nodes/          # Node implementations
│   ├── shaders/        # GLSL compute shaders (v2)
│   └── ui/             # Qt-based interface
├── tests/              # Test suite
├── docs/               # Documentation
├── NODES.md            # Complete node specifications
├── DEVLOG.md           # Development history
└── ROADMAP.md          # Future plans
```

## Documentation

- [NODES.md](NODES.md) - Complete node specifications with all parameters
- [DEVLOG.md](DEVLOG.md) - Development log: v1 to v2 evolution
- [ROADMAP.md](ROADMAP.md) - Future implementation plans
- [CLAUDE.md](CLAUDE.md) - Architecture reference for Claude Code development

## Development

This project is developed using [Claude Code](https://claude.ai/claude-code), with Claude handling implementation under human creative direction.

```bash
# Run tests
pytest

# Run GPU-specific tests
pytest tests/test_gpu.py -v

# Run with coverage
pytest --cov=artifice
```

## Compatibility

- **Windows** - Fully tested and supported
- **macOS/Linux** - May work but untested
- **GPU** - Requires OpenGL 4.3 for real-time mode
- **Python** - 3.10 or higher

## License

MIT License - see [LICENSE](LICENSE)

## Acknowledgments

- Developed with [Claude Code](https://claude.ai/claude-code) by Anthropic
- Inspired by [GLIC](https://github.com/GlitchCodec/GLIC) glitch codec
- Built with [PySide6](https://www.qt.io/qt-for-python) and [ModernGL](https://moderngl.readthedocs.io/)
- Node editor concepts from Blender, Nuke, and TouchDesigner

---

*Converse with Chaos, Sculpt Emergence.*

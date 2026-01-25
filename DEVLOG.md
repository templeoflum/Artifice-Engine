# Artifice Development Log

A chronicle of Artifice's evolution from CPU-based pipeline to real-time GPU rendering.

---

## Overview

Artifice began as a Python implementation of glitch art processing nodes, inspired by the GLIC (Glitch Codec) and classic datamoshing techniques. The project evolved through two major architectural phases:

- **v1**: CPU-based NumPy pipeline with full feature set
- **v2**: GPU compute shader architecture for real-time rendering

This document traces that evolution, the technical decisions made, and lessons learned.

---

## Phase 1: Foundation (v1 - CPU Pipeline)

### Initial Vision

The goal was to create a node-based environment for glitch art that would:
- Expose every parameter of the GLIC codec
- Allow arbitrary node graph construction
- Provide immediate visual feedback
- Be extensible for new algorithms

### Technology Choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.10+ | Rapid development, rich ecosystem |
| Image Processing | NumPy, OpenCV, Pillow | Industry standard, well-documented |
| UI Framework | PySide6 (Qt) | Cross-platform, professional node editors |
| Transforms | SciPy, PyWavelets | Proven FFT, wavelet implementations |

### Core Architecture

The v1 architecture followed a classic node graph pattern:

```
┌─────────────────────────────────────────────────────┐
│                    NodeGraph                         │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐         │
│  │  Node   │───▶│  Node   │───▶│  Node   │         │
│  │ (CPU)   │    │ (CPU)   │    │ (CPU)   │         │
│  └─────────┘    └─────────┘    └─────────┘         │
│       │              │              │               │
│       ▼              ▼              ▼               │
│  NumPy Array    NumPy Array    NumPy Array         │
└─────────────────────────────────────────────────────┘
```

**Key Design Decisions:**

1. **Pull-based Execution**: Nodes are evaluated on-demand when outputs are requested
2. **Dirty Propagation**: Changes invalidate downstream nodes
3. **Type-safe Ports**: Explicit IMAGE, ARRAY, FLOAT types prevent invalid connections
4. **Parameter System**: Unified parameter definitions with UI auto-generation

### Node Families Implemented

| Category | Nodes | Notes |
|----------|-------|-------|
| I/O | ImageLoader, ImageSaver | File browser integration |
| Generators | TestCard, Noise | Procedural patterns |
| Color | ColorSpace (7 spaces), Channel ops | Full color manipulation |
| Segmentation | Quadtree | Adaptive block decomposition |
| Prediction | 6 GLIC predictors | Core codec functionality |
| Quantization | Uniform, Adaptive, Per-channel | Bit depth reduction |
| Transform | DCT, FFT, Wavelet, PixelSort | Frequency and spatial ops |
| Corruption | BitFlip, BitShift, ByteSwap, etc. | Data manipulation |

### Performance Characteristics

Processing times for 1080p images (typical laptop):

| Operation | Time |
|-----------|------|
| Color Space Conversion | 20-40ms |
| Pixel Sort | 150-300ms |
| FFT | 50-100ms |
| Wavelet (3 levels) | 80-150ms |
| Full GLIC Pipeline | 200-500ms |

**Bottleneck Analysis:**
- NumPy operations are efficient but CPU-bound
- Python overhead for complex node graphs
- Memory copies between nodes
- No parallelism in execution

### What v1 Got Right

1. **Comprehensive GLIC Implementation**: All predictors, residual methods, quantization modes
2. **Test Card**: Invaluable for understanding effect behavior
3. **Parameter Granularity**: Every algorithm parameter exposed
4. **Clean Separation**: Core, nodes, UI cleanly separated

### v1 Limitations

1. **No Real-time**: 200-500ms per frame makes interactive exploration frustrating
2. **Memory Overhead**: Full image copies between every node
3. **UI Blocking**: Processing freezes the interface
4. **CPU Ceiling**: Can't leverage GPU parallelism

---

## Phase 2: Real-Time GPU Architecture (v2)

### Motivation

The core insight: glitch art is about exploration. Artists need to:
- Tweak a parameter and see results instantly
- Try dozens of variations rapidly
- Perform live with audio reactivity

50-500ms latency kills this workflow. The solution: move everything to GPU.

### Technology Pivot

| Component | v1 | v2 | Why |
|-----------|----|----|-----|
| Processing | NumPy (CPU) | GLSL Compute Shaders (GPU) | 100-1000x speedup potential |
| Backend | None | ModernGL (OpenGL 4.3) | Mature, Pythonic, compute shader support |
| Execution | Pull-based | Push-based streaming | Continuous render loop |
| Memory | NumPy arrays | GPU textures | Zero-copy between nodes |

### New Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Artifice v2                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Node      │  │   Pipeline  │  │   Real-Time         │  │
│  │   Graph     │──│   Executor  │──│   Preview           │  │
│  │   (Logic)   │  │   (GPU)     │  │   (QOpenGLWidget)   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│         │                │                    │              │
│         ▼                ▼                    ▼              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              GPU Context (ModernGL)                     ││
│  │   Textures (images) │ Compute Shaders │ Memory Barriers ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### GPUNode Base Class

The fundamental abstraction shift:

```python
# v1: CPU Node
class CPUNode:
    def process(self):
        image = self.get_input_value("image")  # NumPy array
        result = some_numpy_operation(image)
        self.set_output_value("image", result)

# v2: GPU Node
class GPUNode:
    shader = "path/to/shader.glsl"

    def execute(self, ctx, input_textures, width, height):
        # Bind inputs as image units
        for i, tex in enumerate(input_textures.values()):
            tex.bind_as_image(i, "read")

        # Bind outputs
        self._output_textures["image"].bind_as_image(i+1, "write")

        # Set uniforms (parameters)
        self._set_uniforms(width, height)

        # Dispatch compute shader
        self._compiled_shader.run(groups_x, groups_y, 1)
```

### Compute Shader Pattern

All processing nodes follow the same GLSL structure:

```glsl
#version 430

layout(local_size_x = 16, local_size_y = 16) in;

layout(rgba32f, binding = 0) readonly uniform image2D input_image;
layout(rgba32f, binding = 1) writeonly uniform image2D output_image;

uniform float parameter1;
uniform int parameter2;

void main() {
    ivec2 pixel = ivec2(gl_GlobalInvocationID.xy);
    ivec2 size = imageSize(input_image);

    if (pixel.x >= size.x || pixel.y >= size.y) return;

    vec4 color = imageLoad(input_image, pixel);

    // Process...
    vec4 result = some_operation(color);

    imageStore(output_image, pixel, result);
}
```

### Performance Results

Processing times for 1080p images:

| Operation | v1 (CPU) | v2 (GPU) | Speedup |
|-----------|----------|----------|---------|
| Color Space | 30ms | <1ms | 30x+ |
| Bit Flip | 15ms | <1ms | 15x+ |
| Pixel Sort | 200ms | 3-5ms | 40-70x |
| Quantize | 25ms | <1ms | 25x+ |
| Full Pipeline | 300ms | 8-12ms | 25-40x |

**Achieved: 60fps sustained at 1080p**

### Node Port: v1 to v2

Each node required careful translation:

1. **Identify Algorithm Core**: What does the NumPy code actually compute?
2. **Design GLSL Equivalent**: Map to GPU-friendly parallel patterns
3. **Handle Edge Cases**: Boundary conditions, numeric precision
4. **Parameter Mapping**: Ensure identical parameter semantics

#### Example: Bit Flip Node

**v1 (NumPy):**
```python
def process(self):
    image = self.get_input_value("image")
    bit = self.get_parameter("bit_position")
    prob = self.get_parameter("probability")

    # Convert to 8-bit integers
    data = (image * 255).astype(np.uint8)

    # Generate random mask
    mask = np.random.random(data.shape) < prob

    # Flip the specified bit
    data[mask] ^= (1 << bit)

    # Back to float
    result = data.astype(np.float32) / 255.0
    self.set_output_value("image", result)
```

**v2 (GLSL):**
```glsl
uniform int bit_position;
uniform float probability;
uniform int seed;
uniform int channel_mask;

// Hash function for deterministic randomness
uint hash(uvec2 p) {
    uint state = p.x * 1597334677u ^ p.y * 3812015801u;
    state = state * 1597334677u;
    return state;
}

void main() {
    ivec2 pixel = ivec2(gl_GlobalInvocationID.xy);
    vec4 color = imageLoad(input_image, pixel);

    // Process each channel
    for (int c = 0; c < 3; c++) {
        if ((channel_mask & (1 << c)) == 0) continue;

        // Deterministic random based on position and seed
        float rand = float(hash(uvec2(pixel) + uvec2(seed, c))) / 4294967295.0;

        if (rand < probability) {
            // Convert to integer, flip bit, convert back
            uint val = uint(color[c] * 255.0);
            val ^= (1u << uint(bit_position));
            color[c] = float(val) / 255.0;
        }
    }

    imageStore(output_image, pixel, color);
}
```

### Challenges Encountered

#### 1. Floating Point Precision

GPU float operations can differ from CPU:
- Solution: Explicit clamping, careful normalization
- Some effects inherently differ slightly (acceptable for glitch art)

#### 2. Parallel Algorithm Design

Sequential algorithms don't parallelize:
- Pixel Sort required complete redesign (bitonic sort)
- FFT uses Stockham algorithm (naturally parallel)
- Some v1 algorithms need fundamentally different approaches

#### 3. Texture Binding Limits

OpenGL has limited image unit bindings:
- Pipeline executor manages binding slots carefully
- Nodes must declare their binding requirements

#### 4. Shader Compilation

GLSL errors are cryptic:
- Comprehensive error logging with line numbers
- Shader hot-reloading for development

### Feature Parity Audit

During v1→v2 port, discovered missing features:

| Node | Missing in v2 | Status |
|------|---------------|--------|
| PixelSort | threshold_mode, seed | ✅ Added |
| Quantize | signed mode, bits param | ✅ Added |
| GLIC Predict | SAD/BSAD/Random modes | ✅ Added |
| Color Space | 8 of 16 spaces | ✅ Added all 16 |
| Data Weave | Entire node | ✅ Created |

**Lesson**: Every parameter is a universe of exploration. Audit thoroughly.

---

## v1 vs v2: When to Use Each

| Use Case | Recommended | Why |
|----------|-------------|-----|
| Live performance | v2 | 60fps essential |
| Parameter exploration | v2 | Instant feedback |
| Batch processing | v1 | More features, proven stability |
| Maximum quality | v1 | Higher precision, no GPU artifacts |
| Algorithm development | v1 | Easier debugging |
| Audio reactivity | v2 | Low latency required |

---

## Key Lessons Learned

### 1. Start with the Right Abstraction

The GPUNode base class makes porting straightforward:
- Standardized shader loading
- Automatic texture management
- Uniform parameter binding

### 2. Parameter Granularity Matters

"Every tiny little parameter has a whole universe of exploration hiding in it."

Don't simplify interfaces. Expose everything. Artists will find uses you didn't imagine.

### 3. Test Cards Are Essential

The procedural test card makes algorithm behavior visible:
- Color bars reveal channel operations
- Checkerboard reveals frequency effects
- Zone plate reveals aliasing

### 4. GPU Patterns Differ from CPU

Some algorithms need complete reimagining:
- Sequential → Parallel
- In-place → Double-buffered
- Conditional → Branchless

### 5. Document Everything

Future development depends on understanding:
- Why decisions were made
- What each parameter does
- How algorithms work

---

## Technical Reference

### File Structure

```
v1 (main branch):
src/artifice/
├── core/           # Node system, graph execution
│   ├── node.py     # Base Node class
│   ├── port.py     # Port types
│   ├── graph.py    # Graph execution
│   └── registry.py # Node registration
├── nodes/          # CPU node implementations
└── ui/             # Qt interface

v2 (realtime-architecture branch):
src/artifice/
├── engine/         # GPU infrastructure
│   ├── backend.py  # ModernGL context
│   ├── node.py     # GPUNode base class
│   ├── pipeline.py # Graph executor
│   └── texture.py  # GPU texture wrapper
├── nodes/          # GPU node implementations
├── shaders/        # GLSL compute shaders
└── ui/             # Qt + OpenGL interface
```

### Shader Conventions

All compute shaders follow:
- `layout(local_size_x = 16, local_size_y = 16)` - 256 threads per workgroup
- `binding = 0` - First input
- `binding = N` - Nth input/output
- Bounds checking in `main()`
- Float [0,1] normalized colors

### Performance Profiling

```python
# Enable GPU timing
import moderngl
ctx.enable(moderngl.QUERY_TIME_ELAPSED)

query = ctx.query(time=True)
with query:
    node.execute(ctx, inputs, width, height)
print(f"GPU time: {query.elapsed / 1e6:.2f}ms")
```

---

## Future Direction

See [ROADMAP.md](ROADMAP.md) for planned features:
- Video synthesis (oscillators, feedback)
- Audio reactivity
- AI integration
- wgpu-py backend (Vulkan/Metal)

---

*Development continues with Claude Code under human creative direction.*

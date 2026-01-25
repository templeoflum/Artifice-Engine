# Artifice Roadmap

Future development plans for Artifice, organized by priority and complexity.

---

## Current Status

**v1 (CPU Pipeline)**: Feature-complete, stable
**v2 (GPU Real-time)**: Core architecture complete, active development

### Recently Completed
- [x] GPU compute shader infrastructure (ModernGL backend)
- [x] Real-time preview at 60fps
- [x] All 16 GLIC color spaces
- [x] Full GLIC predictor implementation (including SAD/BSAD/Random modes)
- [x] Signed quantization for proper residual encoding
- [x] Pixel sort with threshold modes
- [x] Data weave node for image interleaving
- [x] Comprehensive node parameter parity with v1

---

## Near Term (Next Release)

### Polish & Stability

| Task | Priority | Complexity | Notes |
|------|----------|------------|-------|
| Shader hot-reload | High | Low | Faster development iteration |
| Error recovery | High | Medium | Graceful handling of shader errors |
| Parameter presets | Medium | Low | Save/load node configurations |
| Undo/redo system | Medium | Medium | Essential for experimentation |
| Graph save/load | High | Low | JSON serialization |

### Additional Nodes

| Node | Category | Priority | Notes |
|------|----------|----------|-------|
| Solarize | Color | High | Classic glitch effect |
| Levels/Curves | Color | Medium | Standard color correction |
| Chromatic Aberration | Transform | High | Popular glitch aesthetic |
| Displacement Map | Transform | Medium | Use one image to distort another |
| Feedback Buffer | Transform | High | Essential for video synthesis |
| Delay/History | Temporal | High | Frame buffer with decay |

---

## Medium Term (Q2-Q3 2025)

### Video Synthesis Module

Inspired by hardware video synthesizers (LZX, Vidiot, Fairlight CVI):

| Component | Description | Priority |
|-----------|-------------|----------|
| **Oscillators** | Sine, triangle, saw, square with frequency/amplitude/phase | High |
| **Ramps** | Horizontal/vertical gradient generators | High |
| **Colorizers** | Grayscale to color mapping with threshold bands | High |
| **Keyers** | Luma key, chroma key, difference key | Medium |
| **Feedback** | Frame buffer with transform in feedback path | High |
| **Mixers** | Additive, multiplicative, crossfade | Medium |

**Architecture Considerations:**
- Oscillators need time parameter from render loop
- Feedback requires ping-pong texture buffers
- Consider separate "signal" port type for 1D data

### Temporal Processing (Video)

| Feature | Description | Priority |
|---------|-------------|----------|
| Video input | Load video files, process frame-by-frame | High |
| Frame buffer | Access previous N frames | High |
| Frame blending | Mix multiple frames with decay | Medium |
| Motion detection | Frame difference for motion masks | Medium |
| Time remapping | Speed up, slow down, reverse | Low |
| Optical flow | Motion vector estimation | Low |

### Audio Reactivity

| Feature | Description | Priority |
|---------|-------------|----------|
| Audio input | Capture from mic/line in | High |
| FFT analysis | Extract frequency bands | High |
| Beat detection | Trigger events on beats | Medium |
| Parameter mapping | Drive any parameter from audio | High |
| Envelope follower | Smooth amplitude tracking | Medium |
| MIDI input | Control parameters via MIDI | Medium |

---

## Long Term (Q4 2025+)

### Alternative GPU Backends

| Backend | Pros | Cons | Priority |
|---------|------|------|----------|
| **wgpu-py** | Vulkan/Metal, modern, cross-platform | Less mature Python bindings | Medium |
| **CuPy** | CUDA, maximum NVIDIA performance | NVIDIA only | Low |
| **PyTorch** | AI model integration, good GPU support | Overkill for non-AI nodes | Medium |

**Strategy**: Abstract backend interface allows swapping without changing node code.

### AI Integration

| Feature | Description | Complexity |
|---------|-------------|------------|
| Semantic segmentation | Mask regions by content (sky, person, etc.) | Medium |
| Style transfer | Apply artistic styles | Medium |
| Upscaling | AI-based super resolution | Low |
| Inpainting | Fill in regions | Medium |
| Latent space manipulation | Control diffusion model latents | High |

**Considerations:**
- Keep AI optional (large dependencies)
- Run models on GPU alongside shaders
- Latency may break real-time for complex models

### Advanced Transforms

| Transform | Description | Complexity |
|-----------|-------------|------------|
| Morphological operations | Erode, dilate, open, close | Low |
| Distance transform | Distance from edges | Medium |
| Hough transform | Line/circle detection | Medium |
| Optical flow warping | Warp based on motion | High |
| 3D projection | Map 2D onto 3D surfaces | High |

### Plugin System

Allow users to create custom nodes without modifying core:

```python
# user_nodes/my_node.py
from artifice.plugin import PluginNode

class MyGlitchNode(PluginNode):
    name = "My Glitch"
    shader = "my_glitch.glsl"

    def define_parameters(self):
        self.add_parameter("intensity", 0.5, 0.0, 1.0)
```

**Requirements:**
- Plugin directory scanning
- Safe shader compilation
- Parameter validation
- Hot-reload support

---

## Experimental Ideas

### Ideas Under Consideration

| Idea | Description | Feasibility |
|------|-------------|-------------|
| **Cellular Automata** | GPU-accelerated Game of Life, etc. | High |
| **Reaction-Diffusion** | Gray-Scott, Turing patterns | High |
| **Fractal Generators** | Mandelbrot, Julia sets | High |
| **Neural Cellular Automata** | Learned update rules | Medium |
| **L-systems** | Procedural growth patterns | Medium |
| **Fluid Simulation** | Smoke, water effects | Medium |
| **Voronoi/Delaunay** | Geometric patterns | Medium |
| **Ray Marching** | SDF-based 3D rendering | High (but complex) |

### Community Requested

Track feature requests from users:
- [ ] Batch export (render graph to image sequence)
- [ ] Timeline/keyframing for animations
- [ ] LUT import/export
- [ ] Network protocol (OSC, NDI)
- [ ] Headless rendering mode

---

## Technical Debt

Issues to address as the codebase matures:

| Item | Impact | Effort |
|------|--------|--------|
| Test coverage for v2 GPU nodes | High | Medium |
| Documentation for shader authoring | High | Low |
| Performance profiling tools | Medium | Low |
| Memory leak detection | High | Medium |
| Cross-platform testing (macOS, Linux) | Medium | High |

---

## Version Milestones

### v0.2.0 (Near Term)
- [ ] Polish current node set
- [ ] Graph save/load
- [ ] Basic presets system
- [ ] Improved error handling

### v0.3.0 (Video Synthesis)
- [ ] Oscillators and ramps
- [ ] Colorizers
- [ ] Feedback system
- [ ] Frame buffer nodes

### v0.4.0 (Audio)
- [ ] Audio input capture
- [ ] FFT analysis
- [ ] Parameter modulation
- [ ] Beat detection

### v1.0.0 (Stable Release)
- [ ] All core features stable
- [ ] Comprehensive documentation
- [ ] Plugin system
- [ ] Cross-platform support

---

## Contributing

Contributions are welcome. To propose new features:

1. Open an issue describing the feature
2. Discuss implementation approach
3. Submit PR with tests and documentation

Priority is given to:
- Features that enable new artistic possibilities
- Performance improvements
- Documentation and examples

---

*This roadmap is a living document. Priorities may shift based on community feedback and creative direction.*

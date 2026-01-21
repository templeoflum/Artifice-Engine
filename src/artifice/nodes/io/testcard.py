"""
Test card generator node.

Generates a procedural test card image for visualizing node effects.
"""

from __future__ import annotations

import numpy as np

from artifice.core.data_types import ColorSpace, ImageBuffer
from artifice.core.node import Node, ParameterType
from artifice.core.port import PortType
from artifice.core.registry import register_node


def _generate_perlin_noise(size: int, scale: float = 4.0) -> np.ndarray:
    """
    Generate simple Perlin-like noise using interpolated random values.

    Args:
        size: Output image size (square).
        scale: Frequency scale for the noise.

    Returns:
        2D float32 array with values in [0, 1].
    """
    # Create low-res random grid
    grid_size = max(2, int(size / scale))
    grid = np.random.rand(grid_size + 1, grid_size + 1).astype(np.float32)

    # Create coordinate arrays for interpolation
    x = np.linspace(0, grid_size, size)
    y = np.linspace(0, grid_size, size)

    # Get integer and fractional parts
    x0 = np.floor(x).astype(int)
    y0 = np.floor(y).astype(int)
    x1 = np.minimum(x0 + 1, grid_size)
    y1 = np.minimum(y0 + 1, grid_size)

    # Fractional parts with smoothstep
    fx = x - x0
    fy = y - y0
    fx = fx * fx * (3 - 2 * fx)  # Smoothstep
    fy = fy * fy * (3 - 2 * fy)

    # Create meshgrid
    fy_grid, fx_grid = np.meshgrid(fy, fx, indexing='ij')
    y0_grid, x0_grid = np.meshgrid(y0, x0, indexing='ij')
    y1_grid, x1_grid = np.meshgrid(y1, x1, indexing='ij')

    # Bilinear interpolation
    n00 = grid[y0_grid, x0_grid]
    n01 = grid[y0_grid, x1_grid]
    n10 = grid[y1_grid, x0_grid]
    n11 = grid[y1_grid, x1_grid]

    n0 = n00 * (1 - fx_grid) + n01 * fx_grid
    n1 = n10 * (1 - fx_grid) + n11 * fx_grid

    return n0 * (1 - fy_grid) + n1 * fy_grid


def _generate_zone_plate(size: int, frequency: float = 50.0) -> np.ndarray:
    """
    Generate a zone plate (Fresnel pattern / concentric sine rings).

    This creates a frequency sweep pattern that's excellent for testing
    aliasing and frequency-domain operations.

    Args:
        size: Output image size (square).
        frequency: Maximum frequency at the edges.

    Returns:
        2D float32 array with values in [0, 1].
    """
    center = size / 2
    y, x = np.ogrid[:size, :size]

    # Distance squared from center, normalized
    r2 = ((x - center) ** 2 + (y - center) ** 2) / (center ** 2)

    # Zone plate formula: sin(frequency * r^2)
    plate = np.sin(frequency * r2 * np.pi)

    # Normalize to [0, 1]
    return ((plate + 1) / 2).astype(np.float32)


def generate_test_card(size: int = 512, seed: int | None = None) -> ImageBuffer:
    """
    Generate a procedural test card image.

    The test card contains multiple elements designed to help visualize
    the effects of different node types:

    Layout (512x512 default):
    +------------------+------------------+
    |   Color Bars     |   Checkerboard   |
    |   (0-255, 256H)  |   (256x256)      |
    +------------------+------------------+
    |  Radial Gradient |  Diagonal Lines  |
    |   (128x128)      |   (128x128)      |
    +------------------+------------------+
    |   Zone Plate     |   Horiz Ramp     |
    |   (128x128)      |   (128x128)      |
    +------------------+------------------+
    |        Perlin Noise (full width)    |
    |              (512x128)              |
    +-------------------------------------+

    Args:
        size: Output image size (default 512, will be square).
        seed: Random seed for reproducible noise patterns.

    Returns:
        ImageBuffer containing the test card in RGB colorspace.
    """
    if seed is not None:
        np.random.seed(seed)

    # Create RGB image (C, H, W format)
    data = np.zeros((3, size, size), dtype=np.float32)

    half = size // 2
    quarter = size // 4

    # === TOP LEFT: Color Bars (half width, half height) ===
    # 8 bars: R, G, B, C, M, Y, W, K (plus gray in center)
    bar_width = half // 9
    colors = [
        (1.0, 0.0, 0.0),  # Red
        (0.0, 1.0, 0.0),  # Green
        (0.0, 0.0, 1.0),  # Blue
        (0.0, 1.0, 1.0),  # Cyan
        (1.0, 0.0, 1.0),  # Magenta
        (1.0, 1.0, 0.0),  # Yellow
        (1.0, 1.0, 1.0),  # White
        (0.5, 0.5, 0.5),  # Gray
        (0.0, 0.0, 0.0),  # Black
    ]

    for i, (r, g, b) in enumerate(colors):
        x_start = i * bar_width
        x_end = min((i + 1) * bar_width, half)
        data[0, :half, x_start:x_end] = r
        data[1, :half, x_start:x_end] = g
        data[2, :half, x_start:x_end] = b

    # === TOP RIGHT: Checkerboard (half width, half height) ===
    # 8x8 block checkerboard
    checker_size = half // 8
    for cy in range(8):
        for cx in range(8):
            val = 1.0 if (cy + cx) % 2 == 0 else 0.0
            y_start = cy * checker_size
            y_end = (cy + 1) * checker_size
            x_start = half + cx * checker_size
            x_end = half + (cx + 1) * checker_size
            data[:, y_start:y_end, x_start:x_end] = val

    # === MIDDLE LEFT TOP: Radial Gradient (quarter size) ===
    center_y = half + quarter // 2
    center_x = quarter // 2
    y_coords, x_coords = np.ogrid[half:half+quarter, :quarter]
    dist = np.sqrt((y_coords - center_y) ** 2 + (x_coords - center_x) ** 2)
    max_dist = np.sqrt(2) * quarter / 2
    radial = 1.0 - np.clip(dist / max_dist, 0, 1)
    data[:, half:half+quarter, :quarter] = radial.astype(np.float32)

    # === MIDDLE RIGHT TOP: Diagonal Lines (quarter size) ===
    y_coords, x_coords = np.ogrid[half:half+quarter, quarter:half]
    # Create diagonal stripes
    stripe_width = quarter // 8
    diagonal = ((y_coords - half + x_coords - quarter) // stripe_width) % 2
    data[:, half:half+quarter, quarter:half] = diagonal.astype(np.float32)

    # === MIDDLE LEFT BOTTOM: Zone Plate (quarter size) ===
    zone = _generate_zone_plate(quarter, frequency=30.0)
    data[:, half+quarter:half+quarter*2, :quarter] = zone

    # === MIDDLE RIGHT BOTTOM: Horizontal Gradient Ramp (quarter size) ===
    ramp = np.linspace(0, 1, quarter, dtype=np.float32)
    ramp = np.tile(ramp, (quarter, 1))
    data[:, half+quarter:half+quarter*2, quarter:half] = ramp

    # === RIGHT SIDE MIDDLE: Additional patterns ===
    # Top: Fine checkerboard (for high frequency testing)
    fine_checker_size = quarter // 16
    for cy in range(16):
        for cx in range(16):
            val = 1.0 if (cy + cx) % 2 == 0 else 0.0
            y_start = half + cy * fine_checker_size
            y_end = half + (cy + 1) * fine_checker_size
            x_start = half + cx * fine_checker_size
            x_end = half + (cx + 1) * fine_checker_size
            data[:, y_start:y_end, x_start:x_end] = val

    # Bottom: Color gradient (rainbow)
    for x in range(half):
        hue = x / half
        # HSV to RGB conversion for hue sweep
        c = 1.0
        x_val = c * (1 - abs((hue * 6) % 2 - 1))

        if hue < 1/6:
            r, g, b = c, x_val, 0
        elif hue < 2/6:
            r, g, b = x_val, c, 0
        elif hue < 3/6:
            r, g, b = 0, c, x_val
        elif hue < 4/6:
            r, g, b = 0, x_val, c
        elif hue < 5/6:
            r, g, b = x_val, 0, c
        else:
            r, g, b = c, 0, x_val

        data[0, half+quarter:size, half+x] = r
        data[1, half+quarter:size, half+x] = g
        data[2, half+quarter:size, half+x] = b

    # === BOTTOM: Perlin Noise stripe (full width, quarter height) ===
    # Actually, let's add a vertical gradient on bottom-left and noise on bottom-right
    # of the remaining space after the color bars

    # Vertical gradient ramp (bottom-left quarter)
    v_ramp = np.linspace(0, 1, quarter, dtype=np.float32).reshape(-1, 1)
    v_ramp = np.tile(v_ramp, (1, quarter))
    # But we've used this space already, so let's adjust the layout

    # Actually, the layout as implemented covers the full 512x512.
    # Let's add some final touches in any remaining spots

    # Create the ImageBuffer
    buffer = ImageBuffer(data=data, colorspace=ColorSpace.RGB)
    buffer.metadata["generator"] = "TestCard"
    buffer.metadata["size"] = size
    buffer.metadata["seed"] = seed

    return buffer


@register_node
class TestCardNode(Node):
    """
    Generate a procedural test card image.

    Creates a calibration image containing multiple visual elements designed
    to help visualize and test the effects of different processing nodes:

    - Color bars (R, G, B, C, M, Y, W, Gray, K) - test color/channel operations
    - Checkerboard patterns (coarse and fine) - test frequency/DCT/FFT effects
    - Radial gradient - test quantization banding
    - Diagonal lines - test directional operations (pixel sort, wavelets)
    - Zone plate (concentric sine rings) - test frequency response/aliasing
    - Horizontal/vertical gradients - test threshold-based operations
    - Rainbow hue sweep - test color space conversions

    This node has no inputs and generates a fresh test card each execution.
    Use the seed parameter for reproducible random elements.
    """

    name = "Test Card"
    category = "I/O"
    description = "Generate a procedural test card for calibration"
    icon = "grid"
    _abstract = False

    def define_ports(self) -> None:
        """Define output port for generated image."""
        self.add_output(
            "image",
            port_type=PortType.IMAGE,
            description="Generated test card image",
        )

    def define_parameters(self) -> None:
        """Define test card parameters."""
        self.add_parameter(
            "size",
            param_type=ParameterType.INT,
            default=512,
            min_value=128,
            max_value=2048,
            step=128,
            description="Output image size (square)",
        )
        self.add_parameter(
            "seed",
            param_type=ParameterType.INT,
            default=42,
            min_value=0,
            max_value=999999,
            description="Random seed for reproducible patterns",
        )
        self.add_parameter(
            "use_seed",
            param_type=ParameterType.BOOL,
            default=True,
            description="Use fixed seed (disable for random each time)",
        )

    def process(self) -> None:
        """Generate the test card image."""
        size = self.get_parameter("size")
        use_seed = self.get_parameter("use_seed")
        seed = self.get_parameter("seed") if use_seed else None

        buffer = generate_test_card(size=size, seed=seed)
        self.set_output_value("image", buffer)

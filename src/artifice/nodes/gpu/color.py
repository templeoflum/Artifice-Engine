"""GPU-accelerated color processing nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from artifice.core.gpu_node import GPUNode, ShaderUniform
from artifice.core.node import ParameterType
from artifice.core.port import PortType
from artifice.core.registry import register_node

if TYPE_CHECKING:
    pass


@register_node
class ColorSpaceGPUNode(GPUNode):
    """GPU-accelerated color space conversion.

    Converts between all 16 GLIC color spaces:

    Perceptual (good for gradients):
    - LAB: Perceptually uniform, excellent for color manipulation
    - LUV: Similar to LAB, better for additive color
    - HCL: Cylindrical LAB, intuitive hue control

    Video/Compression:
    - YCbCr: JPEG/MPEG standard, separates luma from chroma
    - YUV: Analog video standard
    - YPbPr: Component video
    - YDbDr: SECAM video

    Artist-Friendly:
    - HSV/HSB: Intuitive hue/saturation/brightness
    - HSL: Similar but different lightness model
    - HWB: Hue/whiteness/blackness (CSS standard)

    Scientific:
    - XYZ: CIE 1931, device-independent
    - YXY: Chromaticity diagram coordinates

    Special:
    - CMY: Subtractive color (print)
    - OHTA: Optimal color features
    - GREY: Grayscale (luma only)

    Glitch effects work best by processing in a luma-chroma space
    (YCbCr, LAB) then corrupting the chroma channels while
    preserving luma for structure.
    """

    name = "Color Space (GPU)"
    category = "Color"
    description = "Convert between all 16 GLIC color spaces (GPU accelerated)"
    shader_file = "color/colorspace.glsl"
    _abstract = False

    uniforms: ClassVar[list[ShaderUniform]] = [
        ShaderUniform("from_space", "from_space", "int", 0),
        ShaderUniform("to_space", "to_space", "int", 1),
    ]

    # All 16 GLIC color spaces - order must match shader defines
    SPACES = [
        "RGB",      # 0: Identity
        "HSV",      # 1: Hue-Saturation-Value
        "HSL",      # 2: Hue-Saturation-Lightness
        "YCbCr",    # 3: JPEG/MPEG luma-chroma
        "YUV",      # 4: Analog video
        "LAB",      # 5: CIE L*a*b* (perceptual)
        "XYZ",      # 6: CIE 1931
        "LUV",      # 7: CIE L*u*v*
        "HCL",      # 8: Hue-Chroma-Luma
        "CMY",      # 9: Cyan-Magenta-Yellow
        "HWB",      # 10: Hue-Whiteness-Blackness
        "YPbPr",    # 11: Component video
        "YDbDr",    # 12: SECAM video
        "OHTA",     # 13: Optimal features
        "YXY",      # 14: CIE chromaticity
        "GREY",     # 15: Grayscale
    ]

    # Map from string name to shader ID
    SPACE_MAP = {name: idx for idx, name in enumerate(SPACES)}

    def define_ports(self) -> None:
        self.add_input("image", PortType.IMAGE, "Input image")
        self.add_output("image", PortType.IMAGE, "Output image")

    def define_parameters(self) -> None:
        self.add_parameter(
            "from_space",
            param_type=ParameterType.ENUM,
            default="RGB",
            choices=self.SPACES,
            description="Source color space",
        )
        self.add_parameter(
            "to_space",
            param_type=ParameterType.ENUM,
            default="YCbCr",  # Default to YCbCr - best for glitch effects
            choices=self.SPACES,
            description="Target color space",
        )

    def _upload_uniforms(self) -> None:
        """Upload uniforms with enum conversion."""
        from_str = self.get_parameter("from_space")
        to_str = self.get_parameter("to_space")

        from_int = self.SPACE_MAP.get(from_str, 0)
        to_int = self.SPACE_MAP.get(to_str, 0)

        if "from_space" in self._compiled_shader:
            self._compiled_shader["from_space"].value = from_int
        if "to_space" in self._compiled_shader:
            self._compiled_shader["to_space"].value = to_int

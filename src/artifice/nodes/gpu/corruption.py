"""GPU-accelerated corruption nodes."""

from __future__ import annotations

from typing import ClassVar

from artifice.core.gpu_node import GPUNode, ShaderUniform
from artifice.core.node import ParameterType
from artifice.core.port import PortType
from artifice.core.registry import register_node


@register_node
class BitFlipGPUNode(GPUNode):
    """GPU-accelerated bit flip corruption."""

    name = "Bit Flip (GPU)"
    category = "Corruption"
    description = "Randomly flip bits in image data (GPU accelerated)"
    shader_file = "corruption/bitflip.glsl"
    _abstract = False

    uniforms: ClassVar[list[ShaderUniform]] = [
        ShaderUniform("probability", "probability", "float", 0.01),
        ShaderUniform("seed", "seed", "int", 0),
        ShaderUniform("bits_per_channel", "bits", "int", 8),
        ShaderUniform("affect_alpha", "affect_alpha", "bool", False),
    ]

    def define_ports(self) -> None:
        self.add_input("image", PortType.IMAGE, "Input image")
        self.add_output("image", PortType.IMAGE, "Output image")

    def define_parameters(self) -> None:
        self.add_parameter(
            "probability",
            param_type=ParameterType.FLOAT,
            default=0.01,
            min_value=0.0,
            max_value=1.0,
            step=0.001,
            description="Probability of flipping each bit",
        )
        self.add_parameter(
            "seed",
            param_type=ParameterType.INT,
            default=0,
            min_value=0,
            max_value=999999,
            description="Random seed for reproducibility",
        )
        self.add_parameter(
            "bits",
            param_type=ParameterType.INT,
            default=8,
            min_value=1,
            max_value=8,
            description="Number of bits per channel to consider",
        )
        self.add_parameter(
            "affect_alpha",
            param_type=ParameterType.BOOL,
            default=False,
            description="Whether to affect alpha channel",
        )


@register_node
class BitShiftGPUNode(GPUNode):
    """GPU-accelerated bit shift corruption."""

    name = "Bit Shift (GPU)"
    category = "Corruption"
    description = "Shift bits in image data (GPU accelerated)"
    shader_file = "corruption/bitshift.glsl"
    _abstract = False

    uniforms: ClassVar[list[ShaderUniform]] = [
        ShaderUniform("shift_amount", "shift", "int", 1),
        ShaderUniform("wrap", "wrap", "bool", True),
        ShaderUniform("affect_alpha", "affect_alpha", "bool", False),
    ]

    def define_ports(self) -> None:
        self.add_input("image", PortType.IMAGE, "Input image")
        self.add_output("image", PortType.IMAGE, "Output image")

    def define_parameters(self) -> None:
        self.add_parameter(
            "shift",
            param_type=ParameterType.INT,
            default=1,
            min_value=-7,
            max_value=7,
            description="Bit shift amount (negative = right shift)",
        )
        self.add_parameter(
            "wrap",
            param_type=ParameterType.BOOL,
            default=True,
            description="Wrap bits around (rotate) instead of shifting in zeros",
        )
        self.add_parameter(
            "affect_alpha",
            param_type=ParameterType.BOOL,
            default=False,
            description="Whether to affect alpha channel",
        )


@register_node
class XORNoiseGPUNode(GPUNode):
    """GPU-accelerated XOR noise corruption."""

    name = "XOR Noise (GPU)"
    category = "Corruption"
    description = "Apply XOR noise to image data (GPU accelerated)"
    shader_file = "corruption/xor_noise.glsl"
    _abstract = False

    uniforms: ClassVar[list[ShaderUniform]] = [
        ShaderUniform("noise_seed", "seed", "int", 0),
        ShaderUniform("intensity", "intensity", "float", 0.5),
        ShaderUniform("affect_alpha", "affect_alpha", "bool", False),
    ]

    def define_ports(self) -> None:
        self.add_input("image", PortType.IMAGE, "Input image")
        self.add_output("image", PortType.IMAGE, "Output image")

    def define_parameters(self) -> None:
        self.add_parameter(
            "seed",
            param_type=ParameterType.INT,
            default=0,
            min_value=0,
            max_value=999999,
            description="Random seed for noise generation",
        )
        self.add_parameter(
            "intensity",
            param_type=ParameterType.FLOAT,
            default=0.5,
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            description="Noise intensity (0-1)",
        )
        self.add_parameter(
            "affect_alpha",
            param_type=ParameterType.BOOL,
            default=False,
            description="Whether to affect alpha channel",
        )

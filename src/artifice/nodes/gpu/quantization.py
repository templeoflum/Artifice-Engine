"""GPU-accelerated quantization nodes."""

from __future__ import annotations

from typing import ClassVar

from artifice.core.gpu_node import GPUNode, ShaderUniform
from artifice.core.node import ParameterType
from artifice.core.port import PortType
from artifice.core.registry import register_node


@register_node
class QuantizeGPUNode(GPUNode):
    """GPU-accelerated quantization."""

    name = "Quantize (GPU)"
    category = "Quantization"
    description = "Reduce color precision (GPU accelerated)"
    shader_file = "quantization/quantize.glsl"
    _abstract = False

    uniforms: ClassVar[list[ShaderUniform]] = [
        ShaderUniform("levels", "levels", "int", 8),
        ShaderUniform("mode", "mode", "int", 0),
        ShaderUniform("dither", "dither", "bool", False),
        ShaderUniform("dither_strength", "dither_strength", "float", 1.0),
    ]

    def define_ports(self) -> None:
        self.add_input("image", PortType.IMAGE, "Input image")
        self.add_output("image", PortType.IMAGE, "Output image")

    def define_parameters(self) -> None:
        self.add_parameter(
            "levels",
            param_type=ParameterType.INT,
            default=8,
            min_value=2,
            max_value=256,
            description="Number of quantization levels",
        )
        self.add_parameter(
            "mode",
            param_type=ParameterType.ENUM,
            default="uniform",
            choices=["uniform", "adaptive", "per_channel"],
            description="Quantization mode",
        )
        self.add_parameter(
            "dither",
            param_type=ParameterType.BOOL,
            default=False,
            description="Apply ordered dithering",
        )
        self.add_parameter(
            "dither_strength",
            param_type=ParameterType.FLOAT,
            default=1.0,
            min_value=0.0,
            max_value=2.0,
            description="Dithering strength",
        )

    def _upload_uniforms(self) -> None:
        """Upload uniforms with enum conversion."""
        # Convert enum to int
        mode_str = self.get_parameter("mode")
        mode_map = {"uniform": 0, "adaptive": 1, "per_channel": 2}
        mode_int = mode_map.get(mode_str, 0)

        if "mode" in self._compiled_shader:
            self._compiled_shader["mode"].value = mode_int

        # Upload other uniforms normally
        for uniform in self.uniforms:
            if uniform.param_name == "mode":
                continue  # Already handled

            value = self.get_parameter(uniform.param_name)
            if uniform.uniform_type == "bool":
                value = 1 if value else 0

            if uniform.name in self._compiled_shader:
                self._compiled_shader[uniform.name].value = value

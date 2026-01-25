"""GPU-accelerated node base class.

Provides the foundation for nodes that execute on the GPU via compute shaders.
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from artifice.core.node import Node, ParameterType
from artifice.core.port import PortType

if TYPE_CHECKING:
    from artifice.gpu.backend import GPUBackend
    from artifice.gpu.texture import Texture


@dataclass
class ShaderUniform:
    """Describes a shader uniform parameter.

    Maps a node parameter to a shader uniform variable.
    """

    name: str                    # Uniform name in shader
    param_name: str              # Node parameter name
    uniform_type: str = "float"  # "float", "int", "bool", "vec2", etc.
    default: Any = 0.0


class GPUNode(Node):
    """Base class for GPU-accelerated nodes.

    GPU nodes execute their processing on the GPU using compute shaders.
    They can still have CPU fallback implementations for compatibility.

    Subclasses must define:
        - shader_file: Path to the GLSL compute shader
        - uniforms: List of ShaderUniform mappings
        - define_ports(): Port definitions
        - define_parameters(): Parameter definitions

    Example:
        class BitFlipGPU(GPUNode):
            name = "Bit Flip (GPU)"
            category = "Corruption"
            shader_file = "corruption/bitflip.glsl"
            uniforms = [
                ShaderUniform("probability", "probability", "float", 0.01),
                ShaderUniform("seed", "seed", "int", 0),
            ]
    """

    # Class attributes - override in subclasses
    shader_file: ClassVar[str] = ""  # Path relative to gpu/shaders/
    uniforms: ClassVar[list[ShaderUniform]] = []
    local_size: ClassVar[tuple[int, int, int]] = (16, 16, 1)  # Workgroup size

    # GPU state
    _compiled_shader: Any = None
    _backend: GPUBackend | None = None
    _input_textures: dict[str, Texture] = field(default_factory=dict)
    _output_textures: dict[str, Texture] = field(default_factory=dict)

    def __init__(self):
        super().__init__()
        self._compiled_shader = None
        self._backend = None
        self._input_textures = {}
        self._output_textures = {}

    def process(self) -> None:
        """CPU fallback - not used for GPU nodes.

        GPU nodes use execute_gpu() instead. This method exists to satisfy
        the Node base class abstract method requirement.
        """
        # GPU nodes don't use the CPU process path
        # They override execute_gpu() instead
        pass

    def compile(self, backend: GPUBackend) -> None:
        """Compile the compute shader.

        Called once when the node is added to a GPU graph.

        Args:
            backend: GPU backend to compile with
        """
        if not self.shader_file:
            raise ValueError(f"{self.__class__.__name__} has no shader_file defined")

        self._backend = backend
        shader_source = backend.load_shader(self.shader_file)
        self._compiled_shader = backend.compile_compute_shader(shader_source)

    @property
    def is_compiled(self) -> bool:
        """Return True if shader is compiled and ready."""
        return self._compiled_shader is not None

    def allocate_textures(self, backend: GPUBackend, width: int, height: int) -> None:
        """Allocate GPU textures for inputs/outputs.

        Args:
            backend: GPU backend
            width: Image width
            height: Image height
        """
        from artifice.gpu.backend import TextureFormat

        # Allocate output textures
        for port_name, port in self.outputs.items():
            if port.port_type == PortType.IMAGE:
                texture = backend.create_texture(width, height, TextureFormat.RGBA32F)
                self._output_textures[port_name] = texture

    def set_input_texture(self, port_name: str, texture: Texture) -> None:
        """Set the input texture for a port.

        Args:
            port_name: Name of the input port
            texture: GPU texture to use
        """
        self._input_textures[port_name] = texture

    def get_output_texture(self, port_name: str = "image") -> Texture | None:
        """Get the output texture for a port.

        Args:
            port_name: Name of the output port

        Returns:
            GPU texture or None if not allocated
        """
        return self._output_textures.get(port_name)

    def execute_gpu(self, backend: GPUBackend) -> None:
        """Execute the node on the GPU.

        This is the main GPU execution path. It:
        1. Binds input textures
        2. Binds output textures
        3. Uploads uniform parameters
        4. Dispatches the compute shader

        Args:
            backend: GPU backend
        """
        if not self.is_compiled:
            self.compile(backend)

        # Get output size from first input texture
        width, height = self._get_output_size()

        # Bind input textures
        binding = 0
        for port_name in self.inputs:
            if port_name in self._input_textures:
                texture = self._input_textures[port_name]
                texture.bind_as_image(binding, "read")
                binding += 1

        # Bind output textures
        for port_name in self.outputs:
            if port_name in self._output_textures:
                texture = self._output_textures[port_name]
                texture.bind_as_image(binding, "write")
                binding += 1

        # Upload uniforms
        self._upload_uniforms()

        # Calculate dispatch size
        local_x, local_y, local_z = self.local_size
        groups_x = (width + local_x - 1) // local_x
        groups_y = (height + local_y - 1) // local_y
        groups_z = 1

        # Dispatch
        backend.dispatch_compute(self._compiled_shader, groups_x, groups_y, groups_z)

        # Memory barrier to ensure writes are visible
        backend.memory_barrier()

    def _get_output_size(self) -> tuple[int, int]:
        """Get the output texture size.

        Returns:
            (width, height) tuple
        """
        # Use first input texture size
        for texture in self._input_textures.values():
            return (texture.width, texture.height)

        # Use first output texture size
        for texture in self._output_textures.values():
            return (texture.width, texture.height)

        # Default
        return (512, 512)

    def _upload_uniforms(self) -> None:
        """Upload parameter values to shader uniforms."""
        for uniform in self.uniforms:
            value = self.get_parameter(uniform.param_name)

            # Convert to shader value
            if uniform.uniform_type == "bool":
                value = 1 if value else 0

            # Set uniform on shader
            if uniform.name in self._compiled_shader:
                self._compiled_shader[uniform.name].value = value

    def release(self) -> None:
        """Release GPU resources."""
        # Release output textures
        if self._backend:
            for texture in self._output_textures.values():
                self._backend.destroy_texture(texture)

        self._output_textures.clear()
        self._input_textures.clear()
        self._compiled_shader = None
        self._backend = None


class GPUPassthroughNode(GPUNode):
    """A GPU node that passes input directly to output.

    Useful for testing the GPU pipeline without any processing.
    """

    name = "GPU Passthrough"
    category = "Utility"
    description = "Pass image through GPU pipeline unchanged"
    shader_file = ""  # No shader needed
    _abstract = False

    def define_ports(self) -> None:
        self.add_input("image", PortType.IMAGE, "Input image")
        self.add_output("image", PortType.IMAGE, "Output image")

    def define_parameters(self) -> None:
        pass

    def execute_gpu(self, backend: GPUBackend) -> None:
        """Just copy input to output."""
        if "image" in self._input_textures and "image" in self._output_textures:
            self._output_textures["image"].copy_from(self._input_textures["image"])

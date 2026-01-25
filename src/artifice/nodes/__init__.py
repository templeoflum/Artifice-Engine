"""
Artifice node implementations.

This package contains all built-in nodes organized by category.
"""

from artifice.nodes.generator import TestCardNode
from artifice.nodes.io import ImageLoaderNode, ImageSaverNode
from artifice.nodes.utility import NullNode

# GPU-accelerated nodes
from artifice.nodes.gpu import (
    TestCardGPUNode,
    BitFlipGPUNode,
    BitShiftGPUNode,
    XORNoiseGPUNode,
    ColorSpaceGPUNode,
    QuantizeGPUNode,
)

# Backwards compatibility alias
PassThroughNode = NullNode

__all__ = [
    "ImageLoaderNode",
    "ImageSaverNode",
    "NullNode",
    "PassThroughNode",  # Deprecated alias
    "TestCardNode",
    # GPU nodes
    "TestCardGPUNode",
    "BitFlipGPUNode",
    "BitShiftGPUNode",
    "XORNoiseGPUNode",
    "ColorSpaceGPUNode",
    "QuantizeGPUNode",
]

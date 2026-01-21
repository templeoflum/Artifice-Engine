"""Utility nodes."""

from artifice.nodes.utility.passthrough import NullNode

# Backwards compatibility alias
PassThroughNode = NullNode

__all__ = [
    "NullNode",
    "PassThroughNode",  # Deprecated alias
]

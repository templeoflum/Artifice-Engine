"""Real-time GPU-accelerated preview widget.

Provides a preview that displays GPU-rendered frames.
For initial testing, frames are downloaded from GPU and displayed via Qt.
Future versions will use QOpenGLWidget for zero-copy display.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QImage, QPixmap, QPainter
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QHBoxLayout

if TYPE_CHECKING:
    from artifice.core.stream_executor import StreamExecutor, ExecutorStats
    from artifice.gpu.backend import GPUBackend
    from artifice.gpu.texture import Texture


class RealtimePreviewWidget(QWidget):
    """Real-time preview widget.

    Displays frames from the StreamExecutor. Currently downloads
    frames from GPU for display (fast enough for testing).
    """

    # Signals
    fps_updated = Signal(float)
    frame_rendered = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # GPU resources
        self._backend: GPUBackend | None = None
        self._executor: StreamExecutor | None = None
        self._display_texture: Texture | None = None

        # Display state
        self._current_pixmap: QPixmap | None = None
        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setMinimumSize(320, 240)
        self._image_label.setStyleSheet("background-color: #1a1a1a;")

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._image_label)

        # FPS counter
        self._frame_count = 0
        self._fps_timer = QTimer(self)
        self._fps_timer.timeout.connect(self._update_fps)
        self._fps_timer.start(1000)  # Update every second
        self._last_fps = 0.0

    def set_backend(self, backend: GPUBackend) -> None:
        """Set the GPU backend.

        Args:
            backend: Initialized GPU backend
        """
        self._backend = backend

    def set_executor(self, executor: StreamExecutor) -> None:
        """Connect to a stream executor.

        Args:
            executor: Stream executor to display frames from
        """
        if self._executor:
            try:
                self._executor.frame_ready.disconnect(self._on_frame_ready)
            except RuntimeError:
                pass

        self._executor = executor
        executor.frame_ready.connect(self._on_frame_ready)

    def set_texture(self, texture: Texture) -> None:
        """Set a texture to display directly.

        Args:
            texture: GPU texture to display
        """
        self._display_texture = texture
        self._display_from_texture(texture)

    def set_image(self, image: np.ndarray) -> None:
        """Set a CPU image to display.

        Args:
            image: NumPy array (H, W, C) in [0, 1] or (C, H, W)
        """
        self._display_from_array(image)

    @Slot()
    def _on_frame_ready(self) -> None:
        """Handle new frame from executor."""
        if self._executor and self._executor.triple_buffer:
            texture = self._executor.triple_buffer.get_display_texture()
            if texture:
                self._display_from_texture(texture)
                self._frame_count += 1
                self.frame_rendered.emit()

    def _display_from_texture(self, texture: Texture) -> None:
        """Display a GPU texture (downloads to CPU)."""
        try:
            # Download from GPU
            data = texture.download()
            self._display_from_array(data)
        except Exception:
            pass

    def _display_from_array(self, data: np.ndarray) -> None:
        """Display a NumPy array."""
        if data is None:
            return

        # Handle channel-first format (C, H, W) -> (H, W, C)
        if data.ndim == 3 and data.shape[0] in (1, 3, 4):
            data = np.transpose(data, (1, 2, 0))

        # Ensure we have the right shape
        if data.ndim == 2:
            data = data[:, :, np.newaxis]

        h, w = data.shape[:2]
        channels = data.shape[2] if data.ndim == 3 else 1

        # Convert to 8-bit
        if data.dtype == np.float32 or data.dtype == np.float64:
            data = (np.clip(data, 0, 1) * 255).astype(np.uint8)
        elif data.dtype != np.uint8:
            data = data.astype(np.uint8)

        # Ensure contiguous
        data = np.ascontiguousarray(data)

        # Create QImage
        if channels == 1:
            qimg = QImage(data.data, w, h, w, QImage.Format.Format_Grayscale8)
        elif channels == 3:
            qimg = QImage(data.data, w, h, w * 3, QImage.Format.Format_RGB888)
        elif channels == 4:
            qimg = QImage(data.data, w, h, w * 4, QImage.Format.Format_RGBA8888)
        else:
            return

        # Scale to fit label while maintaining aspect ratio
        pixmap = QPixmap.fromImage(qimg)
        scaled = pixmap.scaled(
            self._image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._image_label.setPixmap(scaled)

    @Slot()
    def _update_fps(self) -> None:
        """Update FPS counter."""
        self._last_fps = float(self._frame_count)
        self._frame_count = 0
        self.fps_updated.emit(self._last_fps)

    @property
    def fps(self) -> float:
        """Return current FPS."""
        return self._last_fps

    def resizeEvent(self, event) -> None:
        """Handle resize - rescale current image."""
        super().resizeEvent(event)
        # Pixmap will be rescaled on next frame


class RealtimePreviewPanel(QWidget):
    """Complete preview panel with stats overlay.

    Wraps RealtimePreviewWidget with FPS display and controls.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Preview widget
        self._preview = RealtimePreviewWidget()
        layout.addWidget(self._preview, 1)

        # Stats bar
        stats_layout = QHBoxLayout()
        stats_layout.setContentsMargins(4, 2, 4, 2)

        self._fps_label = QLabel("FPS: --")
        self._fps_label.setStyleSheet("color: #888; font-size: 11px;")
        stats_layout.addWidget(self._fps_label)

        stats_layout.addStretch()

        self._resolution_label = QLabel("--x--")
        self._resolution_label.setStyleSheet("color: #888; font-size: 11px;")
        stats_layout.addWidget(self._resolution_label)

        layout.addLayout(stats_layout)

        # Connect signals
        self._preview.fps_updated.connect(self._on_fps_updated)

    @Slot(float)
    def _on_fps_updated(self, fps: float) -> None:
        """Update FPS display."""
        color = "#4f4" if fps >= 55 else "#ff4" if fps >= 30 else "#f44"
        self._fps_label.setText(f"FPS: {fps:.1f}")
        self._fps_label.setStyleSheet(f"color: {color}; font-size: 11px;")

    def set_backend(self, backend: GPUBackend) -> None:
        """Set the GPU backend."""
        self._preview.set_backend(backend)

    def set_executor(self, executor: StreamExecutor) -> None:
        """Connect to a stream executor."""
        self._preview.set_executor(executor)

        # Update resolution label
        if executor:
            w, h = executor._output_width, executor._output_height
            self._resolution_label.setText(f"{w}x{h}")

    def update_stats(self, stats: ExecutorStats) -> None:
        """Update stats display.

        Args:
            stats: Executor statistics
        """
        pass

    @property
    def preview_widget(self) -> RealtimePreviewWidget:
        """Return the preview widget."""
        return self._preview

"""
Main window implementation for the AI-Powered File Explorer.
This module provides the primary user interface and coordinates between services.
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QSplitter,
    QVBoxLayout,
    QMessageBox,
    QInputDialog,
    QMenuBar,
    QMenu,
    QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSlot, QSettings

from .file_explorer_panel import FileExplorerPanel
from .preview_panel import PreviewPanel
from .ai_panel import AIPanel
from .command_palette import CommandPalette
from services.file_system import FileSystemService, FileMetadata
from services.ai_service import AIService, AIResponse
from utils.config import Config

class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(
        self,
        file_service: FileSystemService,
        ai_service: AIService,
        config: Config,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        # Store service references
        self.file_service = file_service
        self.ai_service = ai_service
        self.config = config

        # Initialize UI state
        self.current_path: Optional[Path] = None
        self.selected_files: List[Path] = []
        self.settings = QSettings('AI-File-Explorer', 'MainWindow')

        # Set up UI
        self.setup_ui()
        self.restore_state()
        self.setup_connections()

        # Initialize command palette
        self.command_palette = CommandPalette(self)

    def setup_ui(self) -> None:
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("AI-Powered File Explorer")
        self.resize(1200, 800)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create main splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.main_splitter)

        # Create panels
        self.file_explorer = FileExplorerPanel(self.file_service)
        self.preview_panel = PreviewPanel(self.file_service)
        self.ai_panel = AIPanel(self.ai_service)

        # Add panels to splitter
        self.main_splitter.addWidget(self.file_explorer)
        self.main_splitter.addWidget(self.preview_panel)
        self.main_splitter.addWidget(self.ai_panel)

        # Set initial splitter sizes (ratios: 2/5, 2/5, 1/5)
        width = self.width()
        self.main_splitter.setSizes([
            int(width * 0.4),
            int(width * 0.4),
            int(width * 0.2)
        ])

        # Create menus
        self.create_menus()

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def create_menus(self) -> None:
        """Create application menus."""
        menubar = QMenuBar()
        self.setMenuBar(menubar)

        # File menu
        file_menu = menubar.addMenu('&File')
        file_menu.addAction('&Open Folder...', self.open_folder)
        file_menu.addAction('&Settings...', self.show_settings)
        file_menu.addSeparator()
        file_menu.addAction('&Exit', self.close)

        # View menu
        view_menu = menubar.addMenu('&View')
        view_menu.addAction('&Command Palette',
                          self.show_command_palette,
                          'Ctrl+P')

        # Help menu
        help_menu = menubar.addMenu('&Help')
        help_menu.addAction('&About', self.show_about)

    def setup_connections(self) -> None:
        """Set up signal/slot connections between components."""
        # File explorer signals
        self.file_explorer.current_path_changed.connect(self.on_current_path_changed)
        self.file_explorer.selection_changed.connect(self.on_selection_changed)
        self.file_explorer.error_occurred.connect(self.show_error)

        # Preview panel signals
        self.preview_panel.error_occurred.connect(self.show_error)

        # AI panel signals
        self.ai_panel.error_occurred.connect(self.show_error)
        self.ai_panel.status_message.connect(self.status_bar.showMessage)

        # Service signals
        self.file_service.event_emitter.error_occurred.connect(self.show_error)
        self.ai_service.event_emitter.error_occurred.connect(self.show_error)

    @pyqtSlot(Path)
    def on_current_path_changed(self, path: Path) -> None:
        """Handle current path changes from file explorer.

        Args:
            path: New current path
        """
        self.current_path = path
        self.status_bar.showMessage(f"Current path: {path}")

        # Update AI context
        self.ai_service.update_context(
            workspace_path=path,
            selected_files=self.selected_files
        )

    @pyqtSlot(list)
    def on_selection_changed(self, paths: List[Path]) -> None:
        """Handle file selection changes.

        Args:
            paths: List of selected file paths
        """
        self.selected_files = paths

        # Update preview if single file selected
        if len(paths) == 1:
            self.preview_panel.preview_file(paths[0])
        else:
            self.preview_panel.clear_preview()

        # Update AI context
        self.ai_service.update_context(
            workspace_path=self.current_path,
            selected_files=paths
        )

    def open_folder(self) -> None:
        """Show folder selection dialog and navigate to selected folder."""
        from PyQt6.QtWidgets import QFileDialog

        path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            str(self.current_path or Path.home())
        )

        if path:
            self.file_explorer.navigate_to(Path(path))

    def show_settings(self) -> None:
        """Show settings dialog."""
        # To be implemented
        pass

    def show_command_palette(self) -> None:
        """Show the command palette."""
        self.command_palette.show()

    def show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About AI-Powered File Explorer",
            "An intelligent file explorer powered by Claude AI.\n\n"
            "Version: 1.0.0\n"
            "© 2024"
        )

    def show_error(self, message: str) -> None:
        """Show error message to user.

        Args:
            message: Error message to display
        """
        QMessageBox.critical(self, "Error", message)
        logging.error(message)

    def save_state(self) -> None:
        """Save window state and settings."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("splitterSizes", self.main_splitter.sizes())

        if self.current_path:
            self.settings.setValue("lastPath", str(self.current_path))

    def restore_state(self) -> None:
        """Restore saved window state and settings."""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)

        sizes = self.settings.value("splitterSizes")
        if sizes:
            self.main_splitter.setSizes(sizes)

        last_path = self.settings.value("lastPath")
        if last_path:
            path = Path(last_path)
            if path.exists():
                self.file_explorer.navigate_to(path)

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        self.save_state()
        super().closeEvent(event)
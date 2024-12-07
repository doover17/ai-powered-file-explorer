#!/usr/bin/env python3

"""
Main entry point for the AI-Powered File Explorer application.
This module initializes the application, sets up logging, and launches the main window.
"""

import sys
import os
import logging
import asyncio
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Local imports
from ui.main_window import MainWindow
from services.file_system import FileSystemService
from services.ai_service import AIService
from utils.config import load_config, Config
from utils.logging_config import setup_logging

class Application:
    """Main application class that handles initialization and cleanup."""

    def __init__(self):
        self.app: Optional[QApplication] = None
        self.window: Optional[MainWindow] = None
        self.file_service: Optional[FileSystemService] = None
        self.ai_service: Optional[AIService] = None
        self.config: Optional[Config] = None

    async def initialize(self) -> None:
        """Initialize application components."""
        try:
            # Load configuration
            self.config = load_config()

            # Setup logging
            setup_logging(self.config.log_level)
            logging.info("Starting AI-Powered File Explorer")

            # Initialize services
            self.file_service = FileSystemService()
            await self.file_service.initialize()

            self.ai_service = AIService(api_key=os.getenv('ANTHROPIC_API_KEY'))
            await self.ai_service.initialize()

            # Create Qt application
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("AI-Powered File Explorer")

            # Create and show main window
            self.window = MainWindow(
                file_service=self.file_service,
                ai_service=self.ai_service,
                config=self.config
            )
            self.window.show()

            logging.info("Application initialized successfully")

        except Exception as e:
            logging.error(f"Failed to initialize application: {e}")
            raise

    async def cleanup(self) -> None:
        """Cleanup and shutdown application components."""
        logging.info("Shutting down application")

        if self.file_service:
            await self.file_service.cleanup()

        if self.ai_service:
            await self.ai_service.cleanup()

    def run(self) -> int:
        """Run the application main loop."""
        return self.app.exec() if self.app else 1

async def main() -> int:
    """Main entry point for the application."""
    app = Application()
    try:
        await app.initialize()
        result = app.run()
        await app.cleanup()
        return result
    except Exception as e:
        logging.critical(f"Application failed: {e}")
        return 1

if __name__ == "__main__":
    # Set Qt platform properties
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)

    # Run the application
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logging.info("Application terminated by user")
        sys.exit(0)
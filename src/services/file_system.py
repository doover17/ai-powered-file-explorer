"""
File system service for handling file operations and monitoring.
This module provides asynchronous file operations and real-time file system monitoring.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Set, Optional, AsyncGenerator
from datetime import datetime
import aiofiles
import magic
from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    FileCreatedEvent,
    FileModifiedEvent,
    FileDeletedEvent
)
from PyQt6.QtCore import QObject, pyqtSignal


class FileSystemEventEmitter(QObject):
    """Qt signal emitter for file system events."""
    file_created = pyqtSignal(Path)
    file_modified = pyqtSignal(Path)
    file_deleted = pyqtSignal(Path)
    error_occurred = pyqtSignal(str)


class FileSystemHandler(FileSystemEventHandler):
    """Watchdog event handler for file system changes."""

    def __init__(self, emitter: FileSystemEventEmitter):
        super().__init__()
        self.emitter = emitter

    def on_created(self, event: FileCreatedEvent) -> None:
        if not event.is_directory:
            self.emitter.file_created.emit(Path(event.src_path))

    def on_modified(self, event: FileModifiedEvent) -> None:
        if not event.is_directory:
            self.emitter.file_modified.emit(Path(event.src_path))

    def on_deleted(self, event: FileDeletedEvent) -> None:
        if not event.is_directory:
            self.emitter.file_deleted.emit(Path(event.src_path))


class FileMetadata:
    """Container for file metadata."""

    def __init__(
        self,
        path: Path,
        size: int,
        modified_time: datetime,
        mime_type: str,
        is_hidden: bool = False
    ):
        self.path = path
        self.size = size
        self.modified_time = modified_time
        self.mime_type = mime_type
        self.is_hidden = is_hidden


class FileSystemService:
    """Service for handling file system operations and monitoring."""

    def __init__(self, chunk_size: int = 1024 * 1024):  # 1MB chunks
        self.chunk_size = chunk_size
        self.observer = Observer()
        self.event_emitter = FileSystemEventEmitter()
        self.event_handler = FileSystemHandler(self.event_emitter)
        self.monitored_paths: Set[Path] = set()
        self.metadata_cache: Dict[Path, FileMetadata] = {}
        self._is_initialized = False

    async def initialize(self) -> None:
        """Initialize the file system service."""
        if self._is_initialized:
            return

        try:
            self.observer.start()
            self._is_initialized = True
            logging.info("FileSystemService initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize FileSystemService: {e}")
            raise

    async def cleanup(self) -> None:
        """Clean up resources and stop file monitoring."""
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
        self.monitored_paths.clear()
        self.metadata_cache.clear()
        self._is_initialized = False

    async def start_monitoring(self, path: Path) -> None:
        """Start monitoring a directory for changes.

        Args:
            path: Directory path to monitor

        Raises:
            FileNotFoundError: If the path doesn't exist
            PermissionError: If we don't have permission to monitor the path
        """
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")

        try:
            if path not in self.monitored_paths:
                self.observer.schedule(
                    self.event_handler,
                    str(path),
                    recursive=True
                )
                self.monitored_paths.add(path)
                logging.info(f"Started monitoring directory: {path}")
        except Exception as e:
            self.event_emitter.error_occurred.emit(str(e))
            raise

    async def stop_monitoring(self, path: Path) -> None:
        """Stop monitoring a specific directory."""
        if path in self.monitored_paths:
            for watch in self.observer.watches.copy():
                if Path(watch) == path:
                    self.observer.unschedule(self.observer.watches[watch])
            self.monitored_paths.remove(path)
            logging.info(f"Stopped monitoring directory: {path}")

    async def get_metadata(self, path: Path) -> FileMetadata:
        """Get metadata for a file.

        Args:
            path: Path to the file

        Returns:
            FileMetadata object containing file information

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        if path in self.metadata_cache:
            return self.metadata_cache[path]

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        stats = path.stat()
        mime_type = magic.from_file(str(path), mime=True)
        is_hidden = path.name.startswith('.')

        metadata = FileMetadata(
            path=path,
            size=stats.st_size,
            modified_time=datetime.fromtimestamp(stats.st_mtime),
            mime_type=mime_type,
            is_hidden=is_hidden
        )

        self.metadata_cache[path] = metadata
        return metadata

    async def read_file(self, path: Path) -> str:
        """Read a file's contents asynchronously.

        Args:
            path: Path to the file to read

        Returns:
            File contents as a string

        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If we don't have permission to read the file
        """
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            async with aiofiles.open(path, 'r') as f:
                return await f.read()
        except UnicodeDecodeError:
            # If text reading fails, try binary mode
            async with aiofiles.open(path, 'rb') as f:
                return (await f.read()).decode('utf-8', errors='ignore')

    async def read_binary(self, path: Path) -> AsyncGenerator[bytes, None]:
        """Read a binary file in chunks asynchronously.

        Args:
            path: Path to the file to read

        Yields:
            File contents in chunks
        """
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        async with aiofiles.open(path, 'rb') as f:
            while chunk := await f.read(self.chunk_size):
                yield chunk

    async def write_file(
        self,
        path: Path,
        content: str,
        create_dirs: bool = True
    ) -> None:
        """Write content to a file asynchronously.

        Args:
            path: Path to write the file to
            content: Content to write
            create_dirs: Whether to create parent directories if they don't exist
        """
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(path, 'w') as f:
            await f.write(content)
            await f.flush()

        # Clear metadata cache for this file
        self.metadata_cache.pop(path, None)

    async def delete_file(self, path: Path) -> None:
        """Delete a file.

        Args:
            path: Path to the file to delete

        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If we don't have permission to delete the file
        """
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            path.unlink()
            self.metadata_cache.pop(path, None)
        except Exception as e:
            self.event_emitter.error_occurred.emit(str(e))
            raise

    async def list_directory(
        self,
        path: Path,
        include_hidden: bool = False
    ) -> AsyncGenerator[FileMetadata, None]:
        """List contents of a directory asynchronously.

        Args:
            path: Directory path to list
            include_hidden: Whether to include hidden files

        Yields:
            FileMetadata objects for each item in the directory
        """
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")

        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")

        try:
            for item in path.iterdir():
                try:
                    metadata = await self.get_metadata(item)
                    if include_hidden or not metadata.is_hidden:
                        yield metadata
                except (PermissionError, FileNotFoundError) as e:
                    logging.warning(f"Error accessing {item}: {e}")
                    continue
        except Exception as e:
            self.event_emitter.error_occurred.emit(str(e))
            raise

    def clear_metadata_cache(self) -> None:
        """Clear the metadata cache."""
        self.metadata_cache.clear()

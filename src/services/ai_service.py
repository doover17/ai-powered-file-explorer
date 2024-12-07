"""
AI service for handling Claude API integration and context management.
This module manages AI interactions, context tracking, and command processing.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from anthropic import AsyncAnthropic, APIError, APITimeoutError, RateLimitError
from PyQt6.QtCore import QObject, pyqtSignal


@dataclass
class AIContext:
    """Container for AI conversation context."""
    workspace_path: Optional[Path]
    selected_files: List[Path]
    last_command: Optional[str]
    last_response: Optional[str]
    timestamp: datetime


@dataclass
class AIResponse:
    """Container for AI response data."""
    content: str
    context: AIContext
    metadata: Dict[str, Any]


class AIEventEmitter(QObject):
    """Qt signal emitter for AI service events."""
    response_started = pyqtSignal()
    response_chunk = pyqtSignal(str)
    response_complete = pyqtSignal(AIResponse)
    error_occurred = pyqtSignal(str)


class AIService:
    """Service for handling AI operations and context management."""

    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        if not api_key:
            raise ValueError("API key is required")

        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        self.event_emitter = AIEventEmitter()
        self.context: Optional[AIContext] = None
        self.rate_limiter = AsyncRateLimiter(requests_per_minute=50)
        self._is_initialized = False

    async def initialize(self) -> None:
        """Initialize the AI service and verify API connection."""
        if self._is_initialized:
            return

        try:
            # Test API connection
            await self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Test connection"}]
            )
            self._is_initialized = True
            logging.info("AIService initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize AIService: {e}")
            raise

    async def cleanup(self) -> None:
        """Clean up resources and clear context."""
        self.context = None
        self._is_initialized = False

    async def update_context(
        self,
        workspace_path: Optional[Path] = None,
        selected_files: Optional[List[Path]] = None
    ) -> None:
        """Update the current AI context.

        Args:
            workspace_path: Current workspace directory
            selected_files: Currently selected files
        """
        self.context = AIContext(
            workspace_path=workspace_path,
            selected_files=selected_files or [],
            last_command=self.context.last_command if self.context else None,
            last_response=self.context.last_response if self.context else None,
            timestamp=datetime.now()
        )

    async def process_command(self, command: str) -> AIResponse:
        """Process an AI command with current context.

        Args:
            command: User command to process

        Returns:
            AIResponse containing the AI's response

        Raises:
            ConnectionError: If API connection fails
            RateLimitError: If API rate limit is exceeded
        """
        if not self._is_initialized:
            raise RuntimeError("AIService not initialized")

        # Wait for rate limit token
        await self.rate_limiter.acquire()

        try:
            # Build system prompt with context
            system_prompt = self._build_system_prompt()

            # Prepare messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": command}
            ]

            # Signal response start
            self.event_emitter.response_started.emit()

            # Stream response
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=messages,
                stream=True
            )

            # Process response stream
            full_response = []
            async for chunk in response:
                if chunk.content:
                    full_response.append(chunk.content)
                    self.event_emitter.response_chunk.emit(chunk.content)

            # Combine response chunks
            complete_response = "".join(full_response)

            # Update context
            if self.context:
                self.context.last_command = command
                self.context.last_response = complete_response
                self.context.timestamp = datetime.now()

            # Create response object
            ai_response = AIResponse(
                content=complete_response,
                context=self.context.copy() if self.context else None,
                metadata={
                    "model": self.model,
                    "timestamp": datetime.now(),
                    # Approximate
                    "tokens_used": len(complete_response.split())
                }
            )

            # Signal completion
            self.event_emitter.response_complete.emit(ai_response)
            return ai_response

        except APITimeoutError:
            error_msg = "AI request timed out"
            self.event_emitter.error_occurred.emit(error_msg)
            raise ConnectionError(error_msg)

        except RateLimitError:
            error_msg = "AI rate limit exceeded"
            self.event_emitter.error_occurred.emit(error_msg)
            raise

        except APIError as e:
            error_msg = f"AI API error: {e}"
            self.event_emitter.error_occurred.emit(error_msg)
            raise ConnectionError(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error in AI processing: {e}"
            self.event_emitter.error_occurred.emit(error_msg)
            raise

    def _build_system_prompt(self) -> str:
        """Build the system prompt using current context."""
        if not self.context:
            return "You are an AI assistant helping with file management."

        prompt_parts = [
            "You are an AI assistant helping with file management.",
            f"Current workspace: {self.context.workspace_path}",
        ]

        if self.context.selected_files:
            files_str = "\n".join(str(f) for f in self.context.selected_files)
            prompt_parts.append(f"Selected files:\n{files_str}")

        if self.context.last_command:
            prompt_parts.append(f"Last command: {self.context.last_command}")

        return "\n\n".join(prompt_parts)


class AsyncRateLimiter:
    """Rate limiter for API requests."""

    def __init__(self, requests_per_minute: int):
        self.rate_limit = requests_per_minute
        self.tokens = requests_per_minute
        self.last_update = datetime.now()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire a rate limit token."""
        async with self._lock:
            while self.tokens <= 0:
                now = datetime.now()
                time_passed = (now - self.last_update).total_seconds() / 60.0
                self.tokens = min(
                    self.rate_limit,
                    self.tokens + time_passed * self.rate_limit
                )
                if self.tokens <= 0:
                    await asyncio.sleep(0.1)
                self.last_update = now

            self.tokens -= 1

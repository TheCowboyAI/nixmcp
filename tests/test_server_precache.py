"""Tests for the server pre-cache initialization functionality."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

# Import the necessary modules
from mcp_nixos.server import run_precache


class TestServerPrecache:
    """Test the pre-cache functionality in the server module."""

    @pytest.mark.asyncio
    async def test_run_precache_async_success(self):
        """Test successful pre-cache async operation."""
        # Create mock objects
        mock_hm_context = MagicMock()
        mock_hm_context.hm_client.load_in_background = MagicMock()
        mock_hm_context.hm_client.is_loaded = True
        mock_hm_context.hm_client.loading_lock.__enter__ = MagicMock()
        mock_hm_context.hm_client.loading_lock.__exit__ = MagicMock()

        mock_darwin_context = MagicMock()
        mock_darwin_context.startup = AsyncMock()
        mock_darwin_context.status = "ready"

        mock_logger = MagicMock()
        mock_async_timeout = AsyncMock(return_value=True)

        # Define patches that will be applied
        mock_targets = [
            patch("mcp_nixos.server.home_manager_context", mock_hm_context),
            patch("mcp_nixos.server.darwin_context", mock_darwin_context),
            patch("mcp_nixos.server.logger", mock_logger),
            patch("mcp_nixos.server.async_with_timeout", mock_async_timeout),
        ]

        # Apply all patches
        for p in mock_targets:
            p.start()

        try:
            # Import run_precache_async inside the patched context
            from mcp_nixos.server import run_precache_async

            # Execute the function
            result = await run_precache_async()

            # Verify the result and interactions
            assert result is True
            mock_hm_context.hm_client.load_in_background.assert_called_once()
            assert mock_async_timeout.called
        finally:
            # Stop all patches
            for p in mock_targets:
                p.stop()

    @pytest.mark.asyncio
    async def test_run_precache_async_darwin_error(self):
        """Test pre-cache async when Darwin context startup fails."""
        # Create mock objects
        mock_hm_context = MagicMock()
        mock_hm_context.hm_client.load_in_background = MagicMock()
        mock_hm_context.hm_client.is_loaded = True
        mock_hm_context.hm_client.loading_lock.__enter__ = MagicMock()
        mock_hm_context.hm_client.loading_lock.__exit__ = MagicMock()

        mock_darwin_context = MagicMock()

        mock_logger = MagicMock()
        # Create a mock that raises an exception
        mock_async_timeout = AsyncMock(side_effect=Exception("Darwin startup failed"))

        # Define patches that will be applied
        mock_targets = [
            patch("mcp_nixos.server.home_manager_context", mock_hm_context),
            patch("mcp_nixos.server.darwin_context", mock_darwin_context),
            patch("mcp_nixos.server.logger", mock_logger),
            patch("mcp_nixos.server.async_with_timeout", mock_async_timeout),
        ]

        # Apply all patches
        for p in mock_targets:
            p.start()

        try:
            # Import run_precache_async inside the patched context
            from mcp_nixos.server import run_precache_async

            # Execute the function
            result = await run_precache_async()

            # Verify the result and interactions
            assert result is True  # Should still return True as it continues execution
            mock_logger.error.assert_any_call("Error starting Darwin context: Darwin startup failed")
        finally:
            # Stop all patches
            for p in mock_targets:
                p.stop()

    @pytest.mark.asyncio
    async def test_run_precache_async_home_manager_timeout(self):
        """Test pre-cache async when Home Manager loading times out."""
        # Create mock objects
        mock_hm_context = MagicMock()
        mock_hm_context.hm_client.load_in_background = MagicMock()
        mock_hm_context.hm_client.is_loaded = False  # Will never complete loading
        mock_hm_context.hm_client.loading_error = None
        mock_hm_context.hm_client.loading_lock.__enter__ = MagicMock()
        mock_hm_context.hm_client.loading_lock.__exit__ = MagicMock()

        mock_darwin_context = MagicMock()
        mock_darwin_context.startup = AsyncMock()
        mock_darwin_context.status = "ready"

        mock_logger = MagicMock()
        mock_async_timeout = AsyncMock(return_value=True)

        # Define patches that will be applied
        mock_targets = [
            patch("mcp_nixos.server.home_manager_context", mock_hm_context),
            patch("mcp_nixos.server.darwin_context", mock_darwin_context),
            patch("mcp_nixos.server.logger", mock_logger),
            patch("mcp_nixos.server.async_with_timeout", mock_async_timeout),
            patch("time.time", side_effect=[0, 1000]),  # Simulate timeout
            patch("asyncio.sleep", AsyncMock()),
        ]

        # Apply all patches
        for p in mock_targets:
            p.start()

        try:
            # Import run_precache_async inside the patched context
            from mcp_nixos.server import run_precache_async

            # Execute the function
            result = await run_precache_async()

            # Verify the result and interactions
            assert result is True  # Should still return True as it continues execution
            mock_logger.warning.assert_any_call("Timed out after 120s waiting for Home Manager data to load")
        finally:
            # Stop all patches
            for p in mock_targets:
                p.stop()

    @pytest.mark.asyncio
    async def test_run_precache_async_home_manager_error(self):
        """Test pre-cache async when Home Manager loading has an error."""
        # Create mock objects
        mock_hm_context = MagicMock()
        mock_hm_context.hm_client.load_in_background = MagicMock()
        mock_hm_context.hm_client.is_loaded = False
        mock_hm_context.hm_client.loading_error = "Failed to load data"
        mock_hm_context.hm_client.loading_lock.__enter__ = MagicMock()
        mock_hm_context.hm_client.loading_lock.__exit__ = MagicMock()

        mock_darwin_context = MagicMock()
        mock_darwin_context.startup = AsyncMock()
        mock_darwin_context.status = "ready"

        mock_logger = MagicMock()
        mock_async_timeout = AsyncMock(return_value=True)

        # Define patches that will be applied
        mock_targets = [
            patch("mcp_nixos.server.home_manager_context", mock_hm_context),
            patch("mcp_nixos.server.darwin_context", mock_darwin_context),
            patch("mcp_nixos.server.logger", mock_logger),
            patch("mcp_nixos.server.async_with_timeout", mock_async_timeout),
            patch("asyncio.sleep", AsyncMock()),
        ]

        # Apply all patches
        for p in mock_targets:
            p.start()

        try:
            # Import run_precache_async inside the patched context
            from mcp_nixos.server import run_precache_async

            # Execute the function
            result = await run_precache_async()

            # Verify the result and interactions
            assert result is True  # Should still return True as it continues execution
            mock_logger.error.assert_any_call("Home Manager loading failed: Failed to load data")
        finally:
            # Stop all patches
            for p in mock_targets:
                p.stop()

    def test_run_precache_synchronous_success(self):
        """Test successful synchronous pre-cache operation."""
        # Create mock objects
        mock_logger = MagicMock()
        mock_asyncio_run = MagicMock(return_value=True)

        # Define patches that will be applied
        mock_targets = [patch("mcp_nixos.server.logger", mock_logger), patch("asyncio.run", mock_asyncio_run)]

        # Apply all patches
        for p in mock_targets:
            p.start()

        try:
            # Execute the function
            result = run_precache()

            # Verify the result and interactions
            assert result is True
            mock_asyncio_run.assert_called_once()
        finally:
            # Stop all patches
            for p in mock_targets:
                p.stop()

    def test_run_precache_keyboard_interrupt(self):
        """Test keyboard interrupt during pre-cache operation."""
        # Create mock objects
        mock_logger = MagicMock()
        mock_asyncio_run = MagicMock(side_effect=KeyboardInterrupt())

        # Define patches that will be applied
        mock_targets = [patch("mcp_nixos.server.logger", mock_logger), patch("asyncio.run", mock_asyncio_run)]

        # Apply all patches
        for p in mock_targets:
            p.start()

        try:
            # Execute the function
            result = run_precache()

            # Verify the result and interactions
            assert result is False
            mock_logger.info.assert_any_call("Pre-cache operation interrupted")
        finally:
            # Stop all patches
            for p in mock_targets:
                p.stop()

    def test_run_precache_general_exception(self):
        """Test general exception during pre-cache operation."""
        # Create mock objects
        mock_logger = MagicMock()
        mock_asyncio_run = MagicMock(side_effect=Exception("Test error"))

        # Define patches that will be applied
        mock_targets = [patch("mcp_nixos.server.logger", mock_logger), patch("asyncio.run", mock_asyncio_run)]

        # Apply all patches
        for p in mock_targets:
            p.start()

        try:
            # Execute the function
            result = run_precache()

            # Verify the result and interactions
            assert result is False
            mock_logger.error.assert_called_once()
            # Check the error message contains our test error
            assert "Test error" in mock_logger.error.call_args[0][0]
        finally:
            # Stop all patches
            for p in mock_targets:
                p.stop()

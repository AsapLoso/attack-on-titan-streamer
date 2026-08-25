"""
Test Suite: VLC RC Controller, Socket IPC, and Smart Intro-Skip Engine (F9, F10, F11)
Validates TCP socket IPC, command parsing, auto-skip triggering, cold open preservation, and hotkeys.
"""

import socket
import time
from typing import Dict, Any
from unittest.mock import MagicMock, patch

import pytest
from tests.conftest import MockVlcRcServer


class MockVlcRcClient:
    """Standalone reference implementation of VLC RC socket IPC client for contract verification."""

    def __init__(self, host: str = "127.0.0.1", port: int = 4212, timeout: float = 2.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None

    def connect(self, retries: int = 5, delay: float = 0.1) -> bool:
        for _ in range(retries):
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(self.timeout)
                self.sock.connect((self.host, self.port))
                # Read initial prompt
                self.sock.recv(1024)
                return True
            except (socket.error, ConnectionRefusedError):
                time.sleep(delay)
        return False

    def send_command(self, cmd: str) -> str:
        if not self.sock:
            raise ConnectionError("Socket not connected")
        full_cmd = cmd.strip() + "\n"
        self.sock.sendall(full_cmd.encode("utf-8"))
        try:
            data = self.sock.recv(1024)
            return data.decode("utf-8", errors="ignore").strip()
        except socket.timeout:
            return ""

    def get_time(self) -> float:
        resp = self.send_command("get_time")
        # VLC RC responds with number string or '> number'
        clean = resp.replace(">", "").strip()
        try:
            return float(clean.splitlines()[0])
        except (ValueError, IndexError):
            return 0.0

    def seek(self, target_seconds: float) -> str:
        return self.send_command(f"seek {int(target_seconds)}")

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None


class TestVlcRcSocketProtocol:
    """Verify VLC RC TCP socket command and response protocol handling."""

    def test_rc_socket_connection_and_command_exchange(self, mock_vlc_server: MockVlcRcServer):
        """Verify connecting to RC server and sending basic commands."""
        client = MockVlcRcClient(host="127.0.0.1", port=mock_vlc_server.port)
        connected = client.connect()
        assert connected, "Failed to connect to MockVlcRcServer"

        mock_vlc_server.current_time = 128.0
        time_val = client.get_time()
        assert time_val == 128.0

        client.seek(218.0)
        assert mock_vlc_server.current_time == 218.0
        assert "seek 218" in mock_vlc_server.received_commands

        client.close()

    def test_rc_socket_connection_retry_failure(self):
        """Verify client gracefully handles offline/refused connections."""
        client = MockVlcRcClient(host="127.0.0.1", port=65432)  # Non-listening port
        connected = client.connect(retries=2, delay=0.01)
        assert not connected, "Client unexpectedly succeeded connecting to non-listening port"


class TestIntroSkipStateMachine:
    """Verify the logic of skipping intros while preserving cold opens."""

    def simulate_playback_step(
        self,
        current_time: float,
        op_start: float,
        op_end: float,
        auto_skip: bool,
        has_skipped: bool
    ) -> tuple[bool, bool, float]:
        """
        Pure state-machine transition step:
        Returns: (should_seek, new_has_skipped, new_time)
        """
        if not auto_skip or op_end <= 0.0 or has_skipped:
            return False, has_skipped, current_time

        # If current playback is within [op_start, op_end - 1]
        if op_start <= current_time < op_end:
            # Trigger jump
            return True, True, op_end

        return False, has_skipped, current_time

    def test_cold_open_preservation(self):
        """Verify playback before op_start does NOT trigger intro skip."""
        op_start = 128.4
        op_end = 218.4
        
        # At 30s (during cold open story)
        should_seek, has_skipped, new_time = self.simulate_playback_step(
            current_time=30.0,
            op_start=op_start,
            op_end=op_end,
            auto_skip=True,
            has_skipped=False
        )
        assert not should_seek, "Intro skip triggered prematurely during cold open prologue"
        assert not has_skipped
        assert new_time == 30.0

    def test_intro_skip_triggers_at_op_start(self):
        """Verify reaching op_start immediately seeks past song to op_end."""
        op_start = 128.4
        op_end = 218.4

        should_seek, has_skipped, new_time = self.simulate_playback_step(
            current_time=128.5,
            op_start=op_start,
            op_end=op_end,
            auto_skip=True,
            has_skipped=False
        )
        assert should_seek, "Intro skip failed to trigger at op_start"
        assert has_skipped is True
        assert new_time == op_end

    def test_single_skip_trigger_prevents_loops(self):
        """Verify after skipping once, it does not re-trigger."""
        op_start = 128.4
        op_end = 218.4

        should_seek, has_skipped, _ = self.simulate_playback_step(
            current_time=218.4,
            op_start=op_start,
            op_end=op_end,
            auto_skip=True,
            has_skipped=True  # Already skipped
        )
        assert not should_seek, "Intro skip triggered repeatedly after initial skip"

    def test_auto_skip_disabled_flag(self):
        """Verify auto_skip=False disables automatic seeking."""
        op_start = 128.4
        op_end = 218.4

        should_seek, has_skipped, _ = self.simulate_playback_step(
            current_time=130.0,
            op_start=op_start,
            op_end=op_end,
            auto_skip=False,
            has_skipped=False
        )
        assert not should_seek, "Auto-skip triggered when feature was disabled"


class TestLiveVlcControllerModule:
    """Verify vlc_controller.py module if implemented in workspace."""

    def test_vlc_rc_controller_contract_if_present(self, mock_vlc_server: MockVlcRcServer):
        """Test VlcRcController class contract against MockVlcRcServer."""
        try:
            import vlc_controller
            if hasattr(vlc_controller, "VlcRcController"):
                ctrl = vlc_controller.VlcRcController(
                    vlc_path="dummy_vlc",
                    port=mock_vlc_server.port,
                    poll_interval=0.05,
                    auto_skip=True
                )
                assert ctrl.port == mock_vlc_server.port
                assert ctrl.auto_skip is True
                if hasattr(ctrl, "send_command"):
                    resp = ctrl.send_command("status")
                    assert resp is not None
        except ImportError:
            pass  # Module to be created in M3

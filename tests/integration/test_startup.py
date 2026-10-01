"""Integration tests: process lifecycle via `python -m ranger_map`.

Covers the clean-start README path, restart persistence, and the two refusal
cases the design demands: a second server process on the same data root, and
an occupied port.
"""

from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable


def http_get(url: str, timeout: float = 3.0):
    """Blocking-socket HTTP GET.

    urllib is used deliberately: in sandboxed CI shells an intercepting
    proxy can garble httpx's real-socket transport on loopback, while
    plain blocking sockets (like curl) behave. The server under test is
    identical either way.
    """
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def start_server(port: int, data_dir: Path, env_extra: dict | None = None):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    if env_extra:
        env.update(env_extra)
    process = subprocess.Popen(
        [
            PYTHON, "-m", "ranger_map",
            "--host", "127.0.0.1", "--port", str(port),
            "--data-dir", str(data_dir),
        ],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return process


def wait_healthy(port: int, timeout: float = 15.0, process=None):
    deadline = time.monotonic() + timeout
    last_error = None
    while time.monotonic() < deadline:
        try:
            status, body = http_get(f"http://127.0.0.1:{port}/healthz", timeout=2.0)
            if status == 200:
                return body
        except Exception as exc:  # noqa: BLE001 - startup polling
            last_error = exc
        if process is not None and process.poll() is not None:
            output = process.stdout.read() if process.stdout else ""
            raise AssertionError(
                f"server exited rc={process.returncode}: {output[:500]}")
        time.sleep(0.2)
    detail = f"{last_error}"
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:  # pragma: no cover
            process.kill()
        output = process.stdout.read() if process.stdout else ""
        detail += f"; still-alive process output: {output[:600]!r}"
    raise AssertionError(f"server did not become healthy: {detail}")


def stop_server(process):
    # Let short-lived refusal processes finish on their own first, so their
    # diagnostics reach the pipe before any signal races them.
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        pass
    if process.poll() is None:
        process.send_signal(signal.SIGINT)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:  # pragma: no cover - defensive
            process.kill()
            process.wait(timeout=10)
    return process.stdout.read() if process.stdout else ""


def test_clean_start_empty_state_and_restart(tmp_path):
    port = free_port()
    data_dir = tmp_path / "fresh"

    process = start_server(port, data_dir)
    try:
        health = wait_healthy(port, process=process)
        assert health["status"] == "ok"

        # Real empty state: 0 rangers, 0 footprints, honest page.
        status, body = http_get(f"http://127.0.0.1:{port}/ranger-map/v1/map")
        assert status == 200
        assert body["ranger_count"] == 0
        assert body["footprint_count"] == 0
        assert body["items"] == []
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=3.0) as page:
            assert page.status == 200
            html = page.read().decode("utf-8")
        assert "Be the first ranger" in html  # static empty-state copy

        # The native adapter is bound: unsigned garbage is a defined 400,
        # and the manifest is served with a signed proof header.
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}/v1/push", data=b"x", method="POST"
        )
        try:
            urllib.request.urlopen(request, timeout=3.0)
            raise AssertionError("unsigned push should be rejected")
        except urllib.error.HTTPError as exc:
            assert exc.code == 400
            assert b"MALFORMED_WRAPPER" in exc.read()
        with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/v1/manifest", timeout=3.0) as manifest:
            assert manifest.status == 200
            assert manifest.headers.get("X-Popclaw-Manifest-Proof")
    finally:
        output = stop_server(process)
    assert "Map page" in output

    # Seed through the internal trusted path while the server is down
    # (domain-test pattern; never an HTTP write).
    from ranger_map.check_in import TrustedCheckInContext, apply_check_in
    from ranger_map.store import Store
    from tests.conftest import valid_params_bytes

    store = Store.open(data_dir)
    apply_check_in(
        store,
        TrustedCheckInContext("ArangerA1111111111111111111111111", "Yun", "01" * 32),
        valid_params_bytes(place="Hangzhou"),
    )
    store.close()

    # Restart on the SAME origin (the data root is pinned to it; a different
    # origin is refused by design).
    process2 = start_server(port, data_dir)
    try:
        wait_healthy(port, process=process2)
        status, body = http_get(f"http://127.0.0.1:{port}/ranger-map/v1/map")
        assert status == 200
        assert body["ranger_count"] == 1
        assert body["footprint_count"] == 1
        assert body["items"][0]["place"] == "Hangzhou"
        with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/v1/manifest", timeout=3.0) as manifest:
            # Manifest stays pinned across restarts (same capability revision).
            assert manifest.status == 200
            assert manifest.headers.get("X-Popclaw-Manifest-Proof")
    finally:
        stop_server(process2)


def test_second_process_same_data_root_refused(tmp_path):
    port = free_port()
    process = start_server(port, tmp_path / "d")
    try:
        wait_healthy(port)
        port2 = free_port()
        second = start_server(port2, tmp_path / "d")
        output = stop_server(second)
        assert second.returncode != 0
        assert "already using this data directory" in output
    finally:
        stop_server(process)


def test_occupied_port_refused_cleanly(tmp_path):
    blocker = socket.socket()
    blocker.bind(("127.0.0.1", 0))
    blocker.listen(1)
    port = blocker.getsockname()[1]
    try:
        process = start_server(port, tmp_path / "d")
        output = stop_server(process)
        assert process.returncode != 0
        assert "cannot bind" in output
        assert "does not silently switch ports" in output
    finally:
        blocker.close()

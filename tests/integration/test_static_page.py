"""Integration tests: the static comic map page and its assets."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ranger_map.app import create_app  # noqa: E402
from ranger_map.store import Store  # noqa: E402

STATIC = Path(__file__).resolve().parents[2] / "src" / "ranger_map" / "static"


@pytest.fixture()
def client(tmp_path):
    from starlette.testclient import TestClient

    store = Store.open(tmp_path / "data")
    app = create_app(store)
    return TestClient(app)


def test_homepage_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "PopClaw Ranger Map" in response.text
    assert "Every ranger leaves a trace." in response.text


def test_homepage_has_csp_and_no_inline_handlers(client):
    response = client.get("/")
    assert "Content-Security-Policy" in response.text
    assert "default-src 'self'" in response.text
    # No inline event handlers or javascript: URLs.
    assert not re.search(r"\son[a-z]+\s*=", response.text)
    assert "javascript:" not in response.text


def test_static_assets_resolve(client):
    for path in [
        "/static/style.css",
        "/static/app.js",
        "/static/assets/world-land.svg",
        "/static/assets/world-land-dark.svg",
        "/static/assets/brand/popclaw-large-wordmark-positive@2x.png",
        "/static/assets/brand/popclaw-large-wordmark-reverse@2x.png",
    ]:
        response = client.get(path)
        assert response.status_code == 200, path


def test_no_external_resource_requests():
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    js = (STATIC / "app.js").read_text(encoding="utf-8")
    css = (STATIC / "style.css").read_text(encoding="utf-8")
    for name, text in (("index.html", html), ("app.js", js), ("style.css", css)):
        # Any http(s) URL in our own assets would mean an external request.
        assert not re.search(r"https?://(?!www\.w3\.org)", text), name
    # The only namespace reference is the SVG schema declaration.
    assert "http://www.w3.org/2000/svg" in js


def test_land_svg_carries_provenance():
    svg = (STATIC / "assets" / "world-land.svg").read_text(encoding="utf-8")
    assert "natural-earth-vector" in svg
    assert "v5.1.2" in svg
    assert svg.count("<svg") == 1
    dark = (STATIC / "assets" / "world-land-dark.svg").read_text(encoding="utf-8")
    assert "natural-earth-vector" in dark


def test_status_text_rendered_as_text(client, tmp_path):
    # Marker text is rendered by app.js via textContent; the page itself must
    # not embed any server data at all (the only place names in the HTML are
    # the static example-city coordinates in the help drawer).
    response = client.get("/")
    assert "as_of_seq" not in response.text
    assert '"items"' not in response.text
    assert "<script>\n" not in response.text  # JS lives in its own file

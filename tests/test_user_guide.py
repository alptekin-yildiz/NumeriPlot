"""Check offline guide integrity and reproducibility of the shipped pages."""
import json
import runpy
import shutil
import struct
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "guide"


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids = []
        self.links = []
        self.assets = []
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])
        if tag in ("img", "script") and attrs.get("src"):
            self.assets.append(attrs["src"])
        if tag == "link" and attrs.get("href"):
            self.assets.append(attrs["href"])


@pytest.mark.parametrize("filename", ["index.html", "en.html"])
def test_offline_links_and_assets(filename):
    page = Page(GUIDE / filename)
    assert len(page.ids) == len(set(page.ids)), "Duplicate anchor"
    for asset in page.assets:
        assert not urlsplit(asset).scheme, "External runtime dependency"
        assert (GUIDE / asset).is_file()
    for link in page.links:
        parsed = urlsplit(link)
        if parsed.scheme:
            continue
        target = (GUIDE / unquote(parsed.path)) if parsed.path else GUIDE / filename
        assert target.is_file(), link
        if parsed.fragment:
            assert unquote(parsed.fragment) in Page(target).ids, link
    for source in ("essentials.json", "workflows.json", "settings.json"):
        for section in json.loads((GUIDE / source).read_text()):
            assert section["id"] in page.ids


def test_screenshot_pairs_match_manifest():
    manifest = json.loads((GUIDE / "assets/manifest.json").read_text())
    referenced = set()
    for capture in manifest.values():
        assert set(capture) == {"tr", "en"}
        for image in capture.values():
            path = GUIDE / image["src"]
            data = path.read_bytes()
            assert data[:8] == b"\x89PNG\r\n\x1a\n"
            assert struct.unpack(">II", data[16:24]) == (image["width"], image["height"])
            referenced.add(path)
    assert referenced == set((GUIDE / "assets").glob("*.png"))


def test_generated_pages_are_current(tmp_path):
    namespace = runpy.run_path(str(ROOT / "examples/build_guide.py"))
    shutil.copytree(GUIDE / "assets", tmp_path / "assets")
    for source in ("essentials.json", "workflows.json", "settings.json", "assets/manifest.json"):
        target = tmp_path / source
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((GUIDE / source).read_bytes())
    build = namespace["build"]
    build.__globals__["GUIDE"] = tmp_path
    build()
    for filename in ("index.html", "en.html"):
        assert (tmp_path / filename).read_bytes() == (GUIDE / filename).read_bytes()

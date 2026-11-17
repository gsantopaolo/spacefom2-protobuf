"""Tests for render_pdf.py's pure logic; pandoc, Chrome and rsvg-convert are not run."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import render_pdf  # noqa: E402
from render_pdf import GITHUB, find_chrome, prepare  # noqa: E402


@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.setattr(render_pdf, "REPO", tmp_path)
    (tmp_path / "proposal").mkdir()
    (tmp_path / "docs" / "images").mkdir(parents=True)
    return tmp_path


def write(repo, text):
    source = repo / "proposal" / "pitch.md"
    source.write_text(text, encoding="utf-8")
    return source


def test_relative_links_become_github_urls(repo):
    source = write(repo, "[a](open-questions.md) [b](../docs/x.md#part) [c](../README.md)\n")
    assert prepare(source) == (
        f"[a]({GITHUB}proposal/open-questions.md) [b]({GITHUB}docs/x.md#part) "
        f"[c]({GITHUB}README.md)\n"
    )


@pytest.mark.parametrize(
    "link", ["[w](https://example.org/a.md)", "[w](http://x.org)", "[m](mailto:a@b.c)",
             "[s](#section)", "[r](/abs/path.md)"]
)
def test_other_links_are_left_alone(repo, link):
    assert prepare(write(repo, link)) == link


def test_centred_html_image_becomes_markdown_image(repo):
    html = '<p align="center"><img src="../docs/images/arch.svg" alt="Arch" width="600"></p>\n'
    source = write(repo, html)
    path = repo / "docs" / "images" / "arch.svg"
    assert prepare(source) == f"![Arch]({path}){{width=66%}}\n"


def test_svg_is_rasterised_for_word(repo, tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(render_pdf.subprocess, "run", lambda cmd, check: calls.append(cmd))
    source = write(repo, '<p align="center"><img src="../docs/images/arch.svg" alt="Arch"></p>')
    raster = tmp_path / "raster"
    assert prepare(source, raster) == f"![Arch]({raster / 'arch.png'}){{width=66%}}"
    svg = repo / "docs" / "images" / "arch.svg"
    assert calls == [["rsvg-convert", "--zoom=2", "--output", str(raster / "arch.png"), str(svg)]]


def test_chrome_from_env(tmp_path):
    chrome = tmp_path / "chrome"
    chrome.write_text("")
    chrome.chmod(0o755)
    assert find_chrome({"CHROME": str(chrome)}, which=lambda _: "/usr/bin/other") == str(chrome)


def test_chrome_from_env_must_be_executable(tmp_path):
    with pytest.raises(SystemExit, match="is not an executable file"):
        find_chrome({"CHROME": str(tmp_path / "missing")})


def test_chrome_on_path():
    found = {"chromium": "/usr/bin/chromium", "chrome": "/usr/bin/chrome"}
    assert find_chrome({}, which=found.get) == "/usr/bin/chromium"


def test_chrome_macos_default(tmp_path):
    mac = tmp_path / "Google Chrome"
    mac.write_text("")
    assert find_chrome({}, which=lambda _: None, macos_chrome=str(mac)) == str(mac)


def test_no_chrome_fails_loudly(tmp_path):
    with pytest.raises(SystemExit, match="Chrome not found. Set CHROME"):
        find_chrome({}, which=lambda _: None, macos_chrome=str(tmp_path / "none"))

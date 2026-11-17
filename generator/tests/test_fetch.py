"""fetch.py without the network: urlopen is replaced by a stub serving bytes."""

import hashlib
import io

import pytest

from spacefom_proto import fetch as fetch_module
from spacefom_proto.fetch import fetch, raw_url
from spacefom_proto.model import GeneratorError

DATA = b"<objectModel/>"
NAME = "SISO_SpaceFOM_datatypes.xml"


def source(name=NAME, sha256=hashlib.sha256(DATA).hexdigest()):
    return {
        "repository": "https://github.com/nasa/TrickHLA",
        "commit": "abc123",
        "path": "FOMs/SpaceFOM",
        "files": [{"name": name, "sha256": sha256}],
    }


@pytest.fixture
def served(monkeypatch):
    urls = []

    def urlopen(url, timeout):
        urls.append(url)
        return io.BytesIO(DATA)

    monkeypatch.setattr(fetch_module.urllib.request, "urlopen", urlopen)
    return urls


def test_raw_url():
    assert raw_url(source(), NAME) == (
        "https://raw.githubusercontent.com/nasa/TrickHLA/abc123/FOMs/SpaceFOM/" + NAME
    )


def test_fetch_writes_verified_files(tmp_path, served):
    dest = tmp_path / "fom"
    assert fetch(source(), dest) == [dest / NAME]
    assert (dest / NAME).read_bytes() == DATA
    assert served == [raw_url(source(), NAME)]


def test_sha256_mismatch_fails_and_writes_nothing(tmp_path, served):
    dest = tmp_path / "fom"
    with pytest.raises(GeneratorError, match="does not match " + "0" * 64):
        fetch(source(sha256="0" * 64), dest)
    assert not (dest / NAME).exists()


@pytest.mark.parametrize(
    "name", ["../SISO_SpaceFOM_x.xml", "sub/SISO_SpaceFOM_x.xml", "/etc/passwd", "..", "other.xml"]
)
def test_unexpected_name_fails_before_download(tmp_path, served, name):
    dest = tmp_path / "fom"
    with pytest.raises(GeneratorError, match="unexpected FOM module file name"):
        fetch(source(name=name), dest)
    assert served == [] and not dest.exists()


def test_a_bad_name_later_in_the_list_stops_every_download(tmp_path, served):
    src = source()
    src["files"].append({"name": "../evil.xml", "sha256": "0" * 64})
    with pytest.raises(GeneratorError, match="unexpected FOM module file name: ../evil.xml"):
        fetch(src, tmp_path / "fom")
    assert served == []

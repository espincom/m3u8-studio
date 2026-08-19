import os
import re
import struct
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse, unquote
import requests
from .config import DEFAULT_UA


@dataclass
class Variant:
    url: str
    bandwidth: int = 0
    resolution: str = ""
    codecs: str = ""

    def height(self) -> int:
        if "x" in self.resolution:
            try:
                return int(self.resolution.split("x")[1])
            except ValueError:
                return 0
        return 0

    def label(self) -> str:
        parts = []
        if self.resolution:
            h = self.height()
            parts.append("%dp" % h if h else self.resolution)
        if self.bandwidth:
            parts.append("%.1f Mbps" % (self.bandwidth / 1_000_000))
        return " · ".join(parts) or "akis"


@dataclass
class Segment:
    url: str
    index: int
    duration: float = 0.0
    key_uri: str = ""
    key_iv: bytes = b""
    key_method: str = "NONE"
    byte_range: tuple = None


@dataclass
class Media:
    segments: list = field(default_factory=list)
    init_url: str = ""
    total_duration: float = 0.0
    is_fmp4: bool = False


def _attrs(line: str) -> dict:
    out = {}
    for m in re.finditer(r'([A-Z0-9\-]+)=("[^"]*"|[^,]*)', line):
        out[m.group(1)] = m.group(2).strip('"')
    return out


def parse_master(text: str, base_url: str) -> list:
    variants = []
    lines = [l.strip() for l in text.splitlines()]
    for i, line in enumerate(lines):
        if not line.startswith("#EXT-X-STREAM-INF"):
            continue
        a = _attrs(line)
        for nxt in lines[i + 1:]:
            if nxt and not nxt.startswith("#"):
                variants.append(Variant(
                    url=urljoin(base_url, nxt),
                    bandwidth=int(a.get("BANDWIDTH") or a.get("AVERAGE-BANDWIDTH") or 0),
                    resolution=a.get("RESOLUTION", ""),
                    codecs=a.get("CODECS", ""),
                ))
                break
    variants.sort(key=lambda v: (v.height(), v.bandwidth), reverse=True)
    return variants


def parse_media(text: str, base_url: str) -> Media:
    media = Media()
    key_uri, key_iv, key_method = "", b"", "NONE"
    seq, duration, byte_range, next_offset = 0, 0.0, None, 0

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#EXT-X-MEDIA-SEQUENCE"):
            try:
                seq = int(line.split(":", 1)[1].strip())
            except (ValueError, IndexError):
                seq = 0
        elif line.startswith("#EXT-X-KEY"):
            a = _attrs(line)
            key_method = a.get("METHOD", "NONE")
            key_uri = urljoin(base_url, a["URI"]) if a.get("URI") else ""
            iv = a.get("IV", "")
            key_iv = bytes.fromhex(iv[2:]) if iv.lower().startswith("0x") else b""
        elif line.startswith("#EXT-X-MAP"):
            a = _attrs(line)
            if a.get("URI"):
                media.init_url = urljoin(base_url, a["URI"])
                media.is_fmp4 = True
        elif line.startswith("#EXTINF"):
            try:
                duration = float(line.split(":", 1)[1].split(",")[0])
            except (ValueError, IndexError):
                duration = 0.0
        elif line.startswith("#EXT-X-BYTERANGE"):
            val = line.split(":", 1)[1].strip()
            if "@" in val:
                length, offset = val.split("@")
                byte_range = (int(length), int(offset))
            else:
                byte_range = (int(val), next_offset)
            next_offset = byte_range[1] + byte_range[0]
        elif not line.startswith("#"):
            idx = seq + len(media.segments)
            media.segments.append(Segment(
                url=urljoin(base_url, line),
                index=idx,
                duration=duration,
                key_uri=key_uri,
                key_iv=key_iv or struct.pack(">QQ", 0, idx),
                key_method=key_method,
                byte_range=byte_range,
            ))
            media.total_duration += duration
            duration, byte_range = 0.0, None
    return media


def make_session(headers: dict, pool=10) -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": DEFAULT_UA, "Accept": "*/*"})
    s.headers.update({k: v for k, v in (headers or {}).items() if v})
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=max(pool, 10), pool_maxsize=max(pool, 10))
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s


def suggest_name(url: str) -> str:
    path = unquote(urlparse(url).path)
    parts = [p for p in path.split("/") if p]
    base = ""
    if parts:
        stem = os.path.splitext(parts[-1])[0]
        if stem.lower() in ("index", "playlist", "master", "video", "stream", "hls", "chunklist"):
            base = parts[-2] if len(parts) > 1 else stem
        else:
            base = stem
    base = re.sub(r'[<>:"/\\|?*]+', "_", base).strip(" ._") or "video"
    return base[:80] + ".mp4"


def unique_path(path: str) -> str:
    if not os.path.exists(path):
        return path
    stem, ext = os.path.splitext(path)
    i = 2
    while os.path.exists("%s (%d)%s" % (stem, i, ext)):
        i += 1
    return "%s (%d)%s" % (stem, i, ext)

"""Generate simple PWA icons. Run: python scripts/generate_icons.py"""
import struct
import zlib
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "static" / "icons"
OUT.mkdir(parents=True, exist_ok=True)


def png(s, w, h, r, g, b):
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b""
    for y in range(h):
        raw += b"\x00"
        for x in range(w):
            cx, cy = w / 2, h / 2
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if dist < min(w, h) * 0.42:
                raw += bytes([r, g, b])
            else:
                raw += bytes([13, 17, 23])
    comp = zlib.compress(raw, 9)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", comp) + chunk(b"IEND", b"")


for size, name in [(192, "icon-192.png"), (512, "icon-512.png")]:
    (OUT / name).write_bytes(png(name, size, size, 46, 160, 67))

print("Icons written to", OUT)

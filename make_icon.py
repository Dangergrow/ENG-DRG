"""Генератор иконки — книга + флаг UK, glassmorphism стиль."""
import struct, zlib, math

def hex_to_rgb(h):
    return (h >> 16) & 255, (h >> 8) & 255, h & 255

def make_png(size, as_icon=False):
    raw = b''
    cx, cy = size / 2, size / 2
    r = size * 0.44

    for y in range(size):
        raw += b'\x00'
        for x in range(size):
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx*dx + dy*dy)

            if dist < r:
                t = dist / r
                # Deep navy blue gradient
                rr = int(15 + 25 * t)
                gg = int(20 + 35 * t)
                bb = int(60 + 40 * t)

                # Union Jack flag (stylized)
                # Diagonal red cross
                d1 = abs(dx - dy) / math.sqrt(2)
                d2 = abs(dx + dy) / math.sqrt(2)
                is_red = d1 < size * 0.04 or d2 < size * 0.04
                # White edges on cross
                is_white = d1 < size * 0.07 or d2 < size * 0.07

                # Horizontal + vertical white cross
                is_hv_white = abs(dx) < size * 0.07 or abs(dy) < size * 0.07
                is_hv_red = abs(dx) < size * 0.04 or abs(dy) < size * 0.04

                if is_white and not is_red:
                    rr, gg, bb = 255, 255, 255
                elif is_red or is_hv_red:
                    rr, gg, bb = 220, 30, 50  # Red
                elif is_hv_white:
                    rr, gg, bb = 255, 255, 255

                raw += bytes([rr, gg, bb, 255])
            else:
                raw += bytes([0, 0, 0, 0])

    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')

# PNG for GitHub (512x512)
png = make_png(512)
with open('app.png', 'wb') as f:
    f.write(png)

# ICO for .exe (multi-res)
sizes = [256, 48, 32, 16]
entries = b''
pngs = []
offset = 6 + 16 * len(sizes)
for sz in sizes:
    p = make_png(sz, as_icon=True)
    pngs.append(p)
    w = sz if sz < 256 else 0
    h = sz if sz < 256 else 0
    entries += struct.pack('<BBBBHHII', w, h, 0, 0, 1, 32, len(p), offset)
    offset += len(p)

ico = struct.pack('<HHH', 0, 1, len(sizes)) + entries
for p in pngs:
    ico += p

with open('app.ico', 'wb') as f:
    f.write(ico)

import os
print(f'OK: app.png ({os.path.getsize("app.png")} bytes)')
print(f'OK: app.ico ({os.path.getsize("app.ico")} bytes, 4 sizes)')

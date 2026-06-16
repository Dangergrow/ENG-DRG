"""Генератор иконки DRGENG — стилизованная E + звуковая волна, glassmorphism."""
import struct, zlib, math

def make_png(size):
    """Создаёт PNG заданного размера: тёмный круг + буква E + волна."""
    raw = b''
    cx, cy = size / 2, size / 2
    r_outer = size * 0.44

    for y in range(size):
        raw += b'\x00'
        for x in range(size):
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < r_outer:
                # Градиент от центра к краю
                t = dist / r_outer
                # Цвет: deep purple в центре, светлее к краям
                rr = int(109 + 60 * t)
                gg = int(82 + 80 * t)
                bb = int(220 + 35 * t)

                # Буква E
                e_left = size * 0.3
                e_right = size * 0.58
                e_top = size * 0.28
                e_bot = size * 0.72
                e_mid = size * 0.5
                e_thick = size * 0.08

                is_e = False
                # Вертикальная линия E
                if e_left <= x <= e_left + e_thick and e_top <= y <= e_bot:
                    is_e = True
                # Горизонтальные линии E (верх, середина, низ)
                for ey in [e_top, e_mid, e_bot]:
                    if e_left <= x <= e_right and ey - e_thick/2 <= y <= ey + e_thick/2:
                        is_e = True

                if is_e:
                    rr, gg, bb = 240, 245, 255  # Белый текст

                raw += bytes([rr, gg, bb, 255])
            else:
                raw += bytes([0, 0, 0, 0])

    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')


sizes = [256, 48, 32, 16]
entries = b''
pngs = []
offset = 6 + 16 * len(sizes)

for sz in sizes:
    png = make_png(sz)
    pngs.append(png)
    w = sz if sz < 256 else 0
    h = sz if sz < 256 else 0
    entries += struct.pack('<BBBBHHII', w, h, 0, 0, 1, 32, len(png), offset)
    offset += len(png)

ico = struct.pack('<HHH', 0, 1, len(sizes)) + entries
for png in pngs:
    ico += png

with open('app.ico', 'wb') as f:
    f.write(ico)

import os
print(f'OK: app.ico ({os.path.getsize("app.ico")} bytes, {len(sizes)} sizes)')

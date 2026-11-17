# 파티클용 텍스처 생성 (Blender 불필요, 순수 Python) — AI-Assist: generated
# 실행 (프로젝트 루트에서):  python Tools/AssetGen/make_fx_textures.py
# 결과: Assets/_Project/Art/Textures/T_FX_*.png  (128px, 흰색 + 알파)
#
# 색은 전부 흰색이고 모양은 알파에만 들어 있다. 실제 색은 Unity 파티클의 Start Color로 입힌다.
import math
import os
import struct
import zlib

SIZE = 128
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "Assets", "_Project", "Art", "Textures")


def smooth(edge0, edge1, x):
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3 - 2 * t)


def droplet(x, y):
    """물방울: 가장자리가 부드러운 원 + 가운데가 살짝 비쳐 보이게."""
    r = math.hypot(x, y)
    disc = 1.0 - smooth(0.62, 0.95, r)
    hollow = 0.75 + 0.25 * smooth(0.15, 0.7, r)      # 테두리가 더 진한 물방울 느낌
    return disc * hollow


def sparkle(x, y):
    """반짝이: 십자 모양 빛줄기 + 가운데 빛망울."""
    r = math.hypot(x, y)
    ax, ay = abs(x), abs(y)
    ray = max(math.exp(-ay * 26) * (1 - ax), math.exp(-ax * 26) * (1 - ay))
    ray = max(0.0, ray) ** 1.2
    glow = math.exp(-r * r * 22)
    return min(1.0, ray + glow) * (1.0 - smooth(0.85, 1.0, r))


def ring(x, y):
    """터지는 순간 퍼지는 고리."""
    r = math.hypot(x, y)
    return math.exp(-((r - 0.78) / 0.085) ** 2)


def shred(x, y):
    """풍선 조각: 들쭉날쭉한 고무 조각."""
    r = math.hypot(x, y)
    a = math.atan2(y, x)
    edge = 0.62 + 0.16 * math.sin(a * 3 + 0.7) + 0.09 * math.sin(a * 7 + 2.1)
    return 1.0 - smooth(edge - 0.06, edge + 0.02, r)


def write_png(name, fn):
    rows = []
    for j in range(SIZE):
        row = bytearray([0])                          # PNG 필터 타입 0
        for i in range(SIZE):
            x = (i + 0.5) / SIZE * 2 - 1
            y = (j + 0.5) / SIZE * 2 - 1
            a = int(max(0.0, min(1.0, fn(x, y))) * 255 + 0.5)
            row += bytes((255, 255, 255, a))
        rows.append(bytes(row))

    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(b"".join(rows), 9))
    png += chunk(b"IEND", b"")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name + ".png"), "wb") as f:
        f.write(png)
    print(name + ".png")


if __name__ == "__main__":
    write_png("T_FX_Droplet", droplet)
    write_png("T_FX_Sparkle", sparkle)
    write_png("T_FX_Ring", ring)
    write_png("T_FX_Shred", shred)

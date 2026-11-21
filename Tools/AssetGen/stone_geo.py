"""새총 탄환 돌멩이 10종 형상 (결정 008 보완 3).

모두 피벗 = 중심, 긴 쪽 지름 약 3.5~5 cm. 구를 모양마다 다르게 변형하고, 낮은 주파수 굴곡을 더해 대칭을 깬다.
색은 공용 팔레트(M_Palette)를 쓰고, 면마다 얼룩 · 점 · 석영 줄무늬를 칠해 하나하나 개성이 보이게 한다.
"""
import math

from mathutils import Vector

import common as C

SIZE = 0.020     # 기본 반지름 (m)

# (파일 이름, 한글 이름, 형태, 바탕색, 얼룩색, 무늬)   무늬: none · speck(드문 점) · vein(석영 띠)
STONES = [
    ("01_Flat",     "물수제비 돌",   "flat",     "pebble_b",    "pebble_a",   "speck"),
    ("02_Egg",      "달걀 돌",       "egg",      "stone_white", "pebble_c",   "none"),
    ("03_Triangle", "세모 돌",       "triangle", "rock_a",      "rock_b",     "speck"),
    ("04_Long",     "길쭉한 돌",     "long",     "stone_dark",  "rock_b",     "none"),
    ("05_Bean",     "콩 모양 돌",    "bean",     "stone_red",   "bark",       "none"),
    ("06_Chunky",   "각진 돌",       "chunky",   "cliff",       "rock_a",     "speck"),
    ("07_Thumb",    "엄지 자국 돌",  "thumb",    "stone_green", "rock_moss",  "none"),
    ("08_Lumpy",    "울퉁불퉁 돌",   "lumpy",    "rock_b",      "pebble_b",   "speck"),
    ("09_Drop",     "물방울 돌",     "drop",     "pebble_c",    "sand",       "none"),
    ("10_Vein",     "줄무늬 돌",     "round",    "stone_dark",  "rock_b",     "vein"),
]


def _wobble(d, seed, amp):
    """낮은 주파수 굴곡: 사인 세 개를 곱하고 더해 매끈하지만 대칭이 아닌 표면을 만든다."""
    s = seed * 1.7
    n = (math.sin(2.3 * d.x + s) * math.sin(1.9 * d.y + 2 * s) * math.sin(2.6 * d.z + 3 * s)
         + 0.5 * math.sin(4.1 * d.x + 3.7 * d.y + s) * math.cos(3.3 * d.z + 2 * s))
    return 1 + amp * n


def _shape(kind, d, seed):
    if kind == "flat":
        p = Vector((d.x * 1.05, d.y * 0.95, d.z * 0.36))
    elif kind == "egg":
        k = 1 + 0.12 * d.z
        p = Vector((d.x * 0.78 * k, d.y * 0.74 * k, d.z * 1.0))
    elif kind == "triangle":                           # 위에서 보면 둥근 세모
        phi = math.atan2(d.y, d.x)
        r = 1 + 0.20 * math.cos(3 * phi)
        p = Vector((d.x * r, d.y * r, d.z * 0.52))
    elif kind == "long":
        p = Vector((d.x * 1.45, d.y * 0.60, d.z * 0.50))
    elif kind == "bean":                               # 길쭉한 몸을 휘게 해서 콩(강낭콩) 모양
        p = Vector((d.x * 1.2, d.y * 0.72, d.z * 0.62))
        p.y += 0.32 * (d.x ** 2) - 0.12
    elif kind == "chunky":                             # 둥근 육면체: 모서리가 살아 있는 깨진 돌
        e = 0.55
        p = Vector(tuple(math.copysign(abs(c) ** e, c) for c in d))
        p = Vector((p.x * 0.95, p.y * 0.85, p.z * 0.75)) * 0.85
    elif kind == "thumb":                              # 납작한 돌 윗면에 엄지로 누른 듯한 오목한 자국
        p = Vector((d.x * 1.1, d.y * 0.85, d.z * 0.42))
        if d.z > 0:
            p.z -= 0.16 * math.exp(-(d.x ** 2 + d.y ** 2) / 0.18) * d.z
    elif kind == "lumpy":
        p = Vector((d.x, d.y * 0.88, d.z * 0.75)) * _wobble(d, seed + 5, 0.22)
    elif kind == "drop":                               # 한쪽 끝이 좁아지는 물방울
        k = 0.30 + 0.70 * ((1 + d.x) / 2) ** 0.55
        p = Vector((d.x * 1.25, d.y * 0.82 * k, d.z * 0.65 * k))
    else:                                              # round
        p = Vector((d.x, d.y * 0.86, d.z * 0.70))
    return p * _wobble(d, seed, 0.06)


def _paint(pattern, base, mottle, c, seed):
    """면 중심 c(반지름 1 기준 좌표)로 색을 정한다."""
    if pattern == "vein" and abs(c.dot(Vector((0.25, 0.35, 0.9)).normalized()) - 0.08) < 0.07:
        return "stone_vein"                            # 돌을 가로지르는 흰 석영 띠 하나
    if pattern == "speck":
        h = math.sin(c.x * 127.1 + c.y * 311.7 + c.z * 74.7 + seed) * 43758.5453
        if h - math.floor(h) > 0.975:
            return "stone_speck"                       # 드문드문 어두운 점
    # 얼룩: 낮은 주파수 무늬가 높은 곳만 다른 색
    m = math.sin(2.7 * c.x + seed) + math.sin(3.1 * c.y - 2 * seed) + math.sin(2.3 * c.z + 4 * seed)
    return mottle if m > 1.1 else base


def build_stone(key):
    fname, _, kind, base, mottle, pattern = next(s for s in STONES if s[0] == key)
    seed = int(fname[:2])
    lat, lon = 40, 56                                  # 면 단위로 색을 칠하므로, 무늬 경계가 각지지 않게 촘촘히
    mb = C.MeshBuilder()
    rings, units = [], []
    for a in range(1, lat):
        th = math.pi * a / lat
        ring, uring = [], []
        for b in range(lon):
            ph = 2 * math.pi * b / lon
            d = Vector((math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)))
            p = _shape(kind, d, seed)
            ring.append(mb.v(p * SIZE))
            uring.append(p)
        rings.append(ring)
        units.append(uring)
    top_p, bot_p = _shape(kind, Vector((0, 0, 1)), seed), _shape(kind, Vector((0, 0, -1)), seed)
    top, bot = mb.v(top_p * SIZE), mb.v(bot_p * SIZE)

    def col(*pts):
        return _paint(pattern, base, mottle, sum(pts, Vector()) / len(pts), seed)

    for b in range(lon):
        c = (b + 1) % lon
        mb.f([top, rings[0][b], rings[0][c]], col(top_p, units[0][b], units[0][c]))
        mb.f([bot, rings[-1][c], rings[-1][b]], col(bot_p, units[-1][b], units[-1][c]))
        for a in range(lat - 2):
            mb.f([rings[a][b], rings[a + 1][b], rings[a + 1][c], rings[a][c]],
                 col(units[a][b], units[a + 1][b], units[a + 1][c], units[a][c]))
    return mb.build("Stone_" + fname, sharp_deg=80)

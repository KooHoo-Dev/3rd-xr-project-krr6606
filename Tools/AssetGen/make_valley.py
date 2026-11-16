"""야외 여름 계곡 환경 (Valley.fbx) — AI-Assist: generated

결정: docs/decisions/003 (Blender 스크립트로 생성, 초안 구성 그대로)
플레이어는 원점 근처 (0, 0, -0.25)에서 +Z를 바라본다. 던지는 선 = z 0.

구성 (Unity 좌표, m)
  Ground     자갈 강변(플레이어 주변은 y = 0으로 평평) → 앞쪽 시냇물 골 → 양옆 · 뒤 · 건너편 언덕
  Water      시냇물 수면 (y = WATER_Y), 플레이어 앞 약 2.5 ~ 6 m
  Rocks      강가 바위 · 시냇물 징검돌 · 언덕 바위 · 자갈
  Trees      건너편 비탈과 양옆 언덕의 나무
  Mountains  멀리 둘러싼 산 실루엣 (반지름 약 70 ~ 90 m)
하늘은 Unity Skybox를 쓴다. 모든 메시는 M_Palette 하나만 쓴다 (Draw Call 절약).
피벗 = 원점, Unity에서 (0, 0, 0)에 회전 없이 놓는다. Ground에만 MeshCollider를 붙인다.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

WATER_Y = -0.12
STREAM_HALF = 1.6          # 시냇물 골 반폭
X_RANGE = (-26.0, 26.0)
Z_RANGE = (-12.0, 32.0)
STEP = 0.75                # 지면 격자 간격

rng = random.Random(7)     # 같은 결과가 나오도록 시드 고정


# ===========================================================================
# 지형 높이 함수 (Unity 좌표)
# ===========================================================================
def stream_center(x):
    return 4.0 + 0.45 * math.sin(0.22 * x + 0.7)


def smoothstep(e0, e1, v):
    t = min(1.0, max(0.0, (v - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def height(x, z):
    side = max(0.0, abs(x) - 3.5)          # 양옆 언덕
    far = max(0.0, z - 6.5)                # 건너편 비탈
    back = max(0.0, -2.5 - z)              # 뒤쪽 비탈
    h = 0.32 * side ** 1.28 + 0.40 * far ** 1.2 + 0.45 * back ** 1.2
    rough = min(1.0, (side + far + back) / 4.0)
    amp = 0.015 + 0.30 * rough
    h += amp * (math.sin(1.3 * x + 0.4) * math.sin(1.1 * z + 1.3) + 0.5 * math.sin(2.9 * x + 1.7 * z))

    # 시냇물 골: 가운데는 깊고 옆으로 갈수록 V자로 올라간다. 양 끝(|x| 11 ~ 15)에서 골이 사라짐
    d = abs(z - stream_center(x))
    if d < STREAM_HALF:
        carved = -0.32 + 0.30 * (d / STREAM_HALF) ** 2
    else:
        e = d - STREAM_HALF
        carved = -0.02 + 0.9 * e + 1.2 * max(0.0, e - 1.5) ** 2
    w = 1.0 - smoothstep(11.0, 15.0, abs(x))
    h = h * (1 - w) + min(h, carved) * w

    # 플레이어가 서는 곳은 정확히 평평하게 (XR Origin 바닥 = 0)
    if abs(x) < 1.6 and -1.6 < z < 1.4:
        h = 0.0
    return h


def zone_color(x, z, h, up):
    """면 하나의 색 (팔레트 이름)."""
    d = abs(z - stream_center(x))
    if h < WATER_Y + 0.02:
        return "riverbed"
    if up < 0.55:                          # 가파른 곳만 바위 절벽
        return rng.choice(("cliff", "rock_b"))
    if up < 0.75:                          # 중간 비탈: 풀 사이로 이끼 바위
        return rng.choices(("grass_b", "rock_moss", "grass_a"), (4, 2, 3))[0]
    if d < STREAM_HALF + 0.9 and abs(x) < 13:
        return rng.choice(("sand", "pebble_b", "sand"))
    rough = max(0.0, abs(x) - 3.5) + max(0.0, z - 6.5) + max(0.0, -2.5 - z)
    if rough < 0.8:
        return rng.choices(("pebble_a", "pebble_b", "pebble_c"), (5, 3, 2))[0]
    return rng.choices(("grass_a", "grass_b", "grass_c"), (5, 3, 2))[0]


# ===========================================================================
# 공용: 면 방향 맞추기
# ===========================================================================
def orient(obj, flip_if):
    """flip_if(face) 가 True인 면을 뒤집는다. 열린 메시(지면 · 수면 · 산)용."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for f in bm.faces:
        if flip_if(f):
            f.normal_flip()
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


# ===========================================================================
# 지면
# ===========================================================================
def build_ground():
    mb = C.MeshBuilder()
    nx = int((X_RANGE[1] - X_RANGE[0]) / STEP) + 1
    nz = int((Z_RANGE[1] - Z_RANGE[0]) / STEP) + 1
    grid = []
    pts = []
    for j in range(nz):
        row = []
        for i in range(nx):
            x = X_RANGE[0] + i * STEP
            z = Z_RANGE[0] + j * STEP
            if 0 < i < nx - 1 and 0 < j < nz - 1 and not (abs(x) < 2.0 and -2.0 < z < 1.8):
                x += rng.uniform(-0.25, 0.25) * STEP      # 격자 티가 덜 나게 살짝 흔듦
                z += rng.uniform(-0.25, 0.25) * STEP
            y = height(x, z)
            row.append(mb.v(C.U(x, y, z)))
            pts.append((x, y, z))
        grid.append(row)
    for j in range(nz - 1):
        for i in range(nx - 1):
            q = [grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]]
            # 면 색을 정하려고 Unity 좌표로 중심 · 기울기를 계산
            a = Vector(pts[j * nx + i]); b = Vector(pts[j * nx + i + 1])
            c = Vector(pts[(j + 1) * nx + i + 1]); d = Vector(pts[(j + 1) * nx + i])
            n = (c - a).cross(b - d)
            n = n.normalized() if n.length > 0 else Vector((0, 1, 0))
            up = abs(n.y)
            cx, cy, cz = (a + b + c + d) / 4
            # 사각형을 대각선으로 나눠 두 삼각형 → 각진 로우폴리 면. 삼각형마다 색을 따로 뽑아 자갈 · 풀 무늬를 낸다
            mb.f([q[0], q[1], q[2]], zone_color(cx, cz, cy, up))
            mb.f([q[0], q[2], q[3]], zone_color(cx, cz, cy, up))
    obj = mb.build("Ground", sharp_deg=1, recalc=False)
    orient(obj, lambda f: f.normal.z < 0)        # 모든 면이 위(Blender +Z)를 보게
    return obj


# ===========================================================================
# 수면
# ===========================================================================
def build_water():
    mb = C.MeshBuilder()
    xs = [-14.5 + k * 1.0 for k in range(30)]
    rows = []
    for x in xs:
        zc = stream_center(x)
        rows.append([mb.v(C.U(x, WATER_Y, zc + off)) for off in (-2.2, 0.0, 2.2)])
    for k in range(len(xs) - 1):
        for m in range(2):
            mb.f([rows[k][m], rows[k + 1][m], rows[k + 1][m + 1], rows[k][m + 1]], "water")
    obj = mb.build("Water", sharp_deg=1, recalc=False)
    orient(obj, lambda f: f.normal.z < 0)
    return obj


# ===========================================================================
# 바위 · 자갈
# ===========================================================================
def add_rock(mb, pos, size, mossy=False, subdiv=2):
    """찌그러뜨린 아이코스피어 하나. pos = Unity 좌표 바닥 중심, size = (가로, 높이, 세로)."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    rot = Matrix.Rotation(rng.uniform(0, math.tau), 3, "Z")
    sx, sy, sz = size
    base = len(mb.verts)
    for v in bm.verts:
        p = v.co * rng.uniform(0.82, 1.12)
        p = rot @ Vector((p.x * sx / 2, p.y * sz / 2, p.z * sy / 2))
        p.z = max(p.z, -sy * 0.35)                 # 아래쪽을 납작하게 (땅에 박힌 느낌)
        bx, by, bz = C.U(*pos)
        mb.v((bx + p.x, by + p.y, bz + p.z + sy * 0.25))
    tone = rng.choice(("rock_a", "rock_b"))
    for f in bm.faces:
        n = f.normal
        sw = "rock_moss" if (mossy and n.z > 0.6) else tone
        mb.f([base + v.index for v in f.verts], sw)
    bm.free()


def ground_pos(x, z):
    return (x, height(x, z), z)


def build_rocks():
    mb = C.MeshBuilder()
    # 플레이어 쪽 강가 바위 (풍선 아래 시야를 가리지 않게 낮게)
    for x, z, s in ((-3.2, 2.5, 0.7), (-2.0, 2.8, 0.45), (2.4, 2.6, 0.55), (3.6, 2.9, 0.8)):
        add_rock(mb, ground_pos(x, z), (s * 1.3, s * 0.7, s), mossy=True)
    # 시냇물 징검돌
    for x in (-1.2, 0.3, 1.7):
        z = stream_center(x) + rng.uniform(-0.5, 0.5)
        add_rock(mb, (x, -0.28, z), (0.45, 0.32, 0.4))
    # 건너편 강가
    for x in (-4.5, -1.8, 0.8, 3.0, 5.2):
        z = stream_center(x) + 2.0 + rng.uniform(0, 0.8)
        s = rng.uniform(0.5, 1.0)
        add_rock(mb, ground_pos(x, z), (s * 1.2, s * 0.8, s), mossy=True)
    # 시냇물이 사라지는 양 끝을 가리는 큰 바위
    for x, z, s in ((-11.5, 3.6, 3.2), (-13.0, 5.2, 2.6), (11.8, 4.4, 3.4), (13.2, 2.8, 2.4)):
        add_rock(mb, (x, height(x, z) - 0.4, z), (s * 1.3, s, s * 1.1), mossy=True)
    # 양옆 언덕 바위
    for _ in range(10):
        x = rng.choice((-1, 1)) * rng.uniform(5.0, 12.0)
        z = rng.uniform(-6.0, 12.0)
        s = rng.uniform(0.8, 2.2)
        add_rock(mb, (x, height(x, z) - 0.2, z), (s * 1.2, s * 0.8, s), mossy=True)
    # 발밑 자갈 (플레이어 · 받침대 자리는 비움)
    n = 0
    while n < 14:
        x, z = rng.uniform(-3.5, 3.5), rng.uniform(-2.5, 2.2)
        if (abs(x) < 1.1 and -1.2 < z < 1.0) or (abs(x - 0.55) < 0.45 and abs(z + 0.1) < 0.45):
            continue
        s = rng.uniform(0.06, 0.14)
        add_rock(mb, ground_pos(x, z), (s * 1.3, s * 0.6, s), subdiv=1)
        n += 1
    return mb.build("Rocks", sharp_deg=30)


# ===========================================================================
# 나무
# ===========================================================================
def add_conifer(mb, pos, hgt):
    """침엽수: 줄기 + 원뿔 3단."""
    x, y, z = pos
    C.lathe(mb, [(0, 0.0, "trunk"), (0, hgt * 0.035, "trunk"), (hgt * 0.3, hgt * 0.03, "trunk"),
                 (hgt * 0.3, 0.0, "trunk")], seg=6, axis="Z", c=C.U(x, y, z))
    leaf = rng.choice(("leaf_a", "leaf_b"))
    for k, (t0, t1, r) in enumerate(((0.22, 0.62, 0.30), (0.45, 0.82, 0.23), (0.66, 1.0, 0.16))):
        C.lathe(mb, [(hgt * t0, 0.0, leaf), (hgt * t0, hgt * r, leaf), (hgt * t1, 0.0, leaf)],
                seg=7, axis="Z", c=C.U(x, y, z), phase=k * 0.4)


def add_broadleaf(mb, pos, hgt):
    """활엽수: 줄기 + 찌그러진 구 3개로 된 잎 덩어리."""
    x, y, z = pos
    C.lathe(mb, [(0, 0.0, "trunk"), (0, hgt * 0.05, "trunk"), (hgt * 0.55, hgt * 0.035, "trunk"),
                 (hgt * 0.55, 0.0, "trunk")], seg=6, axis="Z", c=C.U(x, y, z))
    leaf = rng.choice(("leaf_a", "leaf_c"))
    for dx, dy, dz, r in ((0, 0.70, 0, 0.30), (0.18, 0.58, 0.08, 0.22), (-0.16, 0.60, -0.1, 0.24)):
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=hgt * r)
        base = len(mb.verts)
        cx, cy, cz = C.U(x + dx * hgt, y + dy * hgt, z + dz * hgt)
        for v in bm.verts:
            p = v.co * rng.uniform(0.85, 1.1)
            mb.v((cx + p.x, cy + p.y, cz + p.z * 0.85))
        for f in bm.faces:
            mb.f([base + v.index for v in f.verts], leaf)
        bm.free()


def build_trees():
    mb = C.MeshBuilder()
    spots = [(-6.0, 8.0), (-3.5, 9.5), (1.5, 10.0), (5.0, 8.5), (7.5, 6.5), (-8.0, 5.5),
             (9.0, 11.0), (-10.0, 10.0), (-5.0, -7.0), (6.0, -8.0)]
    # 건너편 비탈 숲
    for _ in range(18):
        spots.append((rng.uniform(-18, 18), rng.uniform(11, 24)))
    # 양옆 언덕
    for _ in range(8):
        spots.append((rng.choice((-1, 1)) * rng.uniform(8, 20), rng.uniform(-8, 8)))
    for x, z in spots:
        hgt = rng.uniform(4.0, 7.5)
        if rng.random() < 0.55:
            add_conifer(mb, ground_pos(x, z), hgt)
        else:
            add_broadleaf(mb, ground_pos(x, z), hgt * 0.8)
    return mb.build("Trees", sharp_deg=30)


# ===========================================================================
# 먼 산
# ===========================================================================
def build_mountains():
    mb = C.MeshBuilder()
    seg = 72
    peaks = [rng.uniform(16, 34) for _ in range(seg)]
    peaks = [(peaks[k - 1] + 2 * peaks[k] + peaks[(k + 1) % seg]) / 4 for k in range(seg)]  # 살짝 부드럽게
    bottom, mid, top = [], [], []
    for k in range(seg):
        a = math.tau * k / seg
        R = 72 + 10 * math.sin(3 * a + 1.0)
        ca, sa = math.cos(a), math.sin(a)
        h = peaks[k]
        bottom.append(mb.v(C.U(ca * R, -4.0, sa * R)))
        mid.append(mb.v(C.U(ca * (R + 6), h * 0.55, sa * (R + 6))))
        top.append(mb.v(C.U(ca * (R + 14), h, sa * (R + 14))))
    for k in range(seg):
        k2 = (k + 1) % seg
        mb.f([bottom[k], bottom[k2], mid[k2], mid[k]], "mountain_a")
        mb.f([mid[k], mid[k2], top[k2], top[k]], "mountain_b")
    obj = mb.build("Mountains", sharp_deg=1, recalc=False)
    # 안쪽(플레이어 쪽)을 보게: 면 법선이 원점에서 멀어지는 쪽이면 뒤집는다
    orient(obj, lambda f: f.normal.dot(f.calc_center_median().normalized()) > 0)
    return obj


def build_valley():
    root = bpy.data.objects.new("Valley", None)
    bpy.context.scene.collection.objects.link(root)
    parts = [build_ground(), build_water(), build_rocks(), build_trees(), build_mountains()]
    for p in parts:
        p.parent = root
    return root, parts


if __name__ == "__main__":
    C.reset()
    C.make_palette_textures()
    root, parts = build_valley()
    for p in parts:
        tris = sum(len(f.vertices) - 2 for f in p.data.polygons)
        print(f"[valley] {p.name}: tris={tris}")
    C.export_fbx(root, "Valley.fbx")

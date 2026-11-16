"""3단계: 게임 방 환경 + UI 스프라이트

만드는 것 (모두 Assets/_Project/Art/ 아래)
  Models/DartRoom.fbx        방 (바닥 판재, 웨인스코팅 벽, 몰딩, 천장 보, 뒤쪽 문)
  Models/BoardBackboard.fbx  다트판 뒤 나무판 + 검은 서라운드 링 (피벗 = 다트판 앞면 중심)
  Models/ScoreBoard.fbx      칠판 점수판 (피벗 = 칠판 면 중심, 앞면 -Z)
  Models/NeonSign_Title.fbx  "DART CHALLENGE" 네온 (피벗 = 뒷면 중심, 벽에 붙임)
  Models/NeonSign_777.fbx    "BULL 777" 네온
  Models/PendantLamp.fbx     펜던트 조명 (피벗 = 천장 고정점)
  Models/BarStool.fbx        바 의자
  Models/PosterFrame.fbx     다트 포스터 액자 (피벗 = 뒷면 중심)
  Models/OcheLine.fbx        던지는 선 (황동 띠)
  UI/UI_RoundedRect.png, UI/UI_Circle.png

모든 좌표는 Unity 기준(C.U / C.ubox)으로 적었다. 1 = 1 m, +Z = 다트판 방향.
"""
import math
import os
import random
import sys

import bmesh
import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

# 방 크기 (Unity 좌표)
X0, X1 = -2.0, 2.0
Z0, Z1 = -1.9, 2.1          # Z1 = 다트판 쪽 벽 안쪽 면
H = 3.0
T = 0.10                    # 벽 두께
DOOR = (0.8, 1.7, 2.1)      # 뒤쪽 벽 문: x0, x1, 높이


def join(name, objs):
    """여러 오브젝트를 하나의 메시로 합친다 (모두 M_Palette 사용)."""
    bm = bmesh.new()
    for o in objs:
        bm.from_mesh(o.data)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    C.finish_mesh(me)
    for o in objs:
        bpy.data.objects.remove(o)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(C.get_material("M_Palette"))
    return ob


# ===========================================================================
# 방
# ===========================================================================
def wall_elem(mb, wall, s0, s1, y0, y1, p, sw):
    axis, w, d = wall
    if axis == "z":       # 앞/뒤 벽: x 방향으로 뻗음
        C.ubox(mb, (s0, y0, w), (s1, y1, w + d * p), sw)
    else:                 # 옆 벽: z 방향으로 뻗음
        C.ubox(mb, (w, y0, s0), (w + d * p, y1, s1), sw)


def spans(wall_name, s0, s1, p):
    """벽 장식이 놓일 구간. 옆 벽은 양 끝을 p만큼 줄여 모서리에서 맞닿게, 앞 벽은 문 자리를 비운다."""
    if wall_name in ("left", "right"):
        return [(s0 + p, s1 - p)]
    if wall_name == "front":
        return [(s0, DOOR[0] - 0.08), (DOOR[1] + 0.08, s1)]
    return [(s0, s1)]


def build_room():
    rng = random.Random(3)
    mb = C.MeshBuilder()

    # --- 바닥 판재: 다트판 방향(z)으로 길게, 이음매를 엇갈리게 ---
    PW, GAP = 0.18, 0.004
    x = X0
    while x < X1 - 1e-6:
        x1 = min(x + PW, X1)
        z = Z0
        first = True
        while z < Z1 - 1e-6:
            L = rng.uniform(0.25, 1.3) if first else rng.uniform(0.9, 1.6)
            z1 = min(z + L, Z1)
            sw = rng.choice(["floor_a", "floor_b", "floor_c"])
            C.ubox(mb, (x + GAP / 2, -0.02, z + GAP / 2), (x1 - GAP / 2, 0.0, z1 - GAP / 2), sw)
            z, first = z1, False
        x = x1
    C.ubox(mb, (X0, -0.06, Z0), (X1, -0.012, Z1), "floor_gap")   # 틈 사이로 보이는 바닥 밑판

    # --- 벽 · 천장 (방 바깥쪽으로 두께) ---
    C.ubox(mb, (X0 - T, 0, Z1), (X1 + T, H, Z1 + T), "wall_paint")
    C.ubox(mb, (X0 - T, 0, Z0 - T), (X1 + T, H, Z0), "wall_paint")
    C.ubox(mb, (X0 - T, 0, Z0), (X0, H, Z1), "wall_paint")
    C.ubox(mb, (X1, 0, Z0), (X1 + T, H, Z1), "wall_paint")
    C.ubox(mb, (X0 - T, H, Z0 - T), (X1 + T, H + T, Z1 + T), "ceiling")
    for zc in (-1.0, 0.55, 1.95):                                   # 천장 보
        C.ubox(mb, (X0, H - 0.16, zc - 0.08), (X1, H, zc + 0.08), "wood_dark")

    # --- 벽 장식: 걸레받이, 웨인스코팅, 패널, 몰딩 ---
    walls = {
        "back":  (("z", Z1, -1), X0, X1),
        "front": (("z", Z0, +1), X0, X1),
        "left":  (("x", X0, +1), Z0, Z1),
        "right": (("x", X1, -1), Z0, Z1),
    }
    for name, (wall, s0, s1) in walls.items():
        for a, b in spans(name, s0, s1, 0.012):
            wall_elem(mb, wall, a, b, 0.0, 1.0, 0.012, "wood_dark")      # 웨인스코팅
        for a, b in spans(name, s0, s1, 0.02):
            wall_elem(mb, wall, a, b, 0.0, 0.12, 0.02, "trim")           # 걸레받이
        for a, b in spans(name, s0, s1, 0.035):
            wall_elem(mb, wall, a, b, 0.98, 1.05, 0.035, "trim")         # 의자 몰딩
        for a, b in spans(name, s0, s1, 0.04):
            wall_elem(mb, wall, a, b, H - 0.09, H, 0.04, "trim")         # 천장 몰딩
        for a, b in spans(name, s0, s1, 0.022):                          # 돌출 패널
            n = int((b - a - 0.1) // 0.65)
            if n <= 0:
                continue
            start = (a + b) / 2 - (n - 1) * 0.65 / 2
            for k in range(n):
                c = start + k * 0.65
                wall_elem(mb, wall, c - 0.25, c + 0.25, 0.22, 0.86, 0.022, "wood_mid")

    # --- 뒤쪽 문 (플레이어 등 뒤) ---
    dx0, dx1, dh = DOOR
    fw = ("z", Z0, +1)
    wall_elem(mb, fw, dx0, dx1, 0.0, dh, 0.02, "wood_mid")                 # 문짝
    wall_elem(mb, fw, dx0 - 0.08, dx0, 0.0, dh + 0.08, 0.045, "trim")      # 문틀
    wall_elem(mb, fw, dx1, dx1 + 0.08, 0.0, dh + 0.08, 0.045, "trim")
    wall_elem(mb, fw, dx0 - 0.08, dx1 + 0.08, dh, dh + 0.08, 0.045, "trim")
    wall_elem(mb, fw, dx0 + 0.1, dx1 - 0.1, 1.15, 1.95, 0.032, "wood_light")
    wall_elem(mb, fw, dx0 + 0.1, dx1 - 0.1, 0.2, 1.0, 0.032, "wood_light")
    wall_elem(mb, fw, dx1 - 0.14, dx1 - 0.08, 1.0, 1.06, 0.075, "brass")   # 손잡이

    room = mb.build("DartRoom", sharp_deg=40)
    C.bevel_all(room, 0.0025, 1)
    return room


# ===========================================================================
# 다트판 주변
# ===========================================================================
def build_backboard():
    # 피벗 = 다트판 앞면 중심. 벽 안쪽 면은 다트판 앞면에서 +0.10 m 뒤.
    mb = C.MeshBuilder()
    C.ubox(mb, (-0.45, -0.45, 0.06), (0.45, 0.45, 0.10), "wood_dark")
    C.ubox(mb, (-0.47, -0.47, 0.085), (0.47, 0.47, 0.10), "trim")
    plaque = mb.build("Plaque", sharp_deg=40)
    C.bevel_all(plaque, 0.006, 2)

    rb = C.MeshBuilder()
    ring = C.round_profile([
        (-0.060, 0.2268, "rubber"),
        (-0.012, 0.2268, "rubber"),
        (-0.012, 0.340, "rubber"),
        (-0.060, 0.340, "rubber"),
    ], 0.005, 2)
    C.lathe(rb, ring, seg=96, axis="Y", closed=True)   # Blender -Y = Unity +Z (벽 쪽)
    surround = rb.build("Surround", sharp_deg=40)
    return join("BoardBackboard", [plaque, surround])


def build_scoreboard():
    # 피벗 = 칠판 면 중심, 앞면 -Z. 뒷면은 +0.025 (벽에 닿는 면).
    W, Hh, F = 0.90, 0.60, 0.05
    mb = C.MeshBuilder()
    C.ubox(mb, (-W / 2 + F, -Hh / 2 + F, 0.0), (W / 2 - F, Hh / 2 - F, 0.025), "chalkboard")
    C.ubox(mb, (-W / 2, Hh / 2 - F, -0.012), (W / 2, Hh / 2, 0.025), "wood_mid")
    C.ubox(mb, (-W / 2, -Hh / 2, -0.012), (W / 2, -Hh / 2 + F, 0.025), "wood_mid")
    C.ubox(mb, (-W / 2, -Hh / 2 + F, -0.012), (-W / 2 + F, Hh / 2 - F, 0.025), "wood_mid")
    C.ubox(mb, (W / 2 - F, -Hh / 2 + F, -0.012), (W / 2, Hh / 2 - F, 0.025), "wood_mid")
    C.ubox(mb, (-W / 2 + 0.04, -Hh / 2 - 0.015, -0.06), (W / 2 - 0.04, -Hh / 2 + 0.005, 0.025), "wood_dark")
    obj = mb.build("Frame", sharp_deg=40)
    C.bevel_all(obj, 0.003, 1)
    cb = C.MeshBuilder()   # 분필 두 개 (베벨 없이)
    C.ubox(cb, (0.20, -Hh / 2 + 0.005, -0.045), (0.27, -Hh / 2 + 0.017, -0.033), "chalk")
    C.ubox(cb, (0.30, -Hh / 2 + 0.005, -0.040), (0.34, -Hh / 2 + 0.017, -0.028), "chalk")
    chalk = cb.build("Chalk", sharp_deg=40)
    return join("ScoreBoard", [obj, chalk])


def neon_sign(name, lines, plate_pad=0.07):
    """lines: [(글자, 크기, 색, y)] — 피벗 = 뒷판 뒷면 중심, 글자는 -Z(플레이어) 쪽."""
    mb = C.MeshBuilder()
    xmax, ymin, ymax = 0.0, 1e9, -1e9
    for body, size, sw, y in lines:
        me = C.text_mesh(body, size, 0.006, offset=size * 0.035)
        xs = [v.co.x for v in me.vertices]
        ys = [v.co.y for v in me.vertices]
        xmax = max(xmax, max(abs(min(xs)), abs(max(xs))))
        ymin, ymax = min(ymin, min(ys) + y), max(ymax, max(ys) + y)
        # 글자 로컬 (x, y, z) -> Unity (x, y + 줄 위치, -0.026 - z): 앞면이 플레이어 쪽
        C.add_mesh_data(mb, me, sw, lambda co, y=y: C.U(co.x, co.y + y, -0.032 - co.z))
        bpy.data.meshes.remove(me)
    text = mb.build("Text", sharp_deg=40)
    pb = C.MeshBuilder()
    C.ubox(pb, (-xmax - plate_pad, ymin - plate_pad, -0.02), (xmax + plate_pad, ymax + plate_pad, 0.0), "acrylic")
    for sx in (-1, 1):                                       # 고정 볼트
        for sy in (ymin - plate_pad + 0.03, ymax + plate_pad - 0.03):
            bx = sx * (xmax + plate_pad - 0.03)
            C.ubox(pb, (bx - 0.008, sy - 0.008, -0.03), (bx + 0.008, sy + 0.008, -0.02), "steel")
    plate = pb.build("Plate", sharp_deg=40)
    C.bevel_all(plate, 0.004, 2)
    return join(name, [plate, text])


# ===========================================================================
# 조명 · 가구 · 장식
# ===========================================================================
def build_pendant():
    # 피벗 = 천장 고정점(위). 아래로 0.61 m. 전구 중심은 y = -0.53.
    mb = C.MeshBuilder()
    C.lathe(mb, C.round_profile([(0.0, 0.0, "metal_black"), (0.0, 0.06, "metal_black"),
                                 (-0.025, 0.05, "metal_black"), (-0.025, 0.0, "metal_black")], 0.004, 2),
            seg=24, axis="Z")
    C.lathe(mb, [(-0.02, 0.0035, "shaft_black"), (-0.45, 0.0035, "shaft_black")], seg=8, axis="Z")
    C.lathe(mb, [(-0.440, 0.012, "metal_black"), (-0.440, 0.050, "metal_black"),
                 (-0.470, 0.072, "metal_black"), (-0.600, 0.190, "metal_black"),
                 (-0.610, 0.190, "cream"), (-0.606, 0.183, "cream"),
                 (-0.472, 0.064, "cream"), (-0.452, 0.012, "cream")], seg=40, axis="Z", closed=True)
    C.lathe(mb, [(-0.450, 0.0, "brass"), (-0.450, 0.016, "brass"), (-0.495, 0.016, "brass"),
                 (-0.495, 0.0, "brass")], seg=16, axis="Z")
    bulb = [(-0.495, 0.0, "bulb")]
    for k in range(1, 10):
        a = math.pi * k / 10
        bulb.append((-0.530 + 0.036 * math.cos(a) - 0.0, 0.036 * math.sin(a), "bulb"))
    bulb.append((-0.566, 0.0, "bulb"))
    bulb[1:-1] = [(t, r, sw) for t, r, sw in bulb[1:-1] if t < -0.497]
    C.lathe(mb, bulb, seg=20, axis="Z")
    return mb.build("PendantLamp", sharp_deg=40)


def build_stool():
    mb = C.MeshBuilder()
    C.lathe(mb, C.round_profile([
        (0.0, 0.0, "rubber"), (0.0, 0.19, "metal_black"), (0.012, 0.19, "metal_black"),
        (0.03, 0.08, "metal_black"), (0.035, 0.022, "metal_black"),
        (0.66, 0.022, "metal_black"), (0.68, 0.11, "metal_black"), (0.70, 0.11, "metal_black"),
        (0.70, 0.0, "metal_black"),
    ], 0.006, 2), seg=40, axis="Z")
    C.lathe(mb, C.round_profile([
        (0.70, 0.0, "leather_red"), (0.70, 0.185, "leather_red"), (0.77, 0.19, "leather_red"),
        (0.785, 0.10, "leather_red"), (0.785, 0.0, "leather_red"),
    ], 0.02, 3), seg=40, axis="Z")
    # 발 받침 고리 + 살 4개
    C.lathe(mb, [(0.272, 0.152, "steel"), (0.288, 0.152, "steel"), (0.288, 0.168, "steel"),
                 (0.272, 0.168, "steel")], seg=48, axis="Z", c=(0, 0, 0), closed=True)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        ca, sa = math.cos(a), math.sin(a)

        def to3d(s, h, w, ca=ca, sa=sa):
            return (s * ca - w * sa, s * sa + w * ca, h)
        C.prism(mb, [(0.02, 0.274), (0.155, 0.274), (0.155, 0.286), (0.02, 0.286)], -0.006, 0.006, "steel", to3d)
    return mb.build("BarStool", sharp_deg=40)


def disc(mb, r, z0, z1, sw, seg=56, cy=0.0):
    poly = [(r * math.cos(2 * math.pi * k / seg), cy + r * math.sin(2 * math.pi * k / seg)) for k in range(seg)]
    C.prism(mb, poly, z0, z1, sw, lambda x, y, z: C.U(x, y, z))


def build_poster():
    # 피벗 = 뒷면 중심, 앞면 -Z. 0.5 x 0.7 m 빈티지 다트 포스터
    W, Hh = 0.5, 0.7
    fb = C.MeshBuilder()
    C.ubox(fb, (-W / 2, -Hh / 2, -0.025), (W / 2, Hh / 2, 0.0), "wood_dark")
    frame = fb.build("PFrame", sharp_deg=40)
    C.bevel_all(frame, 0.004, 1)
    mb = C.MeshBuilder()
    C.ubox(mb, (-W / 2 + 0.03, -Hh / 2 + 0.03, -0.028), (W / 2 - 0.03, Hh / 2 - 0.03, -0.025), "cream")
    cy = 0.07
    for r, sw, z in ((0.17, "board_black", -0.029), (0.155, "poster_red", -0.030),
                     (0.11, "cream", -0.031), (0.07, "poster_green", -0.032), (0.025, "poster_red", -0.033)):
        disc(mb, r, -0.028, z, sw, cy=cy)
    me = C.text_mesh("DARTS", 0.075, 0.0008, offset=0.002)
    C.add_mesh_data(mb, me, "board_black", lambda co: C.U(co.x, co.y - 0.215, -0.0298 - co.z))
    bpy.data.meshes.remove(me)
    art = mb.build("Art", sharp_deg=40)
    return join("PosterFrame", [frame, art])


def build_oche():
    mb = C.MeshBuilder()
    C.ubox(mb, (-0.35, 0.0, -0.025), (0.35, 0.008, 0.025), "brass")
    o = mb.build("OcheLine", sharp_deg=40)
    C.bevel_all(o, 0.002, 2)
    return o


# ===========================================================================
# UI 스프라이트 (흰색, Unity에서 Image 색으로 칠함)
# ===========================================================================
def save_sprite(name, alpha):
    n = alpha.shape[0]
    px = np.ones((n, n, 4), dtype=np.float32)
    px[:, :, 3] = alpha
    img = bpy.data.images.new(name, n, n, alpha=True)
    img.alpha_mode = "STRAIGHT"
    img.pixels.foreach_set(px.ravel())
    os.makedirs(os.path.join(C.ART, "UI"), exist_ok=True)
    img.filepath_raw = os.path.join(C.ART, "UI", name + ".png")
    img.file_format = "PNG"
    img.save()
    print(f"[sprite] {img.filepath_raw}")


def make_sprites():
    n = 256
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) + 0.5
    r = 64.0                                            # 모서리 반지름 (9-slice 테두리 = 64)
    qx = np.maximum(np.abs(xx - n / 2) - (n / 2 - r), 0)
    qy = np.maximum(np.abs(yy - n / 2) - (n / 2 - r), 0)
    d = np.sqrt(qx * qx + qy * qy) - r
    save_sprite("UI_RoundedRect", np.clip(0.5 - d, 0, 1))
    m = 128
    yy, xx = np.mgrid[0:m, 0:m].astype(np.float32) + 0.5
    d = np.sqrt((xx - m / 2) ** 2 + (yy - m / 2) ** 2) - (m / 2 - 2)
    save_sprite("UI_Circle", np.clip(0.5 - d, 0, 1))


BUILDERS = {
    "DartRoom": build_room,
    "BoardBackboard": build_backboard,
    "ScoreBoard": build_scoreboard,
    "NeonSign_Title": lambda: neon_sign("NeonSign_Title", [("DART CHALLENGE", 0.15, "neon_pink", 0.0)]),
    "NeonSign_777": lambda: neon_sign("NeonSign_777", [("BULL", 0.07, "neon_cyan", 0.075),
                                                        ("777", 0.16, "neon_pink", -0.04)]),
    "PendantLamp": build_pendant,
    "BarStool": build_stool,
    "PosterFrame": build_poster,
    "OcheLine": build_oche,
}

if __name__ == "__main__":
    C.reset()
    C.make_palette_textures()
    total = 0
    for nm, fn in BUILDERS.items():
        C.reset()
        obj = fn()
        C.export_fbx(obj, nm + ".fbx")
    C.reset()
    make_sprites()

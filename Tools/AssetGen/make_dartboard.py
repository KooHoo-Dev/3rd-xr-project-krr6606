"""다트판 (Dartboard.fbx + T_Dartboard_Albedo.png)

규칙: 일반 다트판과 같고 Inner Bull만 777점 (docs/decisions/001 참고).
좌표: 피벗 = 판 앞면 중심, 앞면 = Unity -Z (Blender +Y), Unity +X = 플레이어 기준 오른쪽.
"""
import math
import os
import random
import sys

import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

R = 0.2255                       # 판 전체 반지름 (지름 451 mm)
IB, OB = 0.00635, 0.0159         # Inner / Outer Bull
TI, TO = 0.099, 0.107            # Triple 링
DI, DO = 0.162, 0.170            # Double 링
ORDER = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
TEX = 2048
COL = {
    "bg": "#141518", "black": "#1C1D21", "cream": "#E6D9BC",
    "red": "#C21F2E", "green": "#1D7444", "wire": "#AEB4BC", "num": "#F1EEE6",
}


# ===========================================================================
# 1) 텍스처: 2D 배치를 위에서 정사영 렌더 (x = 플레이어 기준 오른쪽, y = 위)
# ===========================================================================
def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def flat_mat(key):
    m = bpy.data.materials.get("F_" + key)
    if m is None:
        m = bpy.data.materials.new("F_" + key)
        r, g, b = (srgb_to_lin(v) for v in C.hex_rgb(COL[key]))
        m.diffuse_color = (r, g, b, 1)
    return m


def pt(r, deg, z):
    a = math.radians(deg)          # 위에서 시계 방향
    return (r * math.sin(a), r * math.cos(a), z)


class Flat:
    def __init__(self):
        self.parts = {}

    def quad(self, key, vs):
        self.parts.setdefault(key, []).append(vs)

    def arc(self, key, r0, r1, a0, a1, z, steps):
        for k in range(steps):
            b0 = a0 + (a1 - a0) * k / steps
            b1 = a0 + (a1 - a0) * (k + 1) / steps
            self.quad(key, [pt(r0, b0, z), pt(r1, b0, z), pt(r1, b1, z), pt(r0, b1, z)])

    def build(self):
        for key, quads in self.parts.items():
            verts, faces = [], []
            for q in quads:
                faces.append(tuple(range(len(verts), len(verts) + len(q))))
                verts += q
            me = bpy.data.meshes.new("L_" + key)
            me.from_pydata(verts, [], faces)
            me.materials.append(flat_mat(key))
            bpy.context.scene.collection.objects.link(bpy.data.objects.new("L_" + key, me))


def make_texture():
    C.reset()
    L = Flat()
    s = R * 1.05
    L.quad("bg", [(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)])
    for i, _ in enumerate(ORDER):
        c = i * 18.0
        a0, a1 = c - 9, c + 9
        single = "black" if i % 2 == 0 else "cream"
        ring = "red" if i % 2 == 0 else "green"
        L.arc(single, OB, TI, a0, a1, 0.001, 10)
        L.arc(ring, TI, TO, a0, a1, 0.001, 10)
        L.arc(single, TO, DI, a0, a1, 0.001, 10)
        L.arc(ring, DI, DO, a0, a1, 0.001, 10)
    L.arc("green", IB, OB, 0, 360, 0.001, 64)
    L.arc("red", 0, IB, 0, 360, 0.001, 48)
    # 와이어(스파이더) — 3D 와이어 아래 깔리는 선. 멀리서 볼 때 경계를 또렷하게 한다.
    w = 0.0005
    for rr in (IB, OB, TI, TO, DI, DO):
        L.arc("wire", rr - w, rr + w, 0, 360, 0.002, 160)
    for i in range(20):
        a = i * 18.0 + 9
        p = [(math.sin(math.radians(a)), math.cos(math.radians(a)))]
        dx, dy = p[0]
        nx, ny = dy * w, -dx * w
        L.quad("wire", [(OB * dx - nx, OB * dy - ny, 0.002), (DO * dx - nx, DO * dy - ny, 0.002),
                        (DO * dx + nx, DO * dy + ny, 0.002), (OB * dx + nx, OB * dy + ny, 0.002)])
    L.build()

    # 숫자 (똑바로 세운 형태)
    for i, n in enumerate(ORDER):
        cu = bpy.data.curves.new(f"N{n}", "FONT")
        cu.body = str(n)
        cu.size = 0.030
        cu.align_x, cu.align_y = "CENTER", "CENTER"
        cu.offset = 0.0006              # 글자를 조금 두껍게
        cu.materials.append(flat_mat("num"))
        ob = bpy.data.objects.new(f"N{n}", cu)
        ob.location = pt(0.1975, i * 18.0, 0.003)
        bpy.context.scene.collection.objects.link(ob)

    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light = "FLAT"
    sh.color_type = "MATERIAL"
    sh.show_shadows = sh.show_cavity = sh.show_object_outline = sh.show_specular_highlight = False
    sc.display.render_aa = "32"
    sc.view_settings.view_transform = "Standard"
    sc.render.resolution_x = sc.render.resolution_y = TEX
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    cam_d = bpy.data.cameras.new("TexCam")
    cam_d.type = "ORTHO"
    cam_d.ortho_scale = 2 * R
    cam = bpy.data.objects.new("TexCam", cam_d)
    cam.location = (0, 0, 1)
    sc.collection.objects.link(cam)
    sc.camera = cam
    path = os.path.join(C.TEXTURES, "T_Dartboard_Albedo.png")
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)

    # 사이잘(sisal) 섬유 느낌의 아주 약한 노이즈
    img = bpy.data.images.load(path)
    px = np.empty(TEX * TEX * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(-1, 4)
    rng = np.random.default_rng(7)
    grain = 1.0 + (rng.random(TEX * TEX, dtype=np.float32) - 0.5) * 0.07
    px[:, :3] = np.clip(px[:, :3] * grain[:, None], 0, 1)
    img.pixels.foreach_set(px.ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    print(f"[texture] {path}")


# ===========================================================================
# 2) 모델
# ===========================================================================
def board_uv(co):
    # 플레이어 기준 오른쪽 = Blender -X, 위 = Blender +Z
    return (0.5 + (-co.x) / (2 * R), 0.5 + co.z / (2 * R))


def build_board(name="Dartboard"):
    mb = C.MeshBuilder()
    TEXF = ("M_Dartboard", board_uv)
    D = 0.038                                   # 판 두께
    body = C.round_profile([
        (-D, 0.0, "board_black"),
        (-D, R - 0.002, "board_black"),
        (-0.002, R, "board_black"),
        (0.0, R - 0.004, TEXF),
    ], 0.004, 3)
    body += [(0.0, r, TEXF) for r in (0.19, 0.15, 0.11, 0.07, 0.03)]
    body += [(0.0, 0.0, TEXF)]
    C.lathe(mb, body, seg=96, axis="Y")

    # 원형 와이어: 단면이 둥근 사각형인 고리
    w, h = 0.0005, 0.0012
    for rr, seg in ((IB, 32), (OB, 40), (TI, 96), (TO, 96), (DI, 120), (DO, 120)):
        C.lathe(mb, [(0.0, rr - w, "wire_silver"), (h * 0.75, rr - w, "wire_silver"),
                     (h, rr, "wire_silver"), (h * 0.75, rr + w, "wire_silver"),
                     (0.0, rr + w, "wire_silver")], seg=seg, axis="Y", closed=True)
    # 방사형 와이어 20개
    for i in range(20):
        a = math.radians(i * 18.0 + 9)
        dx, dz = -math.sin(a), math.cos(a)        # 플레이어 기준 (sin, cos) -> Blender (-x, z)
        px, pz = dz, -dx

        def to3d(s, hh, ww, dx=dx, dz=dz, px=px, pz=pz):
            return (s * dx + ww * px, hh, s * dz + ww * pz)
        C.prism(mb, [(OB, 0.0), (DO, 0.0), (DO, h * 0.8), (OB, h * 0.8)], -w, w, "wire_silver", to3d)

    return mb.build(name, materials=("M_Palette", "M_Dartboard"), sharp_deg=40)


def make_model():
    C.reset()
    board = build_board()
    C.export_fbx(board, "Dartboard.fbx")
    C.render_previews([board], "Dartboard", [("front", 180, 0), ("angle", 145, 18)],
                      ground=False, fill=0.95)


if __name__ == "__main__":
    random.seed(1)
    make_texture()
    make_model()

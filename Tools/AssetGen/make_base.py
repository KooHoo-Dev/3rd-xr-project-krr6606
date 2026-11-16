"""기본 에셋: 공용 팔레트 텍스처 + 던지는 선 + UI 스프라이트

만드는 것 (모두 Assets/_Project/Art/ 아래)
  Textures/T_Palette_*.png   공용 팔레트 (색 · 금속도 · 발광)
  Models/OcheLine.fbx        던지는 선 (황동 띠)
  UI/UI_RoundedRect.png, UI/UI_Circle.png

실내 다트 바 방 · 네온 · 칠판 등은 기획 전환으로 삭제했다 (docs/decisions/003).
모든 좌표는 Unity 기준(C.U / C.ubox)으로 적었다. 1 = 1 m, +Z = 앞.
"""
import os
import sys

import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402


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
    "OcheLine": build_oche,
}

if __name__ == "__main__":
    C.reset()
    C.make_palette_textures()
    for nm, fn in BUILDERS.items():
        C.reset()
        obj = fn()
        C.export_fbx(obj, nm + ".fbx")
    C.reset()
    make_sprites()

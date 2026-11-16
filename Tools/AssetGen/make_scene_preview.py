"""데모 씬 배치를 Blender에서 미리 렌더 (Unity 씬과 같은 배치표 layout.py 사용).

결과: docs/assets/previews/Scene_player.png, Scene_corner.png
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import layout as LY  # noqa: E402
import make_room as R  # noqa: E402
import make_props as P  # noqa: E402
import make_dartboard as DB  # noqa: E402
from dart_geo import build_dart  # noqa: E402

BUILD = dict(R.BUILDERS)
BUILD.update({"Dartboard": DB.build_board, "BarTable": P.make_table, "DartHolder": P.make_holder})


def place(obj, pos, rot_y):
    obj.location = C.U(*pos)
    obj.rotation_euler = (0, 0, math.radians(-rot_y))   # Unity Y 회전 -> Blender Z 회전 (부호 반대)


C.reset()
objs = []
holder = None
for name, pos, rot in LY.LAYOUT:
    o = BUILD[name]()
    place(o, pos, rot)
    objs.append(o)
    if name == "DartHolder":
        holder = o
bpy.context.view_layer.update()
for e in sorted(holder.children, key=lambda o: o.name):     # 다트 7개를 슬롯에 꽂기
    d = build_dart("D" + e.name)
    d.matrix_world = e.matrix_world.copy()
    d.rotation_euler = (math.radians(90), 0, d.rotation_euler.z)
    d.location = e.matrix_world.translation

# --- 조명 (Unity 씬과 비슷하게) ---
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
sc.view_settings.view_transform = "AgX"
try:
    sc.eevee.taa_render_samples = 64
    sc.eevee.use_raytracing = True
except Exception:
    pass
world = bpy.data.worlds.new("W")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.35, 0.3, 0.25, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25
sc.world = world


def light(kind, pos, energy, color, target=None, size=0.05, spot_deg=60):
    ld = bpy.data.lights.new(kind, kind)
    ld.energy = energy
    ld.color = color
    ld.shadow_soft_size = size
    if kind == "SPOT":
        ld.spot_size = math.radians(spot_deg)
        ld.spot_blend = 0.5
    lo = bpy.data.objects.new(kind, ld)
    lo.location = C.U(*pos)
    if target:
        d = (Vector(C.U(*target)) - lo.location).normalized()
        lo.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.collection.objects.link(lo)


WARM = (1.0, 0.82, 0.62)
light("SPOT", (0.0, 2.47, 1.25), 220, WARM, target=LY.BOARD_CENTER, spot_deg=70)
light("POINT", (0.0, 2.40, 1.25), 25, WARM, size=0.1)
light("POINT", (-1.45, 2.40, -0.25), 60, WARM, size=0.1)
light("POINT", (0.3, 2.6, -0.8), 80, (1.0, 0.9, 0.8), size=0.5)
light("POINT", (0.0, 2.55, 1.9), 8, (1.0, 0.3, 0.6), size=0.3)     # 네온 번짐
light("POINT", (1.15, 1.75, 1.9), 5, (1.0, 0.3, 0.6), size=0.3)

cam_d = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam
for label, pos, target, lens in (
        ("player", (0.0, 1.62, LY.PLAYER[2]), (0.0, 1.55, 2.0), 14),
        ("corner", (-1.8, 2.45, -1.7), (0.35, 1.15, 1.2), 12)):
    cam_d.lens = lens
    cam.location = C.U(*pos)
    d = (Vector(C.U(*target)) - cam.location).normalized()
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(C.PREVIEWS, f"Scene_{label}.png")
    bpy.ops.render.render(write_still=True)
    print(f"[preview] {sc.render.filepath}")

"""데모 씬 배치를 Blender에서 미리 렌더 (Unity 씬과 같은 배치표 layout.py 사용). — AI-Assist: generated

결과: docs/assets/previews/Scene_player.png (플레이어 눈높이), Scene_behind.png (뒤에서), Scene_valley.png (계곡 전체)
조명은 Unity 씬과 비슷하게 해 하나 + 하늘색 환경광. 실제 색감은 Unity Skybox · URP 설정에 따라 조금 다르다.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import layout as LY  # noqa: E402
import make_balloons as BL  # noqa: E402
import make_base as B  # noqa: E402
import make_props as P  # noqa: E402
import make_valley as V  # noqa: E402

BUILD = dict(B.BUILDERS)
BUILD.update({"LogStand": P.make_log_stand,
              "Valley": lambda: V.build_valley()[0]})
SIZES = {n: (d, sw) for n, d, sw in BL.BALLOONS}


def place(obj, pos, rot_y):
    obj.location = C.U(*pos)
    obj.rotation_euler = (0, 0, math.radians(-rot_y))   # Unity Y 회전 -> Blender Z 회전 (부호 반대)


C.reset()
for name, pos, rot in LY.LAYOUT:
    o = BUILD[name]()
    place(o, pos, rot)
for name, pos in LY.BALLOONS:
    d, sw = SIZES[name]
    place(BL.build_balloon(name, d, sw), pos, 0)
bpy.context.view_layer.update()

# --- 조명: 해 + 하늘 ---
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
sc.view_settings.view_transform = "AgX"
try:
    sc.eevee.taa_render_samples = 64
except Exception:
    pass
world = bpy.data.worlds.new("Sky")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.72, 0.95, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
sc.world = world

sun_d = bpy.data.lights.new("Sun", "SUN")
sun_d.energy = 3.5
sun_d.angle = math.radians(3)
sun_d.color = (1.0, 0.95, 0.85)
sun = bpy.data.objects.new("Sun", sun_d)
sc.collection.objects.link(sun)
d = Vector(C.U(-0.32, -0.77, 0.56)).normalized()       # Unity Sun 회전 (50, -30, 0)의 빛 방향 (오른쪽 뒤 위에서 앞으로)
sun.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

# --- 카메라 ---
cam_d = bpy.data.cameras.new("Cam")
cam_d.clip_end = 400
cam = bpy.data.objects.new("Cam", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam
for label, pos, target, lens in (
        ("player", (0.0, 1.62, LY.PLAYER[2]), (0.0, 1.35, 3.0), 13),
        ("behind", (-2.2, 2.6, -3.6), (0.2, 0.9, 2.0), 16),
        ("valley", (0.0, 11.0, -15.0), (0.0, 0.5, 6.0), 18)):
    cam_d.lens = lens
    cam.location = C.U(*pos)
    dv = (Vector(C.U(*target)) - cam.location).normalized()
    cam.rotation_euler = dv.to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(C.PREVIEWS, f"Scene_{label}.png")
    bpy.ops.render.render(write_still=True)
    print(f"[preview] {sc.render.filepath}")

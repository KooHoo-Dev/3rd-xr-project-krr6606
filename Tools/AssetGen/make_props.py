"""다트통 (DartHolder.fbx) + 통나무 받침대 (LogStand.fbx)

피벗은 둘 다 바닥 중심. 받침대 윗면 높이 = 1.0 m → 다트통을 (0, 1.0, 0)에 올리면 된다.
다트통 Slot_01~07 = 꽂힌 다트의 '촉 끝' 위치. 다트(피벗 = 촉 끝)를 Slot 위치에 두고 촉이 아래를 향하게 회전.
"""
import math
import os
import sys

import bpy
import bmesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
from dart_geo import build_dart  # noqa: E402

HOLDER_R, HOLDER_H = 0.065, 0.075
SLOT_RING, SLOT_COUNT = 0.042, 7
HOLE_R, HOLE_DEPTH = 0.0030, 0.034
TIP_LEN = 0.030                      # 다트 촉 길이 (make_dart.py와 같은 값)
TABLE_H = 1.0


def apply_boolean(obj, cutters):
    for ct in cutters:
        m = obj.modifiers.new("cut", "BOOLEAN")
        m.operation = "DIFFERENCE"
        m.solver = "EXACT"
        m.object = ct
        try:
            m.material_mode = "TRANSFER"
        except Exception:
            pass
    dg = bpy.context.evaluated_depsgraph_get()
    new_me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    obj.modifiers.clear()
    old = obj.data
    obj.data = new_me
    bpy.data.meshes.remove(old)
    for ct in cutters:
        bpy.data.objects.remove(ct)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    C.mark_sharp(bm, 40)
    bm.to_mesh(obj.data)
    bm.free()
    C.finish_mesh(obj.data)


def make_holder():
    mb = C.MeshBuilder()
    prof = C.round_profile([
        (0.0, 0.0, "felt_green"),
        (0.0, HOLDER_R - 0.002, "felt_green"),
        (0.003, HOLDER_R - 0.002, "wood_mid"),
        (0.003, HOLDER_R, "wood_mid"),
        (0.052, HOLDER_R, "brass"),          # 황동 띠
        (0.052, HOLDER_R + 0.0015, "brass"),
        (0.060, HOLDER_R + 0.0015, "brass"),
        (0.060, HOLDER_R, "wood_mid"),
        (HOLDER_H, HOLDER_R, "wood_light"),
        (HOLDER_H, HOLDER_R - 0.006, "wood_light"),
        (HOLDER_H, 0.020, "wood_light"),
        (HOLDER_H, 0.0, "wood_light"),
    ], 0.0025, 2)
    C.lathe(mb, prof, seg=48, axis="Z")
    holder = mb.build("DartHolder", sharp_deg=40)

    cutters = []
    for i in range(SLOT_COUNT):
        a = math.radians(90 + 360 * i / SLOT_COUNT)
        cx, cy = SLOT_RING * math.cos(a), SLOT_RING * math.sin(a)
        cm = C.MeshBuilder()
        top = HOLDER_H
        C.lathe(cm, [(top - HOLE_DEPTH, 0.0, "hole_dark"), (top - HOLE_DEPTH, HOLE_R, "hole_dark"),
                     (top - 0.002, HOLE_R, "hole_dark"), (top + 0.0002, HOLE_R + 0.0018, "hole_dark"),
                     (top + 0.01, HOLE_R + 0.0018, "hole_dark"), (top + 0.01, 0.0, "hole_dark")],
                seg=16, axis="Z", c=(cx, cy, 0))
        cutters.append(cm.build(f"Cut{i}", sharp_deg=40))
    apply_boolean(holder, cutters)

    for i in range(SLOT_COUNT):
        a = math.radians(90 + 360 * i / SLOT_COUNT)
        e = C.add_empty(f"Slot_{i + 1:02d}", holder,
                        (SLOT_RING * math.cos(a), SLOT_RING * math.sin(a), HOLDER_H - TIP_LEN))
        e.rotation_euler = (math.radians(90), 0, 0)   # Unity +Z(앞)가 아래를 향하도록
    return holder


def make_log_stand():
    """통나무 받침대: 굵은 통나무를 세우고 윗면을 평평하게 자른 모양 (윗면 높이 = TABLE_H).
    회전체로 만든 뒤 각도마다 반지름을 조금씩 바꿔 나무껍질의 울퉁불퉁함을 낸다."""
    mb = C.MeshBuilder()
    R = 0.17
    prof = [
        (0.0, 0.0, "bark_dark"),
        (0.0, R + 0.06, "bark_dark"),        # 뿌리 쪽으로 퍼짐
        (0.05, R + 0.035, "bark_dark"),
        (0.14, R + 0.005, "bark"),
        (0.45, R, "bark"),
        (0.80, R - 0.005, "bark"),
        (TABLE_H - 0.02, R - 0.005, "bark"),
        (TABLE_H, R - 0.012, "wood_ring"),   # 껍질 안쪽 테두리
        (TABLE_H, R - 0.030, "wood_cut"),
        (TABLE_H, R - 0.070, "wood_ring"),   # 나이테 한 줄
        (TABLE_H, R - 0.080, "wood_cut"),
        (TABLE_H, 0.0, "wood_cut"),
    ]
    C.lathe(mb, prof, seg=24, axis="Z")
    obj = mb.build("LogStand", sharp_deg=50)
    me = obj.data
    for v in me.vertices:                     # 각도에 따라 반지름을 흔든다 (윗면 높이는 그대로)
        a = math.atan2(v.co.y, v.co.x) + 0.5 * v.co.z      # 높이에 따라 살짝 비틀어 결이 기울게
        k = 1.0 + 0.045 * math.sin(5 * a + 1.0) + 0.03 * math.sin(9 * a + 2.0) + 0.02 * math.sin(17 * a)
        v.co.x *= k
        v.co.y *= k
    # 껍질 면을 각도마다 번갈아 어둡게 칠해 세로 골을 표현 (팔레트 UV만 바꾼다)
    uv = me.uv_layers.active.data
    bark_uv, dark_uv = C.palette_uv("bark"), C.palette_uv("bark_dark")
    for poly in me.polygons:
        u0 = uv[poly.loop_start].uv
        if abs(u0[0] - bark_uv[0]) > 1e-4 or abs(u0[1] - bark_uv[1]) > 1e-4:
            continue
        c = poly.center
        if math.sin(7 * math.atan2(c.y, c.x) + 3.0 * c.z) > 0.35:
            for li in poly.loop_indices:
                uv[li].uv = dark_uv
    me.update()
    return obj


def place_darts(holder):
    """미리보기용: 다트를 슬롯에 꽂는다 (내보내기 뒤에 추가하므로 FBX에는 포함되지 않음)."""
    bpy.context.view_layer.update()
    darts = []
    for e in sorted(holder.children, key=lambda o: o.name):
        d = build_dart(f"PreviewDart{len(darts)}")
        d.location = e.matrix_world.translation
        d.rotation_euler = (math.radians(90), 0, math.radians(23 * len(darts)))  # 몸통이 위로
        darts.append(d)
    return darts


if __name__ == "__main__":
    C.reset()
    holder = make_holder()
    C.export_fbx(holder, "DartHolder.fbx")
    darts = place_darts(holder)
    C.render_previews([holder] + darts, "DartHolder", [("hero", 30, 28)], ground=True, fill=0.9)

    C.reset()
    table = make_log_stand()
    C.export_fbx(table, "LogStand.fbx")
    holder = make_holder()
    holder.location.z = TABLE_H
    darts = place_darts(holder)
    C.render_previews([table, holder] + darts, "LogStand_set", [("hero", 30, 12)], ground=True, fill=1.05)

"""통나무 받침대 (LogStand.fbx) — 새총을 올려 두는 곳

피벗은 바닥 중심. 받침대 윗면 높이 = 1.0 m (TABLE_H).
다트통(DartHolder)과 다트 미리보기는 새총 기획 전환으로 삭제했다 (docs/decisions/008).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

TABLE_H = 1.0


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


if __name__ == "__main__":
    C.reset()
    table = make_log_stand()
    C.export_fbx(table, "LogStand.fbx")
    C.render_previews([table], "LogStand", [("hero", 30, 12)], ground=True, fill=1.05)

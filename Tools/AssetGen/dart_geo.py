"""다트 형상 (make_dart.py, make_props.py 미리보기에서 함께 사용)."""
import math

import common as C


def build_dart(name="Dart"):
    mb = C.MeshBuilder()

    # --- 촉 + 배럴 + 샤프트: 회전체(lathe) 프로파일 (t = 촉에서 거리, r = 반지름, 단위 m) ---
    prof = [
        (0.0000, 0.0000, "steel"),
        (0.0035, 0.0009, "steel"),
        (0.0290, 0.0012, "steel"),
        (0.0300, 0.0012, "brass"),       # 촉 -> 배럴 앞 칼라
        (0.0300, 0.0021, "brass"),
        (0.0350, 0.0034, "tungsten"),
        (0.0380, 0.0036, "tungsten"),
    ]
    # 배럴 그립 홈 (3 mm 간격)
    t = 0.0420
    while t < 0.0720:
        prof += [(t, 0.0036, "tungsten"), (t + 0.0003, 0.0031, "tungsten"),
                 (t + 0.0011, 0.0031, "tungsten"), (t + 0.0014, 0.0036, "tungsten")]
        t += 0.0030
    prof += [
        (0.0780, 0.0036, "tungsten"),
        (0.0800, 0.0034, "brass"),       # 배럴 뒤 칼라
        (0.0850, 0.0024, "shaft_black"),
        (0.0850, 0.0021, "shaft_black"),
        (0.0880, 0.0021, "shaft_black"),
        (0.0880, 0.0024, "shaft_black"),  # 샤프트 링
        (0.0900, 0.0024, "shaft_black"),
        (0.0900, 0.0020, "shaft_black"),
        (0.1240, 0.0018, "shaft_black"),
        (0.1260, 0.0000, "shaft_black"),
    ]
    C.lathe(mb, prof, seg=16, axis="Y")

    # --- 깃(Flight) 4장: 날개 평면 좌표 (t, s) — s = 축에서 떨어진 거리 ---
    FIN_RED = [(0.100, 0.0), (0.122, 0.0160), (0.148, 0.0160), (0.148, 0.0)]
    FIN_WHITE = [(0.148, 0.0), (0.148, 0.0160), (0.155, 0.0160), (0.160, 0.0)]
    HALF_T = 0.00025                     # 깃 두께 0.5 mm
    for k in range(4):
        a = math.radians(45 + 90 * k)    # X자 배치
        ca, sa = math.cos(a), math.sin(a)
        # 날개 평면: 축(Y) 방향 t, 반지름 방향 (ca, sa), 두께 방향 (-sa, ca)

        def to3d(tt, s, w, ca=ca, sa=sa):
            return (s * ca - w * sa, tt, s * sa + w * ca)
        C.prism(mb, FIN_RED, -HALF_T, HALF_T, "flight_red", to3d)
        C.prism(mb, FIN_WHITE, -HALF_T, HALF_T, "flight_white", to3d)

    return mb.build(name, sharp_deg=35)

"""물풍선 4종 (Balloon_Red/Blue/Green/Gold.fbx) — AI-Assist: generated

사양: docs/planning/concept.md 5장, docs/decisions/003
  색     지름(cm)
  Red    35
  Blue   28
  Green  22
  Gold   12
피벗 = 풍선 몸통 중심 → Unity에서 SphereCollider(중심 0, 반지름 = 지름/2)를 그대로 쓸 수 있다.
매듭은 몸통 아래(-Y)에 붙어 있다. 회전체라 앞뒤 방향은 상관없다.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

BALLOONS = [
    # (이름, 지름 m, 팔레트 색)
    ("Balloon_Red",   0.35, "balloon_red"),
    ("Balloon_Blue",  0.28, "balloon_blue"),
    ("Balloon_Green", 0.22, "balloon_green"),
    ("Balloon_Gold",  0.12, "balloon_gold"),
]
SEG = 20            # 둘레 분할 (작은 풍선도 둥글게 보이는 최소치)
RINGS = 12          # 위 → 아래 분할


def balloon_profile(d, sw):
    """회전체 단면 (t = 높이, r = 반지름). 아래에서 위로.
    위쪽 반은 구, 아래쪽 반은 조금 길게 늘이고 목으로 좁아지는 물방울 모양."""
    R = d / 2
    pts = []
    # 매듭 꼬리 → 매듭 → 목 (아래쪽부터)
    pts += [(-R * 1.42, 0.0, sw),
            (-R * 1.42, R * 0.10, sw),
            (-R * 1.34, R * 0.07, sw),
            (-R * 1.28, R * 0.13, sw),      # 매듭 볼록
            (-R * 1.20, R * 0.12, sw),
            (-R * 1.15, R * 0.06, sw)]      # 목
    # 몸통: 극각 phi = pi(아래) → 0(위)
    for k in range(RINGS, 0, -1):
        phi = math.pi * k / RINGS
        r = R * math.sin(phi)
        z = R * math.cos(phi)
        if z < 0:
            z *= 1.12                       # 아래쪽을 살짝 늘여 물이 찬 느낌
            r *= 1.0 - 0.10 * (-z / (R * 1.12)) ** 3   # 목 쪽으로 좁아짐
        if r < R * 0.06:
            continue                        # 목보다 가는 링은 건너뜀
        pts.append((z, r, sw))
    pts.append((R, 0.0, sw))                # 꼭대기
    return pts


def build_balloon(name, d, sw):
    mb = C.MeshBuilder()
    C.lathe(mb, balloon_profile(d, sw), seg=SEG, axis="Z")
    return mb.build(name, sharp_deg=60)


if __name__ == "__main__":
    C.reset()
    C.make_palette_textures()
    objs = []
    for name, d, sw in BALLOONS:
        C.reset()
        C.export_fbx(build_balloon(name, d, sw), name + ".fbx")

    # 미리보기: 4개를 한 줄로 (크기 비교)
    C.reset()
    x = 0.0
    for name, d, sw in BALLOONS:
        x += d / 2                           # 이 풍선의 중심까지
        o = build_balloon(name, d, sw)
        o.location = (-x, 0, d / 2 * 1.42)   # 매듭 끝이 바닥에 닿게
        objs.append(o)
        x += d / 2 + 0.08                    # 다음 풍선과 8 cm 간격
    C.render_previews(objs, "Balloons", [("hero", 15, 12)], ground=True, fill=0.9)

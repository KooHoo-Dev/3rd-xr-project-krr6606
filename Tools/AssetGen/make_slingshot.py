"""새총 (Slingshot.fbx) + 주머니 (Pouch.fbx) + 고무줄 (Band.fbx)

결정 008: 왼손으로 손잡이를 주먹 쥐듯 잡고, 오른손으로 주머니를 당긴다. 탄환은 돌멩이(make_stones.py).

Slingshot: 피벗 = 손잡이 가운데(쥐는 곳), Unity +Y 위로 갈래가 서고, +Z가 쏘는 방향.
    자식 빈 오브젝트 (Unity 좌표):
    GripAttach      손잡이 가운데. XR Grab Interactable의 Attach Transform으로 쓴다 (각도는 Play 중에 맞춤)
    BandAnchor_L/R  갈래 끝, 고무줄이 감긴 자리의 뒤쪽
    (주머니가 쉬는 자리는 고정점이 아니다. 실제 새총처럼 갈래 가운데 아래로 늘어지게 SlingshotPouch가 계산한다)
Pouch: 피벗 = 주머니 가운데. 오목한 면이 +Z(앞). 자식 BandTie_L/R(고무줄 끝),
       StoneSeat(오목면 가운데 근처. 돌멩이 프리팹의 피벗 = 돌멩이 뒷면이라, 여기에 두면 면끼리 맞닿는다)
Band: 길이 1 m짜리 고무줄. 피벗 = 시작점, +Z 방향으로 뻗음.
      Unity에서 BandAnchor에 두고 BandTie를 바라보게 회전, Z 스케일 = 두 점 사이 거리.
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import stone_geo  # noqa: E402

BAND_Z = 0.140                     # 고무줄 감는 높이 (피벗 기준, m)
TIP_X = 0.040                      # 갈래 끝의 좌우 위치
HANG = 0.12                        # 미리보기: 주머니가 갈래 가운데에서 아래로 늘어진 길이 (SlingshotPouch.hangLength와 같게)
POUCH_W, POUCH_H = 0.028, 0.014    # 주머니 반폭 · 반높이
BAND_R = 0.0033                    # 고무줄 반지름


def tube(mb, path, radius_fn, color_fn, seg, ref=Vector((0, 1, 0))):
    """path(Blender 좌표 점 목록)를 따라 관을 만든다. 두 끝은 가운데 점으로 모아 둥글게 닫는다.
    radius_fn(s, a, p) / color_fn(s, a, p): s = 0..1 길이 비율, a = 둘레 각도, p = 고리 중심."""
    n = len(path)
    rings = []
    for i, p in enumerate(path):
        t = (path[min(i + 1, n - 1)] - path[max(i - 1, 0)]).normalized()
        u = t.cross(ref).normalized()
        w = t.cross(u)
        s = i / (n - 1)
        ring = []
        for k in range(seg):
            a = 2 * math.pi * k / seg
            ring.append(mb.v(p + (u * math.cos(a) + w * math.sin(a)) * radius_fn(s, a, p)))
        rings.append(ring)
    for i in range(n - 1):
        s = (i + 0.5) / (n - 1)
        mid = (path[i] + path[i + 1]) / 2
        for k in range(seg):
            k2 = (k + 1) % seg
            mb.f([rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]],
                 color_fn(s, 2 * math.pi * (k + 0.5) / seg, mid))
    for idx, end in ((0, path[0] - (path[1] - path[0])), (n - 1, path[-1] + (path[-1] - path[-2]))):
        c = mb.v(end)
        sw = color_fn(idx / (n - 1), 0, path[idx])
        for k in range(seg):
            k2 = (k + 1) % seg
            mb.f([c, rings[idx][k2], rings[idx][k]] if idx == 0 else [c, rings[idx][k], rings[idx][k2]], sw)


def spline(ctrl, count):
    """Catmull-Rom: 제어점을 부드럽게 잇는 점 count개."""
    P = [ctrl[0]] + ctrl + [ctrl[-1]]
    out = []
    for j in range(count):
        g = j / (count - 1) * (len(ctrl) - 1)
        i = min(int(g), len(ctrl) - 2)
        t = g - i
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return out


def wood(s, a, p):
    # 결: 둘레 방향으로 가는 줄무늬가 길이를 따라 조금씩 휘어진다
    return "wood_grain" if math.sin(6 * a + 0.9 * math.sin(p.z * 35)) > 0.86 else "wood_light"


def make_handle(mb):
    z0, z1 = -0.070, 0.071
    path = [Vector((0, 0, z0 + (z1 - z0) * i / 150)) for i in range(151)]
    W0, W1, PITCH = -0.050, 0.044, 0.0085      # 가죽 감은 구간, 한 바퀴 간격

    def ridge(a, z):                             # 나선으로 감긴 가죽 끈의 볼록한 정도 0..1
        return (0.5 + 0.5 * math.cos(a - 2 * math.pi * z / PITCH)) ** 3

    def radius(s, a, p):
        z = p.z
        if z < -0.062:                           # 손잡이 끝을 둥글게
            return 0.0135 * math.sqrt(max(0.02, 1 - ((-0.062 - z) / 0.0085) ** 2))
        if W0 <= z <= W1:
            edge = 0.0007 if (z - W0 < 0.003 or W1 - z < 0.003) else 0.0
            return 0.0150 + 0.0011 * ridge(a, z) + edge
        if z > 0.064:                            # 갈래 속으로 좁아져 숨는 부분
            return 0.0130 * max(0.35, 1 - (z - 0.064) / 0.02)
        return 0.0135

    def color(s, a, p):
        z = p.z
        if W0 <= z <= W1:
            if z - W0 < 0.003 or W1 - z < 0.003:
                return "leather_dark"
            return "leather_red" if ridge(a, z) > 0.12 else "leather_dark"
        return "wood_mid" if z < W0 else wood(s, a, p)

    tube(mb, path, radius, color, seg=28)


def make_arm(mb, side):
    ctrl = [Vector((side * x, 0, z)) for x, z in
            ((0.000, 0.036), (0.004, 0.060), (0.016, 0.086), (0.029, 0.109), (0.037, 0.128),
             (TIP_X, BAND_Z + 0.004), (0.041, 0.160))]
    path = spline(ctrl, 70)
    knot_s, knot_a = 0.42, (0.0 if side > 0 else math.pi)   # 바깥쪽 옹이 하나

    def wrap(p):                                 # 고무줄이 감긴 구간이면 0..1
        return max(0.0, 1 - abs(p.z - BAND_Z) / 0.0075)

    def radius(s, a, p):
        r = 0.0120 + (0.0090 - 0.0120) * s
        if s > 0.93:                             # 끝을 둥글게
            r *= math.sqrt(max(0.03, 1 - ((s - 0.93) / 0.07) ** 2))
        r *= 1 + 0.20 * math.exp(-((s - knot_s) / 0.035) ** 2) * max(0.0, math.cos(a - knot_a)) ** 6
        if wrap(p) > 0:                          # 고무줄을 여러 번 감은 볼록한 띠
            r += 0.0016 + 0.0005 * math.cos(2 * math.pi * (p.z - BAND_Z) / 0.0032)
        return r

    def color(s, a, p):
        if wrap(p) > 0:
            return "band_latex"
        if math.exp(-((s - knot_s) / 0.03) ** 2) * max(0.0, math.cos(a - knot_a)) ** 6 > 0.25:
            return "wood_knot"
        return wood(s, a, p)

    tube(mb, path, radius, color, seg=24)


def make_slingshot():
    mb = C.MeshBuilder()
    make_handle(mb)
    make_arm(mb, 1)
    make_arm(mb, -1)
    obj = mb.build("Slingshot", sharp_deg=70)
    C.add_empty("GripAttach", obj, (0, 0, 0))
    C.add_empty("BandAnchor_L", obj, C.U(-TIP_X, BAND_Z, -0.006))
    C.add_empty("BandAnchor_R", obj, C.U(TIP_X, BAND_Z, -0.006))
    return obj


def make_pouch():
    """앞(+Z)이 오목한 가죽 조각 + 양 끝에 고무줄을 감아 묶은 매듭. Unity 좌표로 만들고 U()로 바꾼다."""
    mb = C.MeshBuilder()
    NX, NY, T = 20, 6, 0.0028

    def z_of(x, y):                              # 가운데가 뒤로 들어간 오목한 면
        return -0.011 * (1 - (x / POUCH_W) ** 2) - 0.003 * (1 - (y / POUCH_H) ** 2)

    F, B = [], []
    for i in range(NX + 1):
        x = -POUCH_W + 2 * POUCH_W * i / NX
        h = POUCH_H * (1 - 0.25 * (x / POUCH_W) ** 2)   # 끝으로 갈수록 좁아짐
        F.append([mb.v(C.U(x, -h + 2 * h * j / NY, z_of(x, -h + 2 * h * j / NY))) for j in range(NY + 1)])
        B.append([mb.v(C.U(x, -h + 2 * h * j / NY, z_of(x, -h + 2 * h * j / NY) - T)) for j in range(NY + 1)])
    for i in range(NX):
        for j in range(NY):
            mb.f([F[i][j], F[i + 1][j], F[i + 1][j + 1], F[i][j + 1]], "wood_dark")
            mb.f([B[i][j + 1], B[i + 1][j + 1], B[i + 1][j], B[i][j]], "wood_dark")
        for j in (0, NY):                        # 위아래 테두리는 진한 가죽 (바느질 느낌)
            mb.f([F[i][j], B[i][j], B[i + 1][j], F[i + 1][j]], "leather_dark")
    for i in (0, NX):
        for j in range(NY):
            mb.f([F[i][j], F[i][j + 1], B[i][j + 1], B[i][j]], "leather_dark")
    for sx in (-1, 1):                           # 고무줄 매듭: 주머니 끝을 세로로 감싼 짧은 관
        x = sx * (POUCH_W + 0.001)
        path = [Vector(C.U(x, -0.008 + 0.016 * i / 8, z_of(x, 0) - T / 2)) for i in range(9)]
        tube(mb, path, lambda s, a, p: 0.0036 + 0.0004 * math.cos(s * 6 * math.pi),
             lambda s, a, p: "band_latex", seg=12, ref=Vector((1, 0, 0)))
    obj = mb.build("Pouch", sharp_deg=60)
    C.add_empty("BandTie_L", obj, C.U(-(POUCH_W + 0.002), 0, -0.004))
    C.add_empty("BandTie_R", obj, C.U(POUCH_W + 0.002, 0, -0.004))
    C.add_empty("StoneSeat", obj, C.U(0, 0, -0.009))   # 오목면 가운데(-0.014)보다 조금 앞: 넓은 돌의 가장자리가 주머니를 뚫지 않게
    return obj


def band_between(mb, a, b):
    path = [a + (b - a) * (i / 12) for i in range(13)]
    tube(mb, path, lambda s, ang, p: BAND_R, lambda s, ang, p: "band_latex", seg=12,
         ref=Vector((0, 0, 1)) if abs((b - a).normalized().z) < 0.9 else Vector((1, 0, 0)))


if __name__ == "__main__":
    C.reset()
    C.make_palette_textures()
    sling = make_slingshot()
    pouch = make_pouch()
    mb = C.MeshBuilder()
    band_between(mb, Vector((0, 0, 0)), Vector(C.U(0, 0, 1)))
    band = mb.build("Band", sharp_deg=70)

    C.export_fbx(sling, "Slingshot.fbx")
    C.export_fbx(pouch, "Pouch.fbx")
    C.export_fbx(band, "Band.fbx")
    C.bpy.data.objects.remove(band)

    # 미리보기: 주머니가 갈래 아래로 늘어진 모습 + 고무줄 두 줄 + 돌멩이 하나 (내보낸 뒤라 FBX에는 영향 없음)
    rest = Vector(C.U(0, BAND_Z - HANG, -0.03))
    pouch.location = rest
    mb = C.MeshBuilder()
    for sx in (-1, 1):
        band_between(mb, Vector(C.U(sx * TIP_X, BAND_Z, -0.006)),
                     rest + Vector(C.U(sx * (POUCH_W + 0.002), 0, -0.004)))
    bands = mb.build("PreviewBands", sharp_deg=70)
    stone = stone_geo.build_stone("01_Flat")
    stone.rotation_euler = (1.5708, 0, 0)          # 납작한 면이 주머니를 향하게 (Unity에서는 프리팹이 같은 처리를 한다)
    stone.location = rest + Vector(C.U(0, 0, -0.009 + 0.008))
    try:
        C.bpy.context.scene.eevee.use_raytracing = True
    except Exception:
        pass
    C.render_previews([sling, pouch, bands, stone], "Slingshot",
                      [("hero", 145, 18), ("back", 180, 8), ("top", 160, 60)], ground=False, fill=1.0)

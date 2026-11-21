"""Blender 헤드리스 에셋 생성 공용 함수.

실행: blender -b --factory-startup -P Tools/AssetGen/make_xxx.py

좌표 규칙 (FBX 내보내기 설정 -Z Forward / Y Up / Apply Transform 기준)
    Blender -Y  ->  Unity +Z (앞)
    Blender +Z  ->  Unity +Y (위)
    Blender -X  ->  Unity +X (오른쪽)
Blender 정면도(Front view)에서 보이는 모습 = Unity에서 오브젝트의 +Z 앞면을 마주 본 모습.
"""
import math
import os

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
ART = os.path.join(ROOT, "Assets", "_Project", "Art")
MODELS = os.path.join(ART, "Models")
TEXTURES = os.path.join(ART, "Textures")
PREVIEWS = os.path.join(ROOT, "docs", "assets", "previews")
for _d in (MODELS, TEXTURES, PREVIEWS):
    os.makedirs(_d, exist_ok=True)

# ---------------------------------------------------------------------------
# 팔레트: 모든 소품이 256px 텍스처 1장을 공유한다 (16x16 칸, 칸당 16px).
# 이름: (색 hex, metallic, smoothness[, 발광 hex])  ※ 새 색은 항상 끝에 추가 (기존 UV 유지)
# ---------------------------------------------------------------------------
PALETTE = {
    "steel":        ("#C9CED6", 1.0, 0.85),
    "tungsten":     ("#565B64", 1.0, 0.62),
    "brass":        ("#C9A24C", 1.0, 0.72),
    "shaft_black":  ("#1B1D22", 0.0, 0.55),
    "flight_red":   ("#D3263B", 0.0, 0.35),
    "flight_white": ("#F0EEE9", 0.0, 0.35),
    "wood_light":   ("#A0703F", 0.0, 0.40),
    "wood_mid":     ("#7A4E2C", 0.0, 0.38),
    "wood_dark":    ("#4A2F1E", 0.0, 0.35),
    "felt_green":   ("#1E5A3A", 0.0, 0.08),
    "hole_dark":    ("#100C09", 0.0, 0.05),
    "metal_black":  ("#26282D", 0.9, 0.55),
    "board_black":  ("#141518", 0.0, 0.12),
    "wire_silver":  ("#BFC4CB", 1.0, 0.78),
    "rubber":       ("#202020", 0.0, 0.20),
    "cream":        ("#EADFC4", 0.0, 0.15),
    # --- 3단계: 방 환경 ---
    "wall_paint":   ("#24443A", 0.0, 0.10),
    "ceiling":      ("#2A2623", 0.0, 0.05),
    "floor_a":      ("#6E4628", 0.0, 0.42),
    "floor_b":      ("#5D3A20", 0.0, 0.42),
    "floor_c":      ("#7C5433", 0.0, 0.42),
    "floor_gap":    ("#150E09", 0.0, 0.10),
    "trim":         ("#36220F", 0.0, 0.45),
    "leather_red":  ("#7A1E24", 0.0, 0.45),
    "chalkboard":   ("#1F2824", 0.0, 0.05),
    "chalk":        ("#E6E4DC", 0.0, 0.05),
    "poster_red":   ("#B3242F", 0.0, 0.15),
    "poster_green": ("#1E6A43", 0.0, 0.15),
    "neon_pink":    ("#FF5AA5", 0.0, 0.60, "#FF2E88"),
    "neon_cyan":    ("#7FF3FF", 0.0, 0.60, "#2EE6FF"),
    "bulb":         ("#FFF1D6", 0.0, 0.60, "#FFD9A0"),
    "acrylic":      ("#0E0F12", 0.0, 0.90),
    # --- 4단계: 물풍선 (docs/decisions/003) ---
    "balloon_red":   ("#E8323C", 0.0, 0.72),
    "balloon_blue":  ("#2F7DE1", 0.0, 0.72),
    "balloon_green": ("#3DBE4E", 0.0, 0.72),
    "balloon_gold":  ("#F2B630", 0.85, 0.82, "#4A3000"),
    # --- 4단계: 통나무 받침대 ---
    "bark":         ("#5B4030", 0.0, 0.20),
    "bark_dark":    ("#3E2B20", 0.0, 0.15),
    "wood_cut":     ("#C99B63", 0.0, 0.30),
    "wood_ring":    ("#A8784A", 0.0, 0.30),
    # --- 4단계: 야외 여름 계곡 ---
    "pebble_a":     ("#A79E91", 0.0, 0.25),
    "pebble_b":     ("#8C8478", 0.0, 0.25),
    "pebble_c":     ("#BDB5A6", 0.0, 0.25),
    "riverbed":     ("#5E6B5E", 0.0, 0.30),
    "sand":         ("#C9B58E", 0.0, 0.15),
    "grass_a":      ("#5E9A3C", 0.0, 0.12),
    "grass_b":      ("#4C8433", 0.0, 0.12),
    "grass_c":      ("#6FAA45", 0.0, 0.12),
    "rock_a":       ("#7D7A72", 0.0, 0.20),
    "rock_b":       ("#66635C", 0.0, 0.20),
    "rock_moss":    ("#5F7046", 0.0, 0.15),
    "cliff":        ("#857F72", 0.0, 0.20),
    "water":        ("#3FA3A8", 0.0, 0.92),
    "leaf_a":       ("#3E7D32", 0.0, 0.15),
    "leaf_b":       ("#2F6A2C", 0.0, 0.15),
    "leaf_c":       ("#58963A", 0.0, 0.15),
    "trunk":        ("#5A4232", 0.0, 0.20),
    "mountain_a":   ("#6F9A8A", 0.0, 0.10),
    "mountain_b":   ("#86AEA0", 0.0, 0.10),
    # --- 5단계: 새총 (docs/decisions/008) ---
    "leather_dark": ("#4A1216", 0.0, 0.35),
    "band_latex":   ("#D99A3C", 0.0, 0.55),
    "wood_grain":   ("#8C5A30", 0.0, 0.38),
    "wood_knot":    ("#5E3A1E", 0.0, 0.30),
    # --- 5단계: 새총 돌멩이 탄환 ---
    "stone_white":  ("#D6D0C3", 0.0, 0.30),
    "stone_dark":   ("#4C4946", 0.0, 0.32),
    "stone_red":    ("#8E5B47", 0.0, 0.30),
    "stone_green":  ("#5E6D58", 0.0, 0.30),
    "stone_vein":   ("#EFECE4", 0.0, 0.40),
    "stone_speck":  ("#2C2A28", 0.0, 0.25),
}
GRID = 16
PAL_SIZE = 256
_NAMES = list(PALETTE.keys())


def palette_uv(name):
    i = _NAMES.index(name)
    col, row = i % GRID, i // GRID          # row 0 = 이미지 아래쪽
    return ((col + 0.5) / GRID, (row + 0.5) / GRID)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[k:k + 2], 16) / 255.0 for k in (0, 2, 4))


def make_palette_textures():
    """T_Palette_Albedo (sRGB) + T_Palette_MS (R=Metallic, A=Smoothness, Linear)
    + T_Palette_Emission (sRGB, 발광 칸만 색, 나머지 검정)."""
    cell = PAL_SIZE // GRID
    alb = [0.0] * (PAL_SIZE * PAL_SIZE * 4)
    ms = [0.0] * (PAL_SIZE * PAL_SIZE * 4)
    emi = [0.0] * (PAL_SIZE * PAL_SIZE * 4)
    for i in range(PAL_SIZE * PAL_SIZE):          # 빈 칸 기본값
        alb[i * 4:i * 4 + 4] = (1.0, 0.0, 1.0, 1.0)
        ms[i * 4:i * 4 + 4] = (0.0, 0.0, 0.0, 0.5)
        emi[i * 4 + 3] = 1.0
    for idx, name in enumerate(_NAMES):
        hexc, metal, smooth = PALETTE[name][:3]
        r, g, b = hex_rgb(hexc)
        er, eg, eb = hex_rgb(PALETTE[name][3]) if len(PALETTE[name]) > 3 else (0.0, 0.0, 0.0)
        col, row = idx % GRID, idx // GRID
        for y in range(row * cell, (row + 1) * cell):
            for x in range(col * cell, (col + 1) * cell):
                p = (y * PAL_SIZE + x) * 4
                alb[p:p + 4] = (r, g, b, 1.0)
                ms[p:p + 4] = (metal, 0.0, 0.0, smooth)
                emi[p:p + 4] = (er, eg, eb, 1.0)
    paths = {}
    for nm, px, cs in (("T_Palette_Albedo", alb, "sRGB"), ("T_Palette_MS", ms, "Non-Color"),
                       ("T_Palette_Emission", emi, "sRGB")):
        img = bpy.data.images.new(nm, PAL_SIZE, PAL_SIZE, alpha=True)
        img.colorspace_settings.name = cs
        img.alpha_mode = "STRAIGHT"
        img.pixels.foreach_set(px)
        path = os.path.join(TEXTURES, nm + ".png")
        img.filepath_raw = path
        img.file_format = "PNG"
        img.save()
        paths[nm] = path
    return paths


# ---------------------------------------------------------------------------
# 씬 정리
# ---------------------------------------------------------------------------
def reset():
    for coll in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.images,
                 bpy.data.lights, bpy.data.cameras, bpy.data.curves, bpy.data.worlds):
        for item in list(coll):
            coll.remove(item)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0


# ---------------------------------------------------------------------------
# 메시 빌더
# ---------------------------------------------------------------------------
class MeshBuilder:
    """면마다 팔레트 이름(str) 또는 ('mat', uv_func) 지정."""

    def __init__(self):
        self.verts = []
        self.faces = []

    def v(self, co):
        self.verts.append(Vector(co))
        return len(self.verts) - 1

    def f(self, idx, sw):
        self.faces.append((list(idx), sw))

    def build(self, name, materials=("M_Palette",), sharp_deg=35.0, recalc=True):
        bm = bmesh.new()
        bv = [bm.verts.new(c) for c in self.verts]
        bm.verts.ensure_lookup_table()
        uv = bm.loops.layers.uv.new("UVMap")
        for idx, sw in self.faces:
            try:
                face = bm.faces.new([bv[i] for i in idx])
            except ValueError:
                continue                      # 중복 면 무시
            if isinstance(sw, str):
                face.material_index = 0
                u = palette_uv(sw)
                for lp in face.loops:
                    lp[uv].uv = u
            else:
                mat_name, fn = sw
                face.material_index = list(materials).index(mat_name)
                for lp in face.loops:
                    lp[uv].uv = fn(lp.vert.co)
        if recalc:
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        mark_sharp(bm, sharp_deg)
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        finish_mesh(me)
        obj = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(obj)
        for m in materials:
            obj.data.materials.append(get_material(m))
        return obj


def mark_sharp(bm, deg):
    thr = math.radians(deg)
    for e in bm.edges:
        if len(e.link_faces) == 2:
            e.smooth = e.calc_face_angle(0.0) <= thr
        else:
            e.smooth = False
    for fc in bm.faces:
        fc.smooth = True


def finish_mesh(me):
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.update()


def axis_point(axis, t, r, a, c=(0, 0, 0)):
    ca, sa = math.cos(a) * r, math.sin(a) * r
    if axis == "Y":
        p = (ca, t, sa)
    elif axis == "Z":
        p = (ca, sa, t)
    else:
        p = (t, ca, sa)
    return (p[0] + c[0], p[1] + c[1], p[2] + c[2])


def lathe(mb, prof, seg=16, axis="Y", c=(0, 0, 0), phase=0.0, closed=False):
    """prof: [(t, r, swatch)] — swatch는 이 점에서 다음 점까지 구간의 색.
    closed=True면 단면이 닫힌 고리(와이어 링 등) — 뚜껑 없이 마지막 점을 첫 점에 잇는다."""
    angs = [phase + 2 * math.pi * k / seg for k in range(seg)]
    rings = []
    for t, r, _ in prof:
        if r <= 1e-7:
            rings.append([mb.v(axis_point(axis, t, 0, 0, c))])
        else:
            rings.append([mb.v(axis_point(axis, t, r, a, c)) for a in angs])
    n = len(prof)
    for i in range(n if closed else n - 1):
        A, B, sw = rings[i], rings[(i + 1) % n], prof[i][2]
        if len(A) == 1 and len(B) == 1:
            continue
        for k in range(seg):
            k2 = (k + 1) % seg
            if len(A) == 1:
                mb.f([A[0], B[k], B[k2]], sw)
            elif len(B) == 1:
                mb.f([A[k], A[k2], B[0]], sw)
            else:
                mb.f([A[k], A[k2], B[k2], B[k]], sw)
    if closed:
        return
    if len(rings[0]) > 1:
        mb.f(rings[0][::-1], prof[0][2])
    if len(rings[-1]) > 1:
        mb.f(rings[-1], prof[-2][2])


def round_profile(pts, rad, seg=3):
    """(t, r, sw) 폴리라인의 안쪽 꼭짓점을 둥글게(베벨). 양 끝점은 그대로."""
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        P = Vector(pts[i][:2])
        A = Vector(pts[i - 1][:2])
        B = Vector(pts[i + 1][:2])
        la, lb = (A - P).length, (B - P).length
        rr = min(rad, la * 0.45, lb * 0.45)
        if rr < 1e-6:
            out.append(pts[i])
            continue
        T1 = P + (A - P).normalized() * rr
        T2 = P + (B - P).normalized() * rr
        for k in range(seg + 1):
            s = k / seg
            q = T1 * (1 - s) ** 2 + P * 2 * (1 - s) * s + T2 * s * s
            sw = pts[i - 1][2] if k < seg else pts[i][2]
            out.append((q.x, q.y, sw))
    out.append(pts[-1])
    return out


def prism(mb, poly2d, z0, z1, sw, to3d):
    """2D 다각형을 두께 방향으로 돌출. to3d(x, y, z) -> 3D 좌표."""
    n = len(poly2d)
    bot = [mb.v(to3d(x, y, z0)) for x, y in poly2d]
    top = [mb.v(to3d(x, y, z1)) for x, y in poly2d]
    mb.f(bot[::-1], sw)
    mb.f(top, sw)
    for i in range(n):
        j = (i + 1) % n
        mb.f([bot[i], bot[j], top[j], top[i]], sw)


def box(mb, cmin, cmax, sw):
    x0, y0, z0 = cmin
    x1, y1, z1 = cmax
    prism(mb, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, sw, lambda x, y, z: (x, y, z))


def U(x, y, z):
    """Unity 좌표(m) -> Blender 좌표. (Unity +X 오른쪽, +Y 위, +Z 앞)"""
    return (-x, -z, y)


def ubox(mb, a, b, sw):
    """Unity 좌표 두 꼭짓점으로 박스."""
    pa, pb = U(*a), U(*b)
    box(mb, tuple(min(pa[i], pb[i]) for i in range(3)),
        tuple(max(pa[i], pb[i]) for i in range(3)), sw)


def bevel_all(obj, offset, segments=1, sharp_deg=40):
    """모든 모서리를 살짝 깎아 하이라이트가 생기게 한다 (박스로 만든 물체용)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=offset, segments=segments,
                    profile=0.5, affect="EDGES", clamp_overlap=True)
    mark_sharp(bm, sharp_deg)
    bm.to_mesh(obj.data)
    bm.free()
    finish_mesh(obj.data)


def add_mesh_data(mb, me, sw, xform):
    """다른 메시(예: 글자)를 MeshBuilder에 합친다. xform(co) -> 새 좌표."""
    base = len(mb.verts)
    for v in me.vertices:
        mb.v(xform(v.co))
    for p in me.polygons:
        mb.f([base + i for i in p.vertices], sw)


def text_mesh(body, size, extrude, offset=0.0, align="CENTER"):
    cu = bpy.data.curves.new("T_" + body, "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.offset = offset
    cu.align_x, cu.align_y = align, "CENTER"
    ob = bpy.data.objects.new("T_" + body, cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    return me


def add_empty(name, parent, loc):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = "ARROWS"
    e.empty_display_size = 0.02
    bpy.context.scene.collection.objects.link(e)
    e.parent = parent
    e.location = loc
    return e


# ---------------------------------------------------------------------------
# 머티리얼 (Blender 미리보기용. Unity에서는 URP Lit로 다시 만든다)
# ---------------------------------------------------------------------------
def _load_image(path, colorspace):
    nm = os.path.basename(path)
    img = bpy.data.images.get(nm) or bpy.data.images.load(path)
    img.colorspace_settings.name = colorspace
    return img


def get_material(name):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    if name == "M_Palette":
        _textured(mat, os.path.join(TEXTURES, "T_Palette_Albedo.png"),
                  os.path.join(TEXTURES, "T_Palette_MS.png"), "Closest",
                  emi_path=os.path.join(TEXTURES, "T_Palette_Emission.png"))
    return mat


def _textured(mat, alb_path, ms_path, interp, roughness=0.5, emi_path=None):
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    t_alb = nt.nodes.new("ShaderNodeTexImage")
    t_alb.image = _load_image(alb_path, "sRGB")
    t_alb.interpolation = interp
    nt.links.new(t_alb.outputs["Color"], bsdf.inputs["Base Color"])
    if ms_path:
        t_ms = nt.nodes.new("ShaderNodeTexImage")
        t_ms.image = _load_image(ms_path, "Non-Color")
        t_ms.interpolation = interp
        sep = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(t_ms.outputs["Color"], sep.inputs["Color"])
        nt.links.new(sep.outputs[0], bsdf.inputs["Metallic"])
        inv = nt.nodes.new("ShaderNodeMath")
        inv.operation = "SUBTRACT"
        inv.inputs[0].default_value = 1.0
        nt.links.new(t_ms.outputs["Alpha"], inv.inputs[1])
        nt.links.new(inv.outputs[0], bsdf.inputs["Roughness"])
    else:
        bsdf.inputs["Metallic"].default_value = 0.0
        bsdf.inputs["Roughness"].default_value = roughness
    if emi_path and os.path.exists(emi_path):
        t_e = nt.nodes.new("ShaderNodeTexImage")
        t_e.image = _load_image(emi_path, "sRGB")
        t_e.interpolation = interp
        nt.links.new(t_e.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 4.0


# ---------------------------------------------------------------------------
# 내보내기 / 미리보기
# ---------------------------------------------------------------------------
def export_fbx(root, filename):
    bpy.ops.object.select_all(action="DESELECT")
    objs = [root] + list(root.children_recursive)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = root
    path = os.path.join(MODELS, filename)
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True, object_types={"MESH", "EMPTY"},
        apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL",
        axis_forward="-Z", axis_up="Y", bake_space_transform=True,
        mesh_smooth_type="OFF", use_tspace=False, add_leaf_bones=False,
        path_mode="STRIP", embed_textures=False, use_custom_props=False)
    tris = sum(len(p.vertices) - 2 for o in objs if o.type == "MESH" for p in o.data.polygons)
    print(f"[export] {path}  tris={tris}")
    return path


def _bbox(objs):
    bpy.context.view_layer.update()          # 방금 옮긴 오브젝트의 matrix_world 갱신
    pts =[o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


def render_previews(objs, name, views, res=(1400, 1000), ground=True, fill=1.0):
    """views: [(label, azimuth_deg, elevation_deg)] — azimuth 0 = Blender 정면(-Y 쪽에서 봄)."""
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = False
    try:
        sc.eevee.taa_render_samples = 64
    except Exception:
        pass
    try:
        sc.view_settings.view_transform = "Standard"   # Unity URP 기본(톤매핑 없음)과 비슷하게
    except Exception:
        pass
    world = bpy.data.worlds.new("W")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.20, 0.215, 0.24, 1)
    bg.inputs["Strength"].default_value = 0.35
    sc.world = world

    mn, mx = _bbox(objs)
    ctr = (mn + mx) / 2
    radius = (mx - mn).length / 2

    if ground:
        gme = bpy.data.meshes.new("Ground")
        s = radius * 30
        gme.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
        g = bpy.data.objects.new("Ground", gme)
        g.location.z = mn.z
        gm = bpy.data.materials.new("GroundMat")
        gm.use_nodes = True
        b = gm.node_tree.nodes.get("Principled BSDF")
        b.inputs["Base Color"].default_value = (0.10, 0.11, 0.12, 1)
        b.inputs["Roughness"].default_value = 0.8
        gme.materials.append(gm)
        sc.collection.objects.link(g)

    def light(nm, kind, energy, direction, size=1.0):
        ld = bpy.data.lights.new(nm, kind)
        ld.energy = energy
        if kind == "AREA":
            ld.size = size
        if kind == "SUN":
            ld.angle = math.radians(8)
        lo = bpy.data.objects.new(nm, ld)
        d = Vector(direction).normalized()
        lo.location = ctr + d * radius * 6
        lo.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(lo)
        return lo

    light("Key", "SUN", 1.6, (-0.6, -0.8, 0.9))
    light("Fill", "AREA", 12.0 * radius * radius * 36, (0.9, -0.4, 0.3), size=radius * 4)
    light("Rim", "AREA", 25.0 * radius * radius * 36, (0.3, 1.0, 0.6), size=radius * 3)

    cam_d = bpy.data.cameras.new("Cam")
    cam_d.lens = 70
    cam = bpy.data.objects.new("Cam", cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam
    fov_h = 2 * math.atan(cam_d.sensor_width / 2 / cam_d.lens)
    fov_v = 2 * math.atan(math.tan(fov_h / 2) * res[1] / res[0])
    dist = radius / math.sin(fov_v / 2) * fill

    out = []
    for label, az, el in views:
        a, e = math.radians(az), math.radians(el)
        d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
        cam.location = ctr + d * dist
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        path = os.path.join(PREVIEWS, f"{name}_{label}.png")
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        out.append(path)
        print(f"[preview] {path}")
    return out

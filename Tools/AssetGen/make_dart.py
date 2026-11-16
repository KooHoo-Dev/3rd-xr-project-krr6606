"""다트 (Dart.fbx) — 길이 16 cm, 피벗 = 촉 끝, 촉 방향 = Unity +Z.

Blender에서는 촉이 원점, 몸통이 +Y 쪽으로 뻗는다 (Blender -Y = Unity +Z).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
from dart_geo import build_dart  # noqa: E402

C.reset()
C.make_palette_textures()
dart = build_dart()
# 잡는 위치: 배럴 중앙 (촉에서 5.8 cm 뒤)
C.add_empty("GrabPoint", dart, (0, 0.058, 0))

C.export_fbx(dart, "Dart.fbx")
C.render_previews([dart], "Dart", [("hero", 35, 25), ("side", 90, 0)],
                  ground=False, fill=0.85)

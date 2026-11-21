"""새총 탄환 돌멩이 10종 (Stone_01_Flat.fbx ~ Stone_10_Vein.fbx) + 한데 모은 미리보기.

형상 · 색은 stone_geo.py의 STONES 표. 재질은 공용 팔레트(M_Palette).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import stone_geo  # noqa: E402

C.reset()
C.make_palette_textures()          # 돌멩이 색을 팔레트 끝에 추가했으므로 텍스처를 다시 쓴다
stones = []
for i, s in enumerate(stone_geo.STONES):
    obj = stone_geo.build_stone(s[0])
    C.export_fbx(obj, obj.name + ".fbx")
    obj.location = (-(i % 5) * 0.07, (i // 5) * 0.075, 0)   # 5개씩 두 줄
    obj.rotation_euler = (0.35, 0.0, 0.5 * i)
    stones.append(obj)

C.render_previews(stones, "Stones", [("hero", 0, 35), ("low", 20, 12)], ground=True, fill=0.75)

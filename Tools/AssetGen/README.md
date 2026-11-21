# AssetGen — Blender 스크립트로 에셋 생성

AI(Claude)가 작성한 생성 스크립트입니다 (`AI-Assist: generated`). 결과물은 `Assets/_Project/Art/`, 미리보기는 `docs/assets/previews/`에 저장됩니다.
실내 다트 바 · 다트판 · 바 테이블 생성 코드는 기획 전환으로 삭제했습니다 ([decisions/003](../../docs/decisions/003-계곡-환경-제작-방식과-실내-에셋-정리.md)). 다트 · 다트통 생성 코드도 새총 전환으로 삭제했습니다 ([decisions/008](../../docs/decisions/008-새총-기획-전환.md)).

## 실행 (Blender 5.2, 프로젝트 루트에서)
```bash
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P Tools/AssetGen/make_props.py
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P Tools/AssetGen/make_base.py
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P Tools/AssetGen/make_balloons.py
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P Tools/AssetGen/make_valley.py
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P Tools/AssetGen/make_scene_preview.py
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P Tools/AssetGen/make_slingshot.py
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P Tools/AssetGen/make_stones.py
```
팔레트 텍스처는 `make_base.py`, `make_stones.py`, `make_balloons.py`, `make_valley.py`가 매번 같은 내용으로 다시 씁니다. 팔레트에 새 색을 넣을 때는 **항상 끝에 추가**(기존 UV 유지).
`make_valley.py`는 난수 시드가 고정되어 있어 실행할 때마다 같은 지형이 나옵니다.

| 파일 | 역할 |
| --- | --- |
| `common.py` | 팔레트, 메시 빌더, 회전체(lathe), FBX 내보내기, 미리보기 렌더 |
| `make_props.py` | LogStand.fbx (통나무 받침대, 윗면 1.0 m) |
| `make_base.py` | 쏘는 선 ShootingLine.fbx + UI 스프라이트 2종 + 팔레트(발광 포함) |
| `make_balloons.py` | Balloon_Red/Blue/Green/Gold.fbx (피벗 = 몸통 중심) |
| `make_valley.py` | Valley.fbx — 자식 Ground · Water · Rocks · Trees · Mountains |
| `make_sfx.py` | 피드백 사운드 `Audio/SFX_*.wav` 7종 합성. **Blender 없이** `python Tools/AssetGen/make_sfx.py` |
| `make_fx_textures.py` | 파티클 텍스처 `T_FX_*.png` 4장. **Blender 없이** `python Tools/AssetGen/make_fx_textures.py`. 프리팹은 Unity 메뉴 Tools > Stone Challenge > Build VFX Prefabs (`VfxBuilder.cs`) |
| `layout.py` | 데모 씬 배치표 (Unity 좌표) — `DemoSceneBuilder.cs`와 같은 값 |
| `make_slingshot.py` | Slingshot.fbx (피벗 = 손잡이 가운데, 자식 GripAttach · BandAnchor_L/R · RestPoint), Pouch.fbx (자식 BandTie_L/R · StoneSeat), Band.fbx (길이 1 m 고무줄, Z 스케일로 늘림) — [decisions/008](../../docs/decisions/008-새총-기획-전환.md) |
| `stone_geo.py` · `make_stones.py` | 새총 탄환 돌멩이 Stone_01_Flat ~ Stone_10_Vein.fbx (모양 10종, 피벗 = 중심). 모양 · 색 · 무늬는 `stone_geo.STONES` 표, 재질은 M_Palette |
| `make_scene_preview.py` | 배치표대로 전체 씬을 Blender에서 미리 렌더 (Scene_player / behind / valley) |

## 자주 바꿀 값
- 색·금속도: `common.py`의 `PALETTE`
- 풍선 지름 · 색: `make_balloons.py`의 `BALLOONS`
- 지형 모양: `make_valley.py`의 `height()` (언덕 경사, 시냇물 위치 `stream_center()`), 면 색은 `zone_color()`
- 나무 · 바위 위치: `make_valley.py`의 `build_trees()`, `build_rocks()`

FBX 축 설정: -Z Forward / Y Up / Apply Transform → Unity에서 회전 (0,0,0), +Z가 앞.

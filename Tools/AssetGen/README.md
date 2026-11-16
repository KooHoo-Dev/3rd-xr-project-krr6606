# AssetGen — Blender 스크립트로 에셋 생성

AI(Claude)가 작성한 생성 스크립트입니다 (`AI-Assist: generated`). 결과물은 `Assets/_Project/Art/`, 미리보기는 `docs/assets/previews/`에 저장됩니다.

## 실행 (Blender 5.2, 프로젝트 루트에서)
```bash
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P Tools/AssetGen/make_dart.py
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P Tools/AssetGen/make_dartboard.py
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P Tools/AssetGen/make_props.py
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P Tools/AssetGen/make_room.py
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P Tools/AssetGen/make_scene_preview.py
```
`make_dart.py`, `make_room.py`가 팔레트 텍스처를 만들기 때문에 이 순서로 실행합니다. 팔레트에 새 색을 넣을 때는 **항상 끝에 추가**(기존 UV 유지).

| 파일 | 역할 |
| --- | --- |
| `common.py` | 팔레트, 메시 빌더, 회전체(lathe), FBX 내보내기, 미리보기 렌더 |
| `dart_geo.py` | 다트 형상 (다트통 미리보기에서도 사용) |
| `make_dart.py` | Dart.fbx + 팔레트 텍스처 |
| `make_dartboard.py` | 다트판 텍스처(2D 배치를 정사영 렌더) + Dartboard.fbx |
| `make_props.py` | DartHolder.fbx, BarTable.fbx |
| `make_room.py` | 방 환경 FBX 9종 + UI 스프라이트 2종 + 팔레트(발광 포함) |
| `layout.py` | 데모 씬 배치표 (Unity 좌표) — `DemoSceneBuilder.cs`와 같은 값 |
| `make_scene_preview.py` | 배치표대로 전체 씬을 Blender에서 미리 렌더 |

## 자주 바꿀 값
- 색·금속도: `common.py`의 `PALETTE`
- 다트 치수: `dart_geo.py`의 `prof`, `FIN_*`
- 다트판 링 반지름·숫자 순서: `make_dartboard.py` 위쪽 상수 (점수 코드와 같은 값을 써야 함)
- 다트통 구멍 위치·개수: `make_props.py`의 `SLOT_*`

FBX 축 설정: -Z Forward / Y Up / Apply Transform → Unity에서 회전 (0,0,0), +Z가 앞.

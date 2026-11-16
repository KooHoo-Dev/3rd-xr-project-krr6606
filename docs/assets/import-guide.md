# 1단계 에셋 — Unity 임포트 가이드

AI가 생성한 파일을 **사용자가 에디터에서** 설정하는 순서입니다. (CLAUDE.md 6장: 에디터 조작은 사용자가)

## 0. 생성된 파일
| 파일 | 내용 | tris |
| --- | --- | --- |
| `Assets/_Project/Art/Models/Dart.fbx` | 다트, 자식 `GrabPoint` | 1,856 |
| `Assets/_Project/Art/Models/Dartboard.fbx` | 다트판 + 와이어 (머티리얼 2개) | 7,968 |
| `Assets/_Project/Art/Models/DartHolder.fbx` | 다트통, 자식 `Slot_01~07` | 3,610 |
| `Assets/_Project/Art/Models/BarTable.fbx` | 바 테이블 (윗면 높이 1.0 m) | 4,224 |
| `Assets/_Project/Art/Textures/T_Palette_Albedo.png` | 공용 색 팔레트 256px | |
| `Assets/_Project/Art/Textures/T_Palette_MS.png` | 공용 금속도(R)·매끈함(A) | |
| `Assets/_Project/Art/Textures/T_Dartboard_Albedo.png` | 다트판 면 2048px | |

다트 7개를 포함해도 약 29k tris로, Quest 예산(~100k)의 30% 정도입니다.
미리보기: [previews/](previews/) · 다시 생성: `Tools/AssetGen/README.md`

## 1. 텍스처 설정 (Project 창에서 파일 선택 → Inspector → Apply)
| 텍스처 | sRGB | Filter Mode | Generate Mip Maps | 그 외 |
| --- | --- | --- | --- | --- |
| T_Palette_Albedo | ✅ | **Point** | ❌ 끔 | Compression: None |
| T_Palette_MS | ❌ **끔** | **Point** | ❌ 끔 | Compression: None |
| T_Dartboard_Albedo | ✅ | Bilinear | ✅ | Aniso Level 4, Max Size 2048 |

> 팔레트는 16px 색 칸이 붙어 있어서, 밉맵이나 보간을 켜면 옆 칸 색이 번질 수 있어요.

## 2. 머티리얼 만들기 (`Assets/_Project/Art/Materials/`)
Project 창 우클릭 → Create → Material → Shader `Universal Render Pipeline/Lit`
- **M_Palette**: Base Map = `T_Palette_Albedo`, Metallic Map = `T_Palette_MS`, Smoothness Source = `Metallic Alpha`, Smoothness 슬라이더 = 1
- **M_Dartboard**: Base Map = `T_Dartboard_Albedo`, Metallic 0, Smoothness 0.1

이름을 정확히 이렇게 지어야 다음 단계의 자동 연결이 됩니다.

## 3. FBX 임포트 설정 (FBX 4개 각각)
- **Model 탭**: Scale Factor 1, Convert Units ✅, Generate Colliders ❌ → Apply
- **Rig 탭**: Animation Type `None` → Apply
- **Animation 탭**: Import Animation ❌ → Apply
- **Materials 탭**: Location `Use Embedded Materials` 그대로 → 아래 **On Demand Remap**에서
  Naming `From Model's Material`, Search `Project-Wide` → `Search and Remap…` 클릭
  → Remapped Materials 목록에 `M_Palette`(다트판은 `M_Dartboard`도)가 연결됐는지 확인 → Apply

## 4. 씬에 놓고 확인할 것 (5분)
| 확인 | 기대 결과 |
| --- | --- |
| Dart를 씬에 드래그 | Scale (1,1,1), 1 m 큐브 옆에서 손가락 길이 정도. **파란 화살표(Z)가 촉 방향**, 피벗이 촉 끝 |
| Dart의 `GrabPoint` | Position (0, 0, -0.058), Rotation (0,0,0) — 배럴 가운데 |
| Dartboard를 (0, 1.73, 2.0)에 | 회전 0으로 두면 **앞면이 플레이어(원점) 쪽**, 20이 위, 1이 오른쪽 |
| BarTable을 (0.45, 0, 0.3)에, DartHolder를 그 위 (0.45, 1.0, 0.3)에 | 다트통이 테이블 위에 딱 붙음 |
| DartHolder의 `Slot_01` | Rotation (90, 0, 0), **파란 화살표가 아래**. 다트를 Slot 위치·회전에 맞추면 구멍에 꽂힘 |

하나라도 다르면 스크린샷이나 Inspector 값을 알려주세요. 스크립트 쪽에서 고칩니다.

## 5. 콜라이더는 나중에 (참고값만)
콜라이더 · Rigidbody는 잡기·던지기를 구현할 때 같이 정합니다. 그때 쓸 수 있는 크기만 적어둡니다.
- 다트: 촉~배럴을 덮는 얇은 캡슐 (반지름 약 0.004, 길이 약 0.09, 방향 Z)
- 다트판: 박스 (0.451, 0.451, 0.038), 중심 (0, 0, 0.019) — 판 앞면이 z = 0
- 다트판 규칙 수치: [decisions/001](../decisions/001-아트-스타일과-다트판-규칙.md)

# 에셋 임포트 가이드

`Tools/AssetGen/`으로 만든 FBX · PNG를 Unity에 들이는 설정입니다.
**1~3번은 데모 씬 빌더(Tools > Dart Challenge > Build Demo Scene)가 자동으로 합니다.** 손으로 다시 맞춰야 할 때만 보세요.
에셋 목록 · 사양: [planning/asset-plan.md](../planning/asset-plan.md) · 미리보기: [previews/](previews/)

## 1. 텍스처 설정 (Project 창에서 파일 선택 → Inspector → Apply)
| 텍스처 | sRGB | Filter Mode | Generate Mip Maps | 그 외 |
| --- | --- | --- | --- | --- |
| T_Palette_Albedo | ✅ | **Point** | ❌ 끔 | Compression: None |
| T_Palette_MS | ❌ **끔** | **Point** | ❌ 끔 | Compression: None |

> 팔레트는 16px 색 칸이 붙어 있어서, 밉맵이나 보간을 켜면 옆 칸 색이 번질 수 있어요.

## 2. 머티리얼 (`Assets/_Project/Art/Materials/`)
- **M_Palette** (Shader `Universal Render Pipeline/Lit`): Base Map = `T_Palette_Albedo`, Metallic Map = `T_Palette_MS`, Smoothness Source = `Metallic Alpha`, Smoothness 슬라이더 = 1, Emission Map = `T_Palette_Emission`

이름이 정확히 `M_Palette`여야 다음 단계의 자동 연결이 됩니다.

## 3. FBX 임포트 설정 (FBX마다)
- **Model 탭**: Scale Factor 1, Convert Units ✅, Generate Colliders ❌ → Apply
- **Rig 탭**: Animation Type `None` → Apply
- **Animation 탭**: Import Animation ❌ → Apply
- **Materials 탭**: Location `Use Embedded Materials` 그대로 → 아래 **On Demand Remap**에서
  Naming `From Model's Material`, Search `Project-Wide` → `Search and Remap…` 클릭
  → Remapped Materials 목록에 `M_Palette`가 연결됐는지 확인 → Apply

## 4. 씬에 놓고 확인할 것
| 확인 | 기대 결과 |
| --- | --- |
| Dart를 씬에 드래그 | Scale (1,1,1), 1 m 큐브 옆에서 손가락 길이 정도. **파란 화살표(Z)가 촉 방향**, 피벗이 촉 끝 |
| Dart의 `GrabPoint` | Position (0, 0, -0.058), Rotation (0,0,0) — 배럴 가운데 |
| DartHolder의 `Slot_01` | Rotation (90, 0, 0), **파란 화살표가 아래**. 다트를 Slot 위치·회전에 맞추면 구멍에 꽂힘 |

씬 전체 배치 확인은 [demo-scene.md](demo-scene.md)의 "확인할 것" 표를 봅니다.

## 5. 콜라이더 참고값
- 다트: 촉~배럴을 덮는 얇은 캡슐 (반지름 약 0.004, 길이 약 0.09, 방향 Z)
- 풍선: SphereCollider, 반지름 = 지름 / 2, 중심 0 (피벗이 몸통 중심)

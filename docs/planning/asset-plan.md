# 에셋 제작 계획

결정 근거: [decisions/001](../decisions/001-아트-스타일과-다트판-규칙.md) — 깔끔한 로우폴리 + Blender 스크립트 생성
기획 전환: [decisions/002](../decisions/002-물풍선-기획-전환.md) — 다트판 → 물풍선, 환경 → 야외 여름 계곡 (2026-11-16)

## 역할 분담  #AI리더십
| 작업 | 사람 | AI |
| --- | --- | --- |
| 사양(치수·규칙) 결정 | ✅ | 선택지 제시 |
| 소품 모델·텍스처 생성 (`Tools/AssetGen/`) | | ✅ (AI-Assist: generated) |
| 미리보기 렌더 검토 → 통과/수정 요청 | ✅ | 수정 반영 |
| 야외 여름 계곡 환경 | ✅ (다른 컴퓨터에서 제작해 적용) | |
| Unity 임포트 · 머티리얼 · 프리팹 · 콜라이더 · XRI 설정 | ✅ | 단계별 안내 |

## 공통 규칙 (Quest)
- 씬 전체 ~100k tris, Draw Call ~100 이하, 1 unit = 1 m
- 소품은 **팔레트 텍스처 1장**(`T_Palette_*`, 256px)을 공유 → 머티리얼 1개(`M_Palette`)
- FBX는 Unity 기준 +Z 앞, +Y 위로 내보냄. 생성 스크립트는 `Tools/AssetGen/`, 결과물은 `Assets/_Project/Art/`

## 목록
| 단계 | 에셋 | 사양 | 상태 |
| --- | --- | --- | --- |
| 1 | 다트 `Dart.fbx` | 길이 16 cm, **피벗 = 촉 끝**, +Z = 촉 방향, 자식 `GrabPoint` | 생성됨 · 계속 사용 |
| 1 | 다트통 `DartHolder.fbx` | 나무 블록, 구멍 7개, 자식 `Slot_01~07` | 생성됨 · 계속 사용 |
| 1 | 바 테이블 `BarTable.fbx` | 높이 1.0 m, 다트통 받침 | 생성됨 · 계곡에 어울리는지 확인 |
| 1 | 다트판 `Dartboard.fbx` | 일반 다트판 | **사용 안 함** (002) |
| 2 | 점수판 · 시작/결과 패널 · 버튼 스프라이트 | World Space Canvas, 9-slice (`UI_RoundedRect`, `UI_Circle`) | 생성됨 · 문구를 물풍선 규칙(60초, 목표 점수)으로 바꿔야 함 |
| 3 | 실내 다트 바 (방 · 백보드 · 네온 · 칠판 · 포스터 · 의자 · 조명) | `make_room.py` | **계곡 환경이 들어오기 전까지 테스트용** |
| 3 | 야외 여름 계곡 | 사용자가 다른 컴퓨터에서 제작 | 예정 |
| 4 | 물풍선 4종 (빨강 35 / 파랑 28 / 초록 22 / 금빛 12 cm) | 매듭 포함 | 예정 |
| 4 | 물 효과 | 터짐 튐, 올 클리어 물 쏟아짐, 바닥 물보라, 금빛 반짝이, 점수 팝업 | 예정 |
| 4 | 사운드 | 팡(콤보는 높이만 변경), 팡파르, 금빛 팡 + 동전 소리, 풍선 떠오름 | 예정 |

임포트 방법: [assets/import-guide.md](../assets/import-guide.md) (데모 씬 빌더가 1~3번을 자동으로 함)

## 배치 기준 (현재 데모 씬)
- 배치표: `Tools/AssetGen/layout.py` = `Assets/_Project/Editor/DemoSceneBuilder.cs` (같은 값 유지)
- 던지는 선: z 0 / XR Origin: (0, 0, -0.25), +Z를 바라봄
- 다트통 테이블: 플레이어 오른쪽 (0.55, 0, -0.1), 다트통 윗면 높이 약 1.07 m
- 풍선 거리: 던지는 선에서 1.2 ~ 2.0 m ([concept.md](concept.md) 5장)
- 데모 씬: [assets/demo-scene.md](../assets/demo-scene.md)

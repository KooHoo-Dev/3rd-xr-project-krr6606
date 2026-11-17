# 에셋 제작 계획

결정 근거: [decisions/001](../decisions/001-아트-스타일과-다트판-규칙.md) — 깔끔한 로우폴리 + Blender 스크립트 생성
기획 전환: [decisions/002](../decisions/002-물풍선-기획-전환.md) — 다트판 → 물풍선, 환경 → 야외 여름 계곡 (2026-11-16)
계곡 제작 방식 · 실내 에셋 삭제: [decisions/003](../decisions/003-계곡-환경-제작-방식과-실내-에셋-정리.md) (2026-11-16)

## 역할 분담  #AI리더십
| 작업 | 사람 | AI |
| --- | --- | --- |
| 사양(치수·규칙) 결정 | ✅ | 선택지 제시 |
| 소품 모델·텍스처 생성 (`Tools/AssetGen/`) | | ✅ (AI-Assist: generated) |
| 미리보기 렌더 검토 → 통과/수정 요청 | ✅ | 수정 반영 |
| 야외 여름 계곡 환경 생성 (`Tools/AssetGen/`) | 검토 → 통과/수정 요청 | ✅ (AI-Assist: generated, 003) |
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
| 1 | 통나무 받침대 `LogStand.fbx` | 윗면 높이 1.0 m, 피벗 = 바닥 중심, 480 tris | 생성됨 · 사용자 검토 대기 |
| 2 | 점수판 · 시작/결과 패널 · 버튼 스프라이트 | World Space Canvas, 9-slice (`UI_RoundedRect`, `UI_Circle`) | 생성됨 · 문구를 60초 · 목표 300점으로 바꿈 |
| 3 | 야외 여름 계곡 `Valley.fbx` | `make_valley.py`. 자식 Ground · Water · Rocks · Trees · Mountains, 약 13.3k tris, 플레이어 주변 y 0 평평 | 생성됨 · 사용자 검토 대기 |
| 3 | 점수 간판 | 계곡에 어울리는 받침 (칠판 대신). 지금은 UI 패널만 떠 있음 | 예정 · 사양 미정 |
| 4 | 물풍선 4종 `Balloon_Red/Blue/Green/Gold.fbx` (35 / 28 / 22 / 12 cm) | 매듭 포함, 피벗 = 몸통 중심, 각 640 tris | 생성됨 · 사용자 검토 대기 |
| 4 | 물 효과 `Prefabs/VFX/VFX_*.prefab` | 풍선 터짐 4종(물 튐 + 쏟아지는 물 + 바닥 물보라 + 풍선 조각, Gold는 반짝이 포함), `VFX_GoldSparkle`, `VFX_WaterSpill`(올 클리어). `VfxBuilder.cs` 메뉴로 생성 | 생성 도구 작성됨 · Unity에서 실행 및 사용자 검토 대기. 점수 팝업은 예정 |
| 4 | 사운드 `Audio/SFX_*.wav` | Pop(콤보는 높이만 변경), GoldPop(팡 + 동전), WaterSpill, Fanfare, BalloonRise, UIClick, DartMiss. `make_sfx.py`로 합성 | 생성됨 · 사용자 청취 검토 대기 |

실내 다트 바 · 다트판 · 바 테이블은 삭제했다 (003). `make_base.py`(옛 `make_room.py`)에는 던지는 선 · UI 스프라이트 · 팔레트만 남아 있다.

임포트 방법: [assets/import-guide.md](../assets/import-guide.md) (데모 씬 빌더가 1~3번을 자동으로 함)

## 배치 기준 (현재 데모 씬)
- 배치표: `Tools/AssetGen/layout.py` = `Assets/_Project/Editor/DemoSceneBuilder.cs` (같은 값 유지)
- 던지는 선: z 0 / XR Origin: (0, 0, -0.25), +Z를 바라봄
- 통나무 받침대: 플레이어 오른쪽 (0.55, 0, -0.1), 다트통 윗면 높이 약 1.07 m
- 시냇물: 던지는 선에서 약 2.4 ~ 5.6 m 앞, 수면 y -0.12
- 풍선 거리: 던지는 선에서 1.2 ~ 2.0 m ([concept.md](concept.md) 5장)
- 데모 씬: [assets/demo-scene.md](../assets/demo-scene.md)

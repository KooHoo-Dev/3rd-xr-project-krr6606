# 데모 씬 (DartDemo.unity)

게임 준비 배치와 방 환경을 갖춘 XR 씬입니다. **동작(잡기·던지기·점수·버튼)은 아직 없고**, 직접 구현할 무대입니다.

> **2026-11-16 기획 전환 ([002](../decisions/002-물풍선-기획-전환.md)):** 다트판 대신 물풍선, 실내 다트 바 대신 야외 여름 계곡으로 바뀝니다.
> 이 씬의 다트판·백보드·네온·실내 방은 계곡 환경이 들어오기 전까지 **테스트용**입니다. XR Origin, 다트, 다트통, UI 패널 구성은 그대로 씁니다.

## 만들기
1. Unity 창을 클릭해 컴파일이 끝날 때까지 기다린다 (새 FBX·PNG도 이때 임포트됨)
2. 메뉴 **Tools > Dart Challenge > Build Demo Scene**
3. `Assets/_Project/Scenes/DartDemo.unity`가 생성되어 열린다
4. (선택) **Tools > Dart Challenge > Bake Lighting** — 간접광·네온 번짐을 굽는다. 몇 분 걸릴 수 있음
5. 빌드에 넣으려면 File > Build Profiles 에서 씬 추가 (Project Settings 변경이라 자동으로 하지 않음)

스크립트: `Assets/_Project/Editor/DemoSceneBuilder.cs` (AI 생성, 에디터 전용 — 빌드에 포함되지 않음)
Blender 미리보기: [Scene_player.png](previews/Scene_player.png), [Scene_corner.png](previews/Scene_corner.png)

## 씬 구성
| 그룹 | 내용 |
| --- | --- |
| Environment | 방(4 × 4 × 3 m), 펜던트 조명 2, 왼쪽 테이블·의자 2, 포스터 2, 네온 간판 2, 다트판 백보드, 벽·바닥 BoxCollider |
| Game | 던지는 선(z 0), 다트판(중심 0, 1.73, 2.0), 점수 칠판, 오른쪽 바 테이블 + 다트통 + **다트 7개(Dart_01~07, 슬롯에 꽂힘)** |
| Lighting | 다트판 스폿(Mixed), 방 포인트(Mixed), 왼쪽 램프(Mixed), 네온 번짐(Baked), 반사 프로브(구워진 큐브맵) |
| XR | XR Interaction Manager, XR Origin (XR Rig) — 위치 (0, 0, -0.25), **Locomotion 꺼짐**(기획서: 제자리 플레이), EventSystem + XR UI Input Module |
| UI | UI_ScoreBoard(칠판 위 "0 / 100", 남은 다트 점 7개), UI_StartPanel(시작 버튼), UI_ResultPanel(다시하기, 꺼져 있음) |

## 자동으로 바뀐 설정 (임포트 가이드 1~3번)
- 팔레트 텍스처: Point 필터, 밉맵 끔, 비압축 / T_Palette_MS는 sRGB 끔
- M_Palette(URP Lit, Metallic Map + Emission Map), M_Dartboard 생성 → FBX 머티리얼에 연결
- FBX: 애니메이션·카메라·조명 임포트 끔, 라이트맵 UV 생성 켬
- UI 스프라이트: Sprite 타입, 둥근 사각형 9-slice 테두리 64

## 확인할 것 (Play 또는 Scene 뷰)
| 확인 | 기대 결과 |
| --- | --- |
| Console의 `[DemoSceneBuilder] Dart_01 bounds size` | 한 변이 약 0.16 (다트 길이) |
| `Dartboard bounds size` | 약 (0.45, 0.45, 0.04) |
| Game 뷰(XR Origin 카메라) | 정면에 다트판, 위에 네온, 왼쪽 칠판에 "0 / 100", 오른손 쪽 테이블에 다트통 |
| 다트 7개 | 촉이 구멍 안으로, 깃이 위로 |
| 시작 패널 | 눈높이보다 약간 아래, 한글이 깨지지 않음 |

에디터에서 컨트롤러 없이 테스트하려면 Project Settings > XR Plug-in Management > XR Interaction Toolkit 의
`Use XR Interaction Simulator in scenes`를 켠다 (설정 변경이므로 직접 선택).

## 다음에 직접 구현할 것
1. 다트에 `XR Grab Interactable` + `Rigidbody` (Throw On Detach) — Attach Transform = `GrabPoint`
2. 다트판 충돌 → 다트 고정 + 점수 판정 (규칙: [decisions/001](../decisions/001-아트-스타일과-다트판-규칙.md))
3. GameManager: 시작 버튼 → 플레이 → 결과 패널, 점수판 텍스트 갱신

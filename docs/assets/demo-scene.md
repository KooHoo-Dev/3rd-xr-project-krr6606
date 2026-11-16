# 데모 씬 (DartDemo.unity)

야외 여름 계곡에 게임 준비 배치를 갖춘 XR 씬입니다. 게임 동작은 `Assets/_Project/Scripts/`에서 직접 구현합니다.
기획 전환 기록: [002](../decisions/002-물풍선-기획-전환.md), [003](../decisions/003-계곡-환경-제작-방식과-실내-에셋-정리.md)

## 만들기
> ⚠️ Build Demo Scene은 씬을 **처음부터 다시 만든다.** 씬에서 직접 바꾼 내용(컴포넌트 · 배치)은 사라지므로, 실행 전에 커밋하거나 프리팹으로 빼 둔다.

1. Unity를 열고 컴파일이 끝날 때까지 기다린다 (새 FBX·PNG도 이때 임포트됨)
2. 메뉴 **Tools > Dart Challenge > Build Demo Scene**
3. `Assets/_Project/Scenes/DartDemo.unity`가 다시 생성되어 열린다
4. (선택) **Tools > Dart Challenge > Bake Lighting (optional)** — 간접광을 굽는다. 몇 분 걸릴 수 있음
5. 빌드에 넣으려면 File > Build Profiles 에서 씬 추가 (Project Settings 변경이라 자동으로 하지 않음)

스크립트: `Assets/_Project/Editor/DemoSceneBuilder.cs` (AI 생성, 에디터 전용 — 빌드에 포함되지 않음)
Blender 미리보기: [Scene_player.png](previews/Scene_player.png), [Scene_behind.png](previews/Scene_behind.png), [Scene_valley.png](previews/Scene_valley.png), [Balloons_hero.png](previews/Balloons_hero.png), [LogStand_set_hero.png](previews/LogStand_set_hero.png)

## 씬 구성
| 그룹 | 내용 |
| --- | --- |
| Environment | `Valley` — Ground(자갈 강변 · 언덕, **MeshCollider**), Water(시냇물 수면 y -0.12), Rocks, Trees, Mountains(굽기에서 제외) |
| Game | 던지는 선(z 0), 통나무 받침대 + 다트통(0.55, 1.0, -0.1) + **다트 7개(Dart_01~07)**, `Balloons_Example`(빨강 · 파랑 · 초록 일렬 + 금빛 1개) |
| Lighting | 해(Directional, Mixed, 부드러운 그림자), 기본 Skybox, 하늘색 환경광, 반사 프로브(30 × 15 × 30 m) |
| XR | XR Interaction Manager, XR Origin (XR Rig) — 위치 (0, 0, -0.25), **Locomotion 꺼짐**(기획서: 제자리 플레이), EventSystem + XR UI Input Module |
| UI | UI_ScoreBoard("0 / 300", 남은 시간 "60"), UI_StartPanel(시작 버튼), UI_ResultPanel(다시하기, 꺼져 있음) |

Valley 전체 약 13.3k tris, 풍선 하나 640 tris, 통나무 480 tris — Quest 예산(~100k)에 여유가 많습니다.

## 빌더가 자동으로 하는 임포트 설정
- 팔레트 텍스처: Point 필터, 밉맵 끔, 비압축 / T_Palette_MS는 sRGB 끔
- M_Palette(URP Lit, Metallic Map + Emission Map) 생성 → 모든 FBX 머티리얼에 연결
- FBX: 애니메이션·카메라·조명 임포트 끔, 라이트맵 UV 생성 켬
- UI 스프라이트: Sprite 타입, 둥근 사각형 9-slice 테두리 64

## 확인할 것 (Play 또는 Scene 뷰)
| 확인 | 기대 결과 |
| --- | --- |
| Console의 `[DemoSceneBuilder] Dart_01 bounds size` | 한 변이 약 0.16 (다트 길이) |
| `Balloon_Red` / `Balloon_Gold bounds size` | 가로 약 0.35 / 약 0.12 |
| Game 뷰(XR Origin 카메라) | 앞에 풍선 줄과 금빛 풍선, 그 뒤로 시냇물과 숲 비탈. 오른손 쪽에 통나무 위 다트통 |
| 바닥 | 플레이어 발밑이 평평하고(y 0) 발이 땅에 묻히거나 뜨지 않음 |
| 다트 7개 | 촉이 구멍 안으로, 깃이 위로 |
| 하늘 | 기본 Skybox가 보이고, 멀리 산이 언덕 사이로 보임 |
| 시작 패널 | 눈높이보다 약간 아래, 한글이 깨지지 않음 |

에디터에서 컨트롤러 없이 테스트하려면 Project Settings > XR Plug-in Management > XR Interaction Toolkit 의
`Use XR Interaction Simulator in scenes`를 켠다 (설정 변경이므로 직접 선택).

## 직접 구현할 것
1. 다트: `XR Grab Interactable` + `Rigidbody` (Throw On Detach), Attach Transform = `GrabPoint` — 진행 중 (`Dart.cs`, `DartGate.cs`, `Prefabs/Dart_01.prefab`)
2. 풍선 프리팹: SphereCollider(Is Trigger, 반지름 = 지름/2, 중심 0) → 다트가 지나가면 터짐 + 점수
3. GameManager: 시작 버튼 → 60초 타이머 · 물결 → 결과 패널, 점수판 텍스트 갱신 — 싱글턴 뼈대만 있음 (`GameManager.cs`)

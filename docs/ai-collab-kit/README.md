# AI 협업 키트 — 프로젝트와 포트폴리오를 같이 하기

> **읽는 이:** 사용자, 그리고 이 키트를 이어서 고칠 다음 세션의 Claude.
> **상태:** v0.2 (2026-11-23) · 라운드 1 피드백 반영, **라운드 2 피드백 대기 중** → [feedback-log.md](feedback-log.md) · 피드백 원문 [feedback/](feedback/)

새 프로젝트를 AI와 시작할 때 복사해 쓰는 묶음이다. 두 가지를 해결한다.
1. **포트폴리오 재료를 프로젝트 도중에 자동으로 모은다.** 끝나고 기억을 더듬지 않는다.
2. **Claude가 문서를 독자에 맞춰 쓴다.** 누가, 무엇을 하려고 읽는지부터 정한다.

## 구성

| 파일 | 무엇 | 주 독자 |
| --- | --- | --- |
| [CLAUDE.template.md](CLAUDE.template.md) | 새 프로젝트의 CLAUDE.md 초안 | 새 세션 Claude |
| [templates/재료집.md](templates/재료집.md) | 포트폴리오 재료를 칸별로 모으는 파일 | 프로젝트 문서를 쓸 사용자 |
| [templates/devlog.md](templates/devlog.md) | 세션 기록 템플릿 | 미래의 나 · 새 세션 Claude |
| [writing-guide.md](writing-guide.md) | 독자부터 정하는 문서 작성법 | 문서를 쓰기 직전의 Claude |
| [personas.md](personas.md) | 독자 페르소나 7개 (사람 5, AI 2) | Claude · 사용자 |
| [examples/](examples/) | 독자별 예시 문서 7개 | 피드백하는 사용자 |
| [feedback-log.md](feedback-log.md) | 피드백 라운드와 반영 내역 | 다음 세션 Claude · 사용자 |
| [applications/](applications/) | 가이드를 실제 문서에 적용하는 작업 계획 (포트폴리오 다듬기) | 사용자 · 다음 세션 Claude |
| [feedback/](feedback/) | 사용자 피드백 원문(변형 없음)과 피드백을 단 원본 파일 | 다음 세션 Claude · 사용자 |

## 새 프로젝트에 쓰는 법

1. 새 프로젝트 루트에 `CLAUDE.template.md`를 `CLAUDE.md`로 복사한다.
2. 이 폴더(`docs/ai-collab-kit/`)를 새 프로젝트의 같은 위치로 복사한다. `examples/`는 빼도 된다.
3. `templates/재료집.md`를 `docs/portfolio/재료집.md`로 복사한다.
4. Claude에게 "CLAUDE.md 1장 같이 채우자"라고 한다.

## 진행 방식 (다음 세션 Claude가 알아야 할 것)

- 이 키트는 **사용자 피드백으로 고쳐 나가는 중**이다. 고치기 전에 [feedback-log.md](feedback-log.md)의 최신 라운드를 읽는다.
- 피드백을 받으면: ① 원문을 글자 그대로 `feedback/round-N-원문.md`에 옮기고 피드백이 달린 파일 전체를 `feedback/round-N-원본/`에 복사(사용자 요청: 원문은 변형 없이 따로 보관) → ② feedback-log에 라운드 추가 → ③ 해당 문서 수정 → ④ 맨 위 버전 · 날짜 갱신.
- 사용자는 문서 사이에 ```` ```피드백: …``` ```` 또는 `// …` 줄로 피드백을 남긴다. 둘 다 찾는다.
- 예시의 사실은 이 프로젝트(XR 물풍선 다트)의 기록에서만 가져온다. 근거가 없으면 `[확인 필요]`로 둔다.
- 이 프로젝트 자체의 CLAUDE.md는 아직 이 템플릿으로 바꾸지 않았다. 바꿀지는 사용자가 정한다.

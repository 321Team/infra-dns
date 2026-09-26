# AI 도구 작업 규칙 — infra-dns

이 저장소에서 작업하는 모든 AI 도구가 따르는 규칙이다. 대상은 Claude(Claude Code), GPT(ChatGPT·Codex), Grok, Cursor 등이다.

공통 규칙의 정본은 fds-project-baseline의 [AGENTS.md](https://github.com/321Team/fds-project-baseline/blob/b2e78d9dd2bb5d5084ffce531f43ccdcaa5fb4d2/AGENTS.md)와 [TICKET_SYNC_POLICY §5.1](https://github.com/321Team/fds-project-baseline/blob/b2e78d9dd2bb5d5084ffce531f43ccdcaa5fb4d2/governance/TICKET_SYNC_POLICY.md)이다(PR [#107](https://github.com/321Team/fds-project-baseline/pull/107) 병합 commit `b2e78d9` 고정). 이 문서는 요약이며, 정본과 다르면 정본이 우선한다. 정본이 개정되면 이 문서의 고정 링크와 요약을 함께 갱신한다.

## 적용 대상

- 이 저장소의 Issue 본문과 Milestone 설명
- 이 저장소 작업 중 fds-project-baseline 등 다른 저장소의 Issue·Milestone에 쓰는 경우
- 쓰기 경로는 가리지 않는다. GitHub MCP·커넥터, 도구가 대신 실행하는 `gh`/API, 에이전트 모드의 브라우저 조작이 모두 해당한다.

## 금지 — Issue 본문·Milestone 설명 직접 수정

- 본문 전체 재작성
- 절·문단·표의 추가·삭제·수정
- 링크·관리 마커(`<!-- … -->`)·보관 원문 편집
- Milestone 설명 변경(텍스트를 함께 보내면 세션 경로가 footer를 붙인 사례가 있다)

이런 변경이 필요하면 교체 본문 파일(UTF-8, LF)과 plan을 준비해 넘긴다. plan에는 `number`, 직전 재조회 `updated_at`, 변경 전 본문 SHA-256(LF), 파일 SHA-256을 적는다. 반영은 담당 Lead가 로컬 `gh`로 직접 실행한다. Milestone 설명은 사람이 웹 UI에서 편집한다.

## 허용 — 필수 속성값과 체크 상태 갱신

대상:
- 상단 필수 속성표(17개)의 값
- AC·Exit Criteria 체크 상태(`[ ]`↔`[x]`)
- 잔여 항목 표기

조건(모두 지킨다):
1. **대상 줄만 문자열 치환한다.** 조회한 원문에서 해당 줄만 바꿔 올린다. 본문 전체를 다시 출력해 쓰지 않는다.
2. **쓰기 직전에 `updated_at`을 다시 확인한다.** 조회 뒤 다른 편집이 있었으면 다시 조회해서 새로 만든다.
3. **쓰기 뒤에 재조회해 대조한다.** 바뀐 줄 외 차이 0, 손상 신호(`&lt;`·`&gt;`·단독 `` `` ``·footer) 증가 0을 확인한다. 어긋나면 추가 쓰기를 멈추고 코멘트로 보고한다.
4. **근거를 코멘트로 남긴다.** 바꾼 항목, 전→후 값, 근거 링크, AI 사용 표기를 적는다.
5. **재조회 대조를 할 수 없는 도구는 쓰지 않는다.** 웹 채팅 등은 변경안을 코멘트로만 남긴다.

## 허용 — 텍스트 없이 값만 바꾸는 변경

Milestone 기한(`due_on`), Issue 날짜 필드(Start date·Target date)가 대상이다.
- 요청에 설명·본문 등 텍스트 필드를 넣지 않는다.
- 쓰기 직전에 현재 값과 `updated_at`을 확인한다.
- 쓰기 뒤에 재조회해 다른 필드가 바이트 그대로인지 확인한다.
- 전후 값을 기록한다. 일정 값은 승인된 변경 기록에 근거가 있어야 한다.

## 항상 허용

- 읽기 전용 조회와 대조(필수 속성 누락, AC 잔여 항목, 증적 연결 점검)
- 교체 본문과 plan 준비
- Issue 코멘트와 PR 본문(AI 사용 표기 포함, footer가 붙을 수 있음을 감안)

## 판단 권한

Status·AC 충족·인수·종결은 담당 Lead가 결정한다. AI 도구는 결정과 근거를 반영할 뿐이며, 스스로 충족을 판정하지 않는다. 리뷰·병합 권한은 [리뷰 정책](docs/REVIEW_POLICY.md)과 [운영 정책](docs/POLICY.md)을 따른다. AI 점검은 독립 승인이 아니다.

## 문제 사례

2026-09-22~26 fds-project-baseline #74·#75·#9·#7·#11·#16·#35·Milestone #5가 AI 세션 경로의 편집으로 손상됐다(HTML 엔티티화, 링크 앞뒤 `` `` `` 삽입, 둥근 따옴표 변환, footer 추가). 도구의 성공 응답은 본문 보존의 증거가 아니며, 손상 조건은 확인되지 않았다. 상세·전후 예시·교훈은 [baseline AGENTS.md "문제 사례"](https://github.com/321Team/fds-project-baseline/blob/b2e78d9dd2bb5d5084ffce531f43ccdcaa5fb4d2/AGENTS.md)에 있다.

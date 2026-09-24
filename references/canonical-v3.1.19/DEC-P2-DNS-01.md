# DEC-P2-DNS-01 — Hybrid DNS Scope Decision

> v3.1.19 CANDIDATE / NOT RELEASED · 2026-09-17 20:28 KST

## 현행 속성

| Property | 입력값 |
|---|---|
| Record ID | DEC-P2-DNS-01 |
| Phase | Phase 2 |
| Category | Architecture / DNS |
| Type | Decision |
| Status | To Do |
| Priority | P1 |
| Start | 2026-10-12 |
| End | 2026-10-16 |
| Calendar Days | 5 |
| Working Days | 5 |
| Lead | 이권욱 |
| Support | 이하영 |
| Exit Criteria | P0 IP Endpoint 유지 또는 Hybrid DNS P1 적용을 확정하고 Resolver/Forwarding/Zone/Route/테스트·Cancelled 결정 근거를 승인 |
| Related Decision IDs | D11; D23 |
| Related Risk IDs | RISK-10; RISK-12 |
| Source | Baseline v3.1.19 CANDIDATE; GitHub #40 @ 2026-09-14T15:16:01Z; 원문 SHA256 d29aacd62e8bd35e1b58dbd297df8f90d4de6fbc9714b8aac755cb1ce7b80764 |
| Schedule Note | Hybrid P0 E2E는 IP Endpoint를 허용하므로 본 P1 결정 미완료가 G5/G6를 자동 차단하지 않는다. |

## 상태와 인수 경계

현재 티켓 속성·AC·종결 이력을 수집했다. 이번 문서 통합에서 새로운 Runtime 시험이나 완료 승인을 수행하지 않았다.

- GitHub lifecycle: open; Milestone: G5 ROSA Application Ready
- 일정은 조정 가능한 계획이며 실제 완료일·Gate 승인일과 구분한다.
- 원문·후속 댓글: [원본 티켓](https://github.com/321Team/fds-project-baseline/issues/40), [고정 수집본](https://github.com/321Team/fds-project-baseline/blob/b2e4612cf2e417b10e7f145c5b1e5f58dbe1b948/tickets/v3.1.19/sources/issue-40.json).
- 상위 속성표는 이 후보의 현행 표다. 아래 원문은 수집 시점의 변경/승인/AC 이력이며 과거 버전 문구를 현재 발행 상태로 사용하지 않는다.

## 원문 보존

<details>
<summary>수집한 GitHub 본문 전체 — SHA256 d29aacd62e8bd35e1b58dbd297df8f90d4de6fbc9714b8aac755cb1ce7b80764</summary>

<!-- fds-spec-audit:20260914:v1:start -->
## 사양·기록 전수 점검 후속 — 2026-09-14 점검 반영

사용자 “각 티켓에 내용 갱신” 지시에 따른 기록 보완. 재대조: `2026-09-14T15:11:45+00:00`. 발행 [docs-v3.1.18](https://github.com/321Team/fds-project-baseline/releases/tag/docs-v3.1.18)과 후속 결정·현재 Issue/PR를 기준으로 한다.

**이 티켓의 점검 결과:** 조건부 결정. IP endpoint 또는 Hybrid DNS·적용/유예/N/A 근거를 D23으로 기록.

**인계·관련 티켓:** [#34](https://github.com/321Team/fds-project-baseline/issues/34) · [#47](https://github.com/321Team/fds-project-baseline/issues/47) · [#48](https://github.com/321Team/fds-project-baseline/issues/48).

점검 항목 A01~A07/R01~R06의 전체 대응은 [P1-DOC-01 #24](https://github.com/321Team/fds-project-baseline/issues/24)에서 추적한다. 미완료 티켓의 기록/시험값은 해당 실행·인수 전에 확정할 후속이며, 유예·조건부 P1/P2 항목을 현재 P0 차단으로 추가하지 않는다.

이번 내용 갱신은 기존 AC 체크·Status·Lead/Support·계획 일정·사람의 승인/종결을 변경하지 않는다. 아래 작성 당시의 미병합·검토대기 표현은 위 최신 확인 및 연결된 근거와 구분한다. 기존 본문·보관 원문·댓글은 보존한다.
<!-- fds-spec-audit:20260914:v1:end -->

---

<!-- fds-milestone-assignment:2026-09-11 issue:40 -->
## 대표 Milestone 배정 — 2026-09-11

- **추적 Milestone:** G5 ROSA Application Ready (GitHub #9)
- **배정 성격:** P2 잠정 계획 · 이권욱 사용자 지시에 따른 대표 추적 항목 지정.
- **배정 근거:** WBS 2026-10-12~10-16 DNS 범위 결정 계획에 따라 G5에 연결한다. 기존 G5/G6 Non-blocking Decision 및 P0 IP Endpoint 허용을 유지한다.
- **출처:** [발행 정본 v3.1.18 WBS](https://github.com/321Team/fds-project-baseline/blob/72599ae49342b0fb8dbd3d8ee60314afb9f907bb/wbs/FDS_v3.1.18_WBS_and_Gantt_v1.0.xlsx)
- **일정 원칙:** 일정은 고정된 필수 기한이 아닌 조정 가능한 계획 목표다. 선행조건과 영향 확인 후 유연하게 조정하며, 실제 완료일·승인·Runtime 증적 요건과 구분한다.
- **적용 범위:** 대표 Milestone 연결과 이 근거 기록. 기존 상태·완료 사실·AC·담당·티켓 Start/End 및 Gate 요건을 유지한다.

---

<!-- fds-notion-migration:2026-09-09 record-id:DEC-P2-DNS-01 -->
<!-- fds-canonical-description:v3.1.18 record-id:DEC-P2-DNS-01 -->
# DEC-P2-DNS-01 — Hybrid DNS Scope Decision

> 적용 기준: [발행 정본 v3.1.18](https://github.com/321Team/fds-project-baseline/releases/tag/docs-v3.1.18) · 2026-09-11 11:23:47 KST 게시.
> 승인 소스: `72599ae49342b0fb8dbd3d8ee60314afb9f907bb`. 문서의 작성 당시 후보·미발행·이전 상태 표현은 이력이며, 현재 적용 기준은 이 머리말과 최신 운영 기록을 따른다. 계획 갱신으로 실제 AC·승인·종결을 상향하지 않는다.

## 티켓 속성

| Property | 입력값 |
| --- | --- |
| Record ID | DEC-P2-DNS-01 |
| Phase | Phase 2 |
| Category | Architecture / DNS |
| Type | Decision |
| Status | To Do |
| Priority | P1 |
| Start | 2026-10-12 |
| End | 2026-10-16 |
| Calendar Days | 5 |
| Working Days | 5 |
| Lead | 이권욱 |
| Support | 이하영 |
| Exit Criteria | P0 IP Endpoint 유지 또는 Hybrid DNS P1 적용을 확정하고 Resolver/Forwarding/Zone/Route/테스트·Cancelled 결정 근거를 승인 |
| Related Decision IDs | D11; D23 |
| Related Risk IDs | RISK-10; RISK-12 |
| Source | Baseline v3.1.18; Ticket Pack v3.1.18; GitHub #40 snapshot 2026-09-09T12:08:24Z |
| Schedule Note | Hybrid P0 E2E는 IP Endpoint를 허용하므로 본 P1 결정 미완료가 G5/G6를 자동 차단하지 않는다. |


## 최신 운영 기록의 보존

- 이관 직전 Issue 상태: **To Do / open**. 원본 갱신 시각: `2026-09-09T12:08:24Z`.
- 담당·라벨·실제 Type·Milestone·댓글·AC 판정은 이 Description 단계에서 변경하지 않는다.
- 현행 설계·Scope·계획은 상단 v3.1.18을 따른다. 아래 원문 보관의 과거 사양·상태를 현재 값으로 다시 적용하지 않는다.

## 정본에 반영된 실행·검토 상태 — 작성 시점 기록

기준 시점의 To Do 상태와 기존 Acceptance를 유지한다. 이번 정본 정리에서는 서버 실행·새 Runtime 판정을 수행하지 않았다.

근거: [Issue #40](https://github.com/321Team/fds-project-baseline/issues/40), Issue 갱신 시각 `2026-09-09T12:08:24Z`. 댓글·승인 기록과 본문 보관본은 [정본 수집 원문](https://github.com/321Team/fds-project-baseline/blob/72599ae49342b0fb8dbd3d8ee60314afb9f907bb/tickets/v3.1.18/source-snapshot.json)에 보존하고 실제 Gate는 해당 증적·승인 범위로 판정한다.

## 적용 기준

- Baseline v3.1.18의 현행 설계·Interface·Gate와 아래 Scope/Acceptance를 함께 적용한다.
- 이력의 당시 PASS·Done은 원래 범위에 한정한다. 후속 Runtime 또는 승인자를 새로 생성하지 않는다.

---

# User Story

Hybrid Network 담당자로서 Phase 2에서 Hybrid DNS를 적용할지 결정한다. 이를 통해 P1 기능이 P0 Hybrid E2E 일정을 불필요하게 차단하지 않도록 한다.

---

# Scope

## In Scope

- IP Endpoint 유지안
- Hybrid DNS 적용안
- Conditional Forwarding
- Route/ACL
- Test/N/A 기준

## Out of Scope

- 명시되지 않은 P1/P2 기능과 Scope Out 기능은 본 티켓에서 구현하지 않는다.

---

# 핵심 요구사항

- [ ] P0 DB `.55`와 필요 시 Harbor `.54` IP Endpoint를 보장한다.
- [ ] 적용안은 Resolver와 Zone 권위를 명시한다.
- [ ] 미적용 시 P1 Backlog Owner/Due를 기록한다.
- [ ] Reverse/PTR을 자동 포함하지 않는다.

---

# Acceptance Criteria

- [ ] P0/P1 범위가 단일안으로 승인된다.
- [ ] 적용 시 Query Path와 Test가 정의된다.
- [ ] 미적용 시 N/A/Deferred 근거가 기록된다.

---

# 검증 및 증적

- Decision 비교표
- DNS/Route 영향도
- Decision D23
- 갱신 Interface/WBS
- Evidence Path: `docs/evidence/DEC-P2-DNS-01/`

---

# Dependency

- **Blocked By:** P2-VPN-01 Route 설계
- **Blocks / Next:** P2-HYB-01
- **Related Ticket:** P1-DNS-01
- **Milestone:** G5 / G6 Non-blocking Decision

---

# Decision / Risk Control

- **Related Decision IDs:** D11; D23
- **Decision Control:** D23 결과는 P0 E2E 차단 여부와 후속 P1 Due를 함께 기록한다.
- **Related Risk IDs:** RISK-10; RISK-12
- **Risk Control:** 관련 Risk의 예방·탐지·복구 통제를 Acceptance와 Evidence에 연결한다.

---

# Completion Record

- **Result:** TBD
- **Status:** To Do
- **Exit Criteria:** P0 IP Endpoint 유지 또는 Hybrid DNS P1 적용을 확정하고 Resolver/Forwarding/Zone/Route/테스트·Cancelled 결정 근거를 승인
- **Completed Date:** 미입력
- **Reviewer / Approver:** 미입력 — 입력 시 풀네임 사용

## 갱신 전 원문 보관

<details>
<summary>이전 본문·승인·검토·AC 이력 원문 — 당시 기록</summary>

원문 SHA-256: `435220556fff452886c9f9540bd90c868f859d20d9098b2d96610431f56019d5`. 원문은 아래 문자 그대로 보존하며 현재 속성표로 사용하지 않는다.

````text
<!-- fds-notion-migration:2026-09-09 record-id:DEC-P2-DNS-01 -->
# DEC-P2-DNS-01 — Hybrid DNS Scope Decision

> 이관일: 2026-09-09 · 정본 및 보관 Notion 입력본 기준. Notion 실시간 원문·댓글·첨부의 완전 복제를 확인한 결과는 아니다.

## Notion 데이터 속성

| Property | 입력값 |
|---|---|
| Record ID | DEC-P2-DNS-01 |
| Phase | Phase 2 |
| Category | Architecture / DNS |
| Type | Decision |
| Status | To Do |
| Priority | P1 |
| Start | 2026-10-12 |
| End | 2026-10-16 |
| Calendar Days | 5 |
| Working Days | 5 |
| Lead | 이권욱 |
| Support | 이하영 |
| Exit Criteria | P0 IP Endpoint 유지 또는 Hybrid DNS P1 적용을 확정하고 Resolver/Forwarding/Zone/Route/테스트·Cancelled 결정 근거를 승인 |
| Related Decision IDs | D11; D23 |
| Related Risk IDs | RISK-10; RISK-12 |
| Source | FDS_Project_Implementation_Baseline_v3.1.12; FDS_Phase1_Logical_Architecture_v3.1.2; Phase 2 OCI/AWS/ROSA Design; 이관 대조: Baseline/WBS v3.1.17 (commit 2d93395a0e19ea67e5be199d7183a7edbaa6cf4c) |
| Schedule Note | Hybrid P0 E2E는 IP Endpoint를 허용하므로 본 P1 결정 미완료가 G5/G6를 자동 차단하지 않는다. |

## 이관 기준 및 확인 사항

- 속성의 일정·담당·상태는 RELEASED v3.1.17 WBS(기준일 2026-09-04)를 우선 반영했다. 이후 별도 근거가 있는 변경만 아래에 명시한다.
- [현행 정본 v3.1.17](https://github.com/321Team/fds-project-baseline/blob/2d93395a0e19ea67e5be199d7183a7edbaa6cf4c/baseline/FDS_Project_Implementation_Baseline_v3.1.17.md) · [정본 WBS](https://github.com/321Team/fds-project-baseline/blob/2d93395a0e19ea67e5be199d7183a7edbaa6cf4c/wbs/FDS_v3.1.17_WBS_and_Gantt_v1.0.xlsx).
- 본문은 아래에 적힌 원본 버전의 기록이다. 위 속성·후속 승인과 다른 과거 상태는 현재 판정으로 사용하지 않는다. 이관 자체로 미실행 AC를 체크하거나 새 승인을 부여하지 않는다.
- Lead/Support의 풀네임은 본문 속성으로 보존한다. GitHub 계정 대응이 확인되지 않은 사람에게 자동 배정하지 않았다.

## 원본 및 변경 출처

- `FDS_Notion_Remaining_Backlog_Manual_v1.9.md`
- `FDS_v3.1.17_WBS_and_Gantt_v1.0.xlsx`

---

## Description — 보관 입력본

> 원본: `FDS_Notion_Remaining_Backlog_Manual_v1.9.md`. 원본의 완료/미완료 체크와 당시 이력을 보존했다.

# 🎯 User Story

Hybrid Network 담당자로서 Phase 2에서 Hybrid DNS를 적용할지 결정한다. 이를 통해 P1 기능이 P0 Hybrid E2E 일정을 불필요하게 차단하지 않도록 한다.

---

# 📌 Scope

## In Scope

- IP Endpoint 유지안
- Hybrid DNS 적용안
- Conditional Forwarding
- Route/ACL
- Test/N/A 기준

## Out of Scope

- 명시되지 않은 P1/P2 기능과 Scope Out 기능은 본 티켓에서 구현하지 않는다.

---

# 📋 핵심 요구사항

- [ ] P0 DB `.55`와 필요 시 Harbor `.54` IP Endpoint를 보장한다.
- [ ] 적용안은 Resolver와 Zone 권위를 명시한다.
- [ ] 미적용 시 P1 Backlog Owner/Due를 기록한다.
- [ ] Reverse/PTR을 자동 포함하지 않는다.

---

# ✅ Acceptance Criteria

- [ ] P0/P1 범위가 단일안으로 승인된다.
- [ ] 적용 시 Query Path와 Test가 정의된다.
- [ ] 미적용 시 N/A/Deferred 근거가 기록된다.

---

# 🧪 검증 및 증적

- Decision 비교표
- DNS/Route 영향도
- Decision D23
- 갱신 Interface/WBS
- Evidence Path: `docs/evidence/DEC-P2-DNS-01/`

---

# 🔗 Dependency

- **Blocked By:** P2-VPN-01 Route 설계
- **Blocks / Next:** P2-HYB-01
- **Related Ticket:** P1-DNS-01
- **Milestone:** G5 / G6 Non-blocking Decision

---

# ⚖️ Decision / Risk Control

- **Related Decision IDs:** D11; D23
- **Decision Control:** D23 결과는 P0 E2E 차단 여부와 후속 P1 Due를 함께 기록한다.
- **Related Risk IDs:** RISK-10; RISK-12
- **Risk Control:** 관련 Risk의 예방·탐지·복구 통제를 Acceptance와 Evidence에 연결한다.

---

# 📝 Completion Record

- **Result:** TBD
- **Status:** To Do
- **Exit Criteria:** P0 IP Endpoint 유지 또는 Hybrid DNS P1 적용을 확정하고 Resolver/Forwarding/Zone/Route/테스트·Cancelled 결정 근거를 승인
- **Completed Date:** 미입력
- **Reviewer / Approver:** 미입력 — 입력 시 풀네임 사용
````

</details>


</details>

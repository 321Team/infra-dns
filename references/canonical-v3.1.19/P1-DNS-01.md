# P1-DNS-01 — Internal DNS Primary/Secondary

> v3.1.19 CANDIDATE / NOT RELEASED · 2026-09-17 20:28 KST

## 현행 속성

| Property | 입력값 |
|---|---|
| Record ID | P1-DNS-01 |
| Phase | Phase 1 |
| Category | DNS / Supporting Service |
| Type | Task |
| Status | Done |
| Priority | P1 |
| Start | 2026-08-28 |
| End | 2026-09-03 |
| Calendar Days | 7 |
| Working Days | 5 |
| Lead | 이권욱 |
| Support | 이하영 |
| Exit Criteria | Primary/Secondary·TSIG·제한 Query/Recursion·Failover Evidence와 k8s-api-lb01 `.109` Resolver/ACL/IPSet 검증 및 Support Review 승인 |
| Related Decision IDs | D08; D09; D34; D35 |
| Related Risk IDs | RISK-02; RISK-04; RISK-07 |
| Source | Baseline v3.1.19 CANDIDATE; GitHub #12 @ 2026-09-14T15:14:27Z; 원문 SHA256 7aeb1f0922e47a785a81ec918bc76ba8a7a022e7d47bf81fe6a08f812584ccf3 |
| Schedule Note | 기술 검증·Support Review·.109 ACL/Resolver/Failover Delta 확인 완료. 2026-09-03 Done 승인. |

## 상태와 인수 경계

현재 티켓 속성·AC·종결 이력을 수집했다. 이번 문서 통합에서 새로운 Runtime 시험이나 완료 승인을 수행하지 않았다.

- GitHub lifecycle: closed; Milestone: G1 Infrastructure Ready
- 일정은 조정 가능한 계획이며 실제 완료일·Gate 승인일과 구분한다.
- 원문·후속 댓글: [원본 티켓](https://github.com/321Team/fds-project-baseline/issues/12), [고정 수집본](https://github.com/321Team/fds-project-baseline/blob/b2e4612cf2e417b10e7f145c5b1e5f58dbe1b948/tickets/v3.1.19/sources/issue-12.json).
- 상위 속성표는 이 후보의 현행 표다. 아래 원문은 수집 시점의 변경/승인/AC 이력이며 과거 버전 문구를 현재 발행 상태로 사용하지 않는다.

## 원문 보존

<details>
<summary>수집한 GitHub 본문 전체 — SHA256 7aeb1f0922e47a785a81ec918bc76ba8a7a022e7d47bf81fe6a08f812584ccf3</summary>

<!-- fds-spec-audit:20260914:v1:start -->
## 사양·기록 전수 점검 후속 — 2026-09-14 점검 반영

사용자 “각 티켓에 내용 갱신” 지시에 따른 기록 보완. 재대조: `2026-09-14T15:11:45+00:00`. 발행 [docs-v3.1.18](https://github.com/321Team/fds-project-baseline/releases/tag/docs-v3.1.18)과 후속 결정·현재 Issue/PR를 기준으로 한다.

**이 티켓의 점검 결과:** DNS 원 종결 유지. 신규 프록시 .56 ACL/ipset 4/4 결과는 #78/#74·As-built에 연결 ; A07/R05.

- 새 egress-proxy01 .56에 대한 양 DNS BIND ACL·firewalld ipset runtime/permanent와 UDP/TCP4/4 결과는 #78/#74의 후속 변경 근거다. 원 DNS 구축 종결과 OID-04 관리망 DNS N/A를 유지한다.

**인계·관련 티켓:** [#74](https://github.com/321Team/fds-project-baseline/issues/74) · [#78](https://github.com/321Team/fds-project-baseline/issues/78).

점검 항목 A01~A07/R01~R06의 전체 대응은 [P1-DOC-01 #24](https://github.com/321Team/fds-project-baseline/issues/24)에서 추적한다. 미완료 티켓의 기록/시험값은 해당 실행·인수 전에 확정할 후속이며, 유예·조건부 P1/P2 항목을 현재 P0 차단으로 추가하지 않는다.

이번 내용 갱신은 기존 AC 체크·Status·Lead/Support·계획 일정·사람의 승인/종결을 변경하지 않는다. 아래 작성 당시의 미병합·검토대기 표현은 위 최신 확인 및 연결된 근거와 구분한다. 기존 본문·보관 원문·댓글은 보존한다.
<!-- fds-spec-audit:20260914:v1:end -->

---

<!-- fds-milestone-assignment:2026-09-11 issue:12 -->
## 대표 Milestone 배정 — 2026-09-11

- **추적 Milestone:** G1 Infrastructure Ready (GitHub #2)
- **배정 성격:** 완료 이력 · 이권욱 사용자 지시에 따른 대표 추적 항목 지정.
- **배정 근거:** 2026-09-03 DNS 기술 검증·Support Review 및 .109 Delta 승인 완료. G1 인프라 추적에 연결하며 기존 Non-blocker 구분을 유지한다.
- **출처:** [발행 정본에 보존된 종결·승인 이력](https://github.com/321Team/fds-project-baseline/blob/72599ae49342b0fb8dbd3d8ee60314afb9f907bb/tickets/v3.1.18/source-snapshot.json)
- **일정 원칙:** 일정은 고정된 필수 기한이 아닌 조정 가능한 계획 목표다. 선행조건과 영향 확인 후 유연하게 조정하며, 실제 완료일·승인·Runtime 증적 요건과 구분한다.
- **적용 범위:** 대표 Milestone 연결과 이 근거 기록. 기존 상태·완료 사실·AC·담당·티켓 Start/End 및 Gate 요건을 유지한다.

---

<!-- fds-notion-migration:2026-09-09 record-id:P1-DNS-01 -->
<!-- fds-canonical-description:v3.1.18 record-id:P1-DNS-01 -->
# P1-DNS-01 — Internal DNS Primary/Secondary

> 적용 기준: [발행 정본 v3.1.18](https://github.com/321Team/fds-project-baseline/releases/tag/docs-v3.1.18) · 2026-09-11 11:23:47 KST 게시.
> 승인 소스: `72599ae49342b0fb8dbd3d8ee60314afb9f907bb`. 문서의 작성 당시 후보·미발행·이전 상태 표현은 이력이며, 현재 적용 기준은 이 머리말과 최신 운영 기록을 따른다. 계획 갱신으로 실제 AC·승인·종결을 상향하지 않는다.

## 티켓 속성

| Property | 입력값 |
| --- | --- |
| Record ID | P1-DNS-01 |
| Phase | Phase 1 |
| Category | DNS / Supporting Service |
| Type | Task |
| Status | Done |
| Priority | P1 |
| Start | 2026-08-28 |
| End | 2026-09-03 |
| Calendar Days | 7 |
| Working Days | 5 |
| Lead | 이권욱 |
| Support | 이하영 |
| Exit Criteria | Primary/Secondary·TSIG·제한 Query/Recursion·Failover Evidence와 k8s-api-lb01 `.109` Resolver/ACL/IPSet 검증 및 Support Review 승인 |
| Related Decision IDs | D08; D09; D34; D35 |
| Related Risk IDs | RISK-02; RISK-04; RISK-07 |
| Source | Baseline v3.1.18; Ticket Pack v3.1.18; GitHub #12 snapshot 2026-09-10T02:09:19Z |
| Schedule Note | 기술 검증·Support Review·.109 ACL/Resolver/Failover Delta 확인 완료. 2026-09-03 Done 승인. |


## 최신 운영 기록의 보존

- 이관 직전 Issue 상태: **Done / closed**. 원본 갱신 시각: `2026-09-10T02:09:19Z`.
- 담당·라벨·실제 Type·Milestone·댓글·AC 판정은 이 Description 단계에서 변경하지 않는다.
- 현행 설계·Scope·계획은 상단 v3.1.18을 따른다. 아래 원문 보관의 과거 사양·상태를 현재 값으로 다시 적용하지 않는다.

## 정본에 반영된 실행·검토 상태 — 작성 시점 기록

기준 시점의 Done 상태와 기존 Acceptance를 유지한다. 이번 정본 정리에서는 서버 실행·새 Runtime 판정을 수행하지 않았다.

근거: [Issue #12](https://github.com/321Team/fds-project-baseline/issues/12), Issue 갱신 시각 `2026-09-10T02:09:19Z`. 댓글·승인 기록과 본문 보관본은 [정본 수집 원문](https://github.com/321Team/fds-project-baseline/blob/72599ae49342b0fb8dbd3d8ee60314afb9f907bb/tickets/v3.1.18/source-snapshot.json)에 보존하고 실제 Gate는 해당 증적·승인 범위로 판정한다.

## 적용 기준

- Baseline v3.1.18의 현행 설계·Interface·Gate와 아래 Scope/Acceptance를 함께 적용한다.
- 이력의 당시 PASS·Done은 원래 범위에 한정한다. 후속 Runtime 또는 승인자를 새로 생성하지 않는다.
- 이 티켓은 종결 이력이다. 과거 구성 설명은 해당 종결 범위를 설명하며 현재 배포 명령으로 사용하지 않는다. 후속 설계 변경은 Baseline의 현행 절과 책임 티켓을 따른다.

---

### User Story

인프라 담당자로서 승인된 P1 Host에 제한된 Primary/Secondary DNS와 Failover를 제공하고 k8s-api-lb01도 내부 DNS 정본을 사용하도록 한다.

### Scope

#### In Scope

- dns01/dns02, `fds.internal`, TSIG Transfer, 제한 Query/Recursion
- k8s-api-lb01 `.109` BIND ACL·firewalld IPSet·Resolver·Failover

#### Out of Scope

- Reverse/PTR, DNSSEC, 완전한 Authoritative/Recursive 분리, Hybrid DNS

### 핵심 요구사항

- [x] Primary/Secondary·TSIG·기존 Client Failover Technical PASS
- [x] dns01/dns02 ACL과 `fds-dns-clients` IPSet에 `.109` 반영
- [x] k8s-api-lb01 Resolver `.52→.53`, Search Domain `fds.internal`
- [x] `.109` 내부·외부 Query와 Primary 장애 Failover Technical Test
- [x] Management `.10/.20/.30` DNS 필요성·ACL OID-04 결정 — N/A 종결: v3.1.17 §15.1 OID-04 / IF-13M(D36)에 따라 P1 범위 제외, IF-13M 미구현 및 `.10` 제외 유지. 향후 도입은 Change Request 대상이다. 호스트별 ACL 구현·시험 PASS를 뜻하지 않는다.

### Acceptance Criteria

- [x] 원본 Evidence SHA-256 및 Support Review 승인 — DNS-AC-12/14/16 PASS (2026-09-03 승인본).
- [x] `.109` Positive Test PASS, 비승인 Source Negative Test 유지 — DNS-AC-06/10/11; DNS-NT-01/03; DNS-CR-05 PASS (2026-09-03 승인본).
- [x] Secret/TSIG 원문이 Evidence에 포함되지 않음 — DNS-AC-13 PASS (2026-09-03 승인본).

### 검증 및 증적

- `docs/evidence/P1-DNS-01/`
- 상세 Description: `P1-DNS-01_Notion_Description_v1.1.md`

### Dependency

- `.109` delta 실행 시점: P1-LB-01 Stage A
- Routing/SNAT 변경 시에만 D-NET-01 §15.2 ICR 발행

### Decision / Risk Control

- Decision: `.109`는 실제 LB VM Interface이므로 DNS Consumer로 허용한다.
- Risk Control: `/24` 전체가 아닌 `.109/32`만 추가하고 기존 monitor01 차단을 유지한다.

### Review / Handoff

- Review Owner: 이하영
- Handoff: ACL/IPSet·Resolver·Failover Evidence를 P1-LB와 P1-K8S에 전달한다.

### Completion Record

- Result: DNS 기능·보안·Failover·R2 Evidence Integrity·Runbook·Support Review PASS
- Status: Done
- Completed Date: 2026-09-03
- Reviewer / Approver: 이하영 / 이권욱 — Approved (2026-09-03)

## 승인본의 상세 Acceptance Criteria 보완

| ID | 완료 조건 | 현재 판정 |
|---|---|---|
| DNS-AC-01 | dns01 Primary와 dns02 Secondary가 활성화되고 부팅 시 자동 시작됨 | PASS |
| DNS-AC-02 | 승인된 13개 A Record가 양쪽 권한 서버에서 동일하게 응답함 | PASS |
| DNS-AC-03 | SOA Serial이 `2026090101`로 일치함 | PASS |
| DNS-AC-04 | Fresh HMAC-SHA256 TSIG Transfer가 성공하고 BADKEY/BADSIG가 없음 | PASS |
| DNS-AC-05 | 미인증 AXFR이 실패함 | PASS |
| DNS-AC-06 | 승인 Source만 Query/Recursion과 TCP/UDP 53에 접근할 수 있음 | PASS |
| DNS-AC-07 | `8.8.8.8` Forwarding과 `forward only` 외부 해석이 정상임 | PASS |
| DNS-AC-08 | Primary 중단 중 dns02가 내부·외부 해석을 지속함 | PASS |
| DNS-AC-09 | k8s-control01 Resolver Canary, Rollback, Reapply, Failover가 정상임 | PASS |
| DNS-AC-10 | k8s-api-lb01 `.109`의 ACL/IPSet, Resolver 및 Failover가 정상임 | PASS |
| DNS-AC-11 | monitor01의 직접 내부/재귀 질의가 차단됨 | PASS |
| DNS-AC-12 | 원본 11개, Sidecar 11개, Manifest 12개와 ZIP Sidecar가 검증됨 | PASS |
| DNS-AC-13 | Evidence에 TSIG Secret, Key Hash, 인증 AXFR MAC이 노출되지 않음 | PASS |
| DNS-AC-14 | v1.8 기반 R2가 정본 경로에 반영되고 ZIP SHA-256이 일치함 | PASS |
| DNS-AC-15 | 재실행 가능한 Runbook에 Subshell Guard와 상대 ZIP Sidecar 규칙이 반영됨 | PASS — v1.9 설치/Runbook/Canonical RC 0 |
| DNS-AC-16 | 이하영 Support Reviewer가 정본과 검증 결과를 승인함 | PASS — 2026-09-03 |
| DNS-AC-17 | 전체 6개 Node Resolver 전환의 소유 티켓, 일정, 검증 기준이 명시됨 | PASS |
| DNS-AC-18 | CoreDNS Source 관측과 ACL/ICR 분기 기준이 P1-K8S-01 Handoff로 명시됨 | PASS |

## 체크사항 보완 근거와 후속 작업 (2026-09-09)

- 상세 승인본: `P1-DNS-01_Notion_Description_v1.3_Review.md` (본문 v1.3-R5, 2026-09-03).
- 승인 기록: `P1-DNS-01_Support_Review_Approval_Record_20260903.md`. 이하영 회신만으로 승인을 추정한 것이 아니라 이권욱 Lead의 승인 완료 확정을 함께 기록한 문서다.
- R2 정본 ZIP: `P1-DNS-01-FRESH-20260902-R2.zip`; SHA-256 `e23d02a8422fdc4943ce2e255b5b087f0e58e5ad2a0439ddcf7d041276f315ab`. Raw TXT 11개, Sidecar 11개, Manifest 12개와 ZIP Sidecar 검증 PASS 기록을 대조했다.
- `.109` 증적: `lb/20260902T184256+0900_k8s_api_lb01_evidence.txt`, `failover/20260902T184144+0900_k8s_api_lb01_failover_evidence.txt`. 비승인 Source 증적: `monitor01/20260902T184303+0900_monitor01_negative.txt`.
- 전체 6개 Node Resolver 전환의 실행·멱등성 검증은 [CR-P1-ANS-01-01 #58](https://github.com/321Team/fds-project-baseline/issues/58) 소유다. DNS-AC-17의 PASS는 소유권·일정·검증 기준 Handoff에 대한 판정이다.
- CoreDNS Source 관측과 ACL/ICR 분기는 [P1-K8S-01 #10](https://github.com/321Team/fds-project-baseline/issues/10) 소유다. DNS-AC-18의 PASS는 Handoff 기준 문서화에 대한 판정이며 Runtime 완료를 뜻하지 않는다.
- OID-04는 [v3.1.17 정본 §15.1](https://github.com/321Team/fds-project-baseline/blob/2d93395a0e19ea67e5be199d7183a7edbaa6cf4c/baseline/FDS_Project_Implementation_Baseline_v3.1.17.md)의 OID-04 및 IF-13M(D36) 행에 근거해 P1 N/A로 종결했다. 별도 호스트 허용 승인이나 Runtime PASS를 만들어 넣지 않았다.

## 갱신 전 원문 보관

<details>
<summary>이전 본문·승인·검토·AC 이력 원문 — 당시 기록</summary>

원문 SHA-256: `3551107b2a496f900fc34addef828fcaa5aed7fd6a7080b51038ff2827d7d2e3`. 원문은 아래 문자 그대로 보존하며 현재 속성표로 사용하지 않는다.

````text
<!-- fds-notion-migration:2026-09-09 record-id:P1-DNS-01 -->
# P1-DNS-01 — Internal DNS Primary/Secondary

> 이관일: 2026-09-09 · 정본 및 보관 Notion 입력본 기준. Notion 실시간 원문·댓글·첨부의 완전 복제를 확인한 결과는 아니다.

## Notion 데이터 속성

| Property | 입력값 |
|---|---|
| Record ID | P1-DNS-01 |
| Phase | Phase 1 |
| Category | DNS / Supporting Service |
| Type | Task |
| Status | Done |
| Priority | P1 |
| Start | 2026-08-28 |
| End | 2026-09-03 |
| Calendar Days | 7 |
| Working Days | 5 |
| Lead | 이권욱 |
| Support | 이하영 |
| Exit Criteria | Primary/Secondary·TSIG·제한 Query/Recursion·Failover Evidence와 k8s-api-lb01 `.109` Resolver/ACL/IPSet 검증 및 Support Review 승인 |
| Related Decision IDs | D08; D09; D34; D35 |
| Related Risk IDs | RISK-02; RISK-04; RISK-07 |
| Source | Baseline v3.1.15; P1-DNS Description v1.1; P1-DNS Evidence Package v1.0; P1-LB Guide v1.3; D35; 이관 대조: Baseline/WBS v3.1.17 (commit 2d93395a0e19ea67e5be199d7183a7edbaa6cf4c) |
| Schedule Note | 기술 검증·Support Review·.109 ACL/Resolver/Failover Delta 확인 완료. 2026-09-03 Done 승인. |

## 이관 기준 및 확인 사항

- 속성의 일정·담당·상태는 RELEASED v3.1.17 WBS(기준일 2026-09-04)를 우선 반영했다. 이후 별도 근거가 있는 변경만 아래에 명시한다.
- v3.1.17에서 Technical/Evidence/Support Review Closed로 Done(2026-09-03)이 확인된다. 2026-09-03 승인본과 Support Review 승인 기록으로 Description의 체크사항과 Completion Record를 보완했다.
- [현행 정본 v3.1.17](https://github.com/321Team/fds-project-baseline/blob/2d93395a0e19ea67e5be199d7183a7edbaa6cf4c/baseline/FDS_Project_Implementation_Baseline_v3.1.17.md) · [정본 WBS](https://github.com/321Team/fds-project-baseline/blob/2d93395a0e19ea67e5be199d7183a7edbaa6cf4c/wbs/FDS_v3.1.17_WBS_and_Gantt_v1.0.xlsx).
- 본문은 아래에 적힌 원본 버전의 기록이다. 위 속성·후속 승인과 다른 과거 상태는 현재 판정으로 사용하지 않는다. 이관 자체로 미실행 AC를 체크하거나 새 승인을 부여하지 않는다.
- Lead/Support의 풀네임은 본문 속성으로 보존한다. GitHub 계정 대응이 확인되지 않은 사람에게 자동 배정하지 않았다.

## 원본 및 변경 출처

- `FDS_Notion_Remaining_Backlog_Manual_v1.9.md`
- `FDS_v3.1.15_Canonical_Ticket_Update_Pack_v1.0.md`
- `FDS_v3.1.17_WBS_and_Gantt_v1.0.xlsx`

---

## Description — 승인 기록 반영 (2026-09-09)

> 원본: `FDS_v3.1.15_Canonical_Ticket_Update_Pack_v1.0.md`. v1.3-R5 승인본과 2026-09-03 Support Review 승인 기록을 대조하여 체크사항을 보완했다. 이번 작업에서 Runtime 시험을 재실행하지 않았다.

### 🎯 User Story

인프라 담당자로서 승인된 P1 Host에 제한된 Primary/Secondary DNS와 Failover를 제공하고 k8s-api-lb01도 내부 DNS 정본을 사용하도록 한다.

### 📌 Scope

#### In Scope

- dns01/dns02, `fds.internal`, TSIG Transfer, 제한 Query/Recursion
- k8s-api-lb01 `.109` BIND ACL·firewalld IPSet·Resolver·Failover

#### Out of Scope

- Reverse/PTR, DNSSEC, 완전한 Authoritative/Recursive 분리, Hybrid DNS

### 📋 핵심 요구사항

- [x] Primary/Secondary·TSIG·기존 Client Failover Technical PASS
- [x] dns01/dns02 ACL과 `fds-dns-clients` IPSet에 `.109` 반영
- [x] k8s-api-lb01 Resolver `.52→.53`, Search Domain `fds.internal`
- [x] `.109` 내부·외부 Query와 Primary 장애 Failover Technical Test
- [x] Management `.10/.20/.30` DNS 필요성·ACL OID-04 결정 — N/A 종결: v3.1.17 §15.1 OID-04 / IF-13M(D36)에 따라 P1 범위 제외, IF-13M 미구현 및 `.10` 제외 유지. 향후 도입은 Change Request 대상이다. 호스트별 ACL 구현·시험 PASS를 뜻하지 않는다.

### ✅ Acceptance Criteria

- [x] 원본 Evidence SHA-256 및 Support Review 승인 — DNS-AC-12/14/16 PASS (2026-09-03 승인본).
- [x] `.109` Positive Test PASS, 비승인 Source Negative Test 유지 — DNS-AC-06/10/11; DNS-NT-01/03; DNS-CR-05 PASS (2026-09-03 승인본).
- [x] Secret/TSIG 원문이 Evidence에 포함되지 않음 — DNS-AC-13 PASS (2026-09-03 승인본).

### 🧪 검증 및 증적

- `docs/evidence/P1-DNS-01/`
- 상세 Description: `P1-DNS-01_Notion_Description_v1.1.md`

### 🔗 Dependency

- `.109` delta 실행 시점: P1-LB-01 Stage A
- Routing/SNAT 변경 시에만 D-NET-01 §15.2 ICR 발행

### ⚖️ Decision / Risk Control

- Decision: `.109`는 실제 LB VM Interface이므로 DNS Consumer로 허용한다.
- Risk Control: `/24` 전체가 아닌 `.109/32`만 추가하고 기존 monitor01 차단을 유지한다.

### 🔍 Review / Handoff

- Review Owner: 이하영
- Handoff: ACL/IPSet·Resolver·Failover Evidence를 P1-LB와 P1-K8S에 전달한다.

### 📝 Completion Record

- Result: DNS 기능·보안·Failover·R2 Evidence Integrity·Runbook·Support Review PASS
- Status: Done
- Completed Date: 2026-09-03
- Reviewer / Approver: 이하영 / 이권욱 — Approved (2026-09-03)

## 승인본의 상세 Acceptance Criteria 보완

| ID | 완료 조건 | 현재 판정 |
|---|---|---|
| DNS-AC-01 | dns01 Primary와 dns02 Secondary가 활성화되고 부팅 시 자동 시작됨 | PASS |
| DNS-AC-02 | 승인된 13개 A Record가 양쪽 권한 서버에서 동일하게 응답함 | PASS |
| DNS-AC-03 | SOA Serial이 `2026090101`로 일치함 | PASS |
| DNS-AC-04 | Fresh HMAC-SHA256 TSIG Transfer가 성공하고 BADKEY/BADSIG가 없음 | PASS |
| DNS-AC-05 | 미인증 AXFR이 실패함 | PASS |
| DNS-AC-06 | 승인 Source만 Query/Recursion과 TCP/UDP 53에 접근할 수 있음 | PASS |
| DNS-AC-07 | `8.8.8.8` Forwarding과 `forward only` 외부 해석이 정상임 | PASS |
| DNS-AC-08 | Primary 중단 중 dns02가 내부·외부 해석을 지속함 | PASS |
| DNS-AC-09 | k8s-control01 Resolver Canary, Rollback, Reapply, Failover가 정상임 | PASS |
| DNS-AC-10 | k8s-api-lb01 `.109`의 ACL/IPSet, Resolver 및 Failover가 정상임 | PASS |
| DNS-AC-11 | monitor01의 직접 내부/재귀 질의가 차단됨 | PASS |
| DNS-AC-12 | 원본 11개, Sidecar 11개, Manifest 12개와 ZIP Sidecar가 검증됨 | PASS |
| DNS-AC-13 | Evidence에 TSIG Secret, Key Hash, 인증 AXFR MAC이 노출되지 않음 | PASS |
| DNS-AC-14 | v1.8 기반 R2가 정본 경로에 반영되고 ZIP SHA-256이 일치함 | PASS |
| DNS-AC-15 | 재실행 가능한 Runbook에 Subshell Guard와 상대 ZIP Sidecar 규칙이 반영됨 | PASS — v1.9 설치/Runbook/Canonical RC 0 |
| DNS-AC-16 | 이하영 Support Reviewer가 정본과 검증 결과를 승인함 | PASS — 2026-09-03 |
| DNS-AC-17 | 전체 6개 Node Resolver 전환의 소유 티켓, 일정, 검증 기준이 명시됨 | PASS |
| DNS-AC-18 | CoreDNS Source 관측과 ACL/ICR 분기 기준이 P1-K8S-01 Handoff로 명시됨 | PASS |

## 체크사항 보완 근거와 후속 작업 (2026-09-09)

- 상세 승인본: `P1-DNS-01_Notion_Description_v1.3_Review.md` (본문 v1.3-R5, 2026-09-03).
- 승인 기록: `P1-DNS-01_Support_Review_Approval_Record_20260903.md`. 이하영 회신만으로 승인을 추정한 것이 아니라 이권욱 Lead의 승인 완료 확정을 함께 기록한 문서다.
- R2 정본 ZIP: `P1-DNS-01-FRESH-20260902-R2.zip`; SHA-256 `e23d02a8422fdc4943ce2e255b5b087f0e58e5ad2a0439ddcf7d041276f315ab`. Raw TXT 11개, Sidecar 11개, Manifest 12개와 ZIP Sidecar 검증 PASS 기록을 대조했다.
- `.109` 증적: `lb/20260902T184256+0900_k8s_api_lb01_evidence.txt`, `failover/20260902T184144+0900_k8s_api_lb01_failover_evidence.txt`. 비승인 Source 증적: `monitor01/20260902T184303+0900_monitor01_negative.txt`.
- 전체 6개 Node Resolver 전환의 실행·멱등성 검증은 [CR-P1-ANS-01-01 #58](https://github.com/321Team/fds-project-baseline/issues/58) 소유다. DNS-AC-17의 PASS는 소유권·일정·검증 기준 Handoff에 대한 판정이다.
- CoreDNS Source 관측과 ACL/ICR 분기는 [P1-K8S-01 #10](https://github.com/321Team/fds-project-baseline/issues/10) 소유다. DNS-AC-18의 PASS는 Handoff 기준 문서화에 대한 판정이며 Runtime 완료를 뜻하지 않는다.
- OID-04는 [v3.1.17 정본 §15.1](https://github.com/321Team/fds-project-baseline/blob/2d93395a0e19ea67e5be199d7183a7edbaa6cf4c/baseline/FDS_Project_Implementation_Baseline_v3.1.17.md)의 OID-04 및 IF-13M(D36) 행에 근거해 P1 N/A로 종결했다. 별도 호스트 허용 승인이나 Runtime PASS를 만들어 넣지 않았다.
````

</details>


</details>

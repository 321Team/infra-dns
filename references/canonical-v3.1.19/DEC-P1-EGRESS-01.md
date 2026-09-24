# DEC-P1-EGRESS-01 — Alertmanager 전용 프록시 배치·예약 IP 사용 결정

> v3.1.19 CANDIDATE / NOT RELEASED · 2026-09-17 20:28 KST

## 현행 속성

| Property | 입력값 |
|---|---|
| Record ID | DEC-P1-EGRESS-01 |
| Phase | Phase 1 |
| Category | Monitoring / Architecture / Egress |
| Type | Decision |
| Status | Done |
| Priority | P1 |
| Start | 2026-09-14 |
| End | 2026-09-21 |
| Calendar Days | 8 |
| Working Days | 6 |
| Lead | 이권욱 |
| Support | 이하영, 이재환 |
| Exit Criteria | 배치·예외 정책 기록, 예약 IP/자산 충돌 확인, 자원 영향 검토, #74/#75 구현·인계 조건 연결 |
| Related Decision IDs | D17; D33; D34; D35 — 기존 의미 유지. 신규 D/IF 순번은 정본 레지스터 대조 후 부여 |
| Related Risk IDs | RISK-04; RISK-07 |
| Source | Baseline v3.1.19 CANDIDATE; GitHub #78 @ 2026-09-16T09:59:18Z; 원문 SHA256 c0c2cb91bc64ffee04373a656451d5e941e7f855ab0e00416fe1667c4a756692 |
| Schedule Note | Decision 범위 종결. 초기 계획 End 2026-09-21은 G2 추적 목표로 보존한다. 배치·정책·예약 IP/자산·자원 영향·#74/#75 구현/인계 조건 확정이 완료되어 2026-09-16 Done 처리한다. #74/#75의 Squid/NetworkPolicy Runtime·독립 리뷰·서비스 인수는 계속 별도 추적하며 본 종결로 완료 처리하지 않는다. 교육장 주말 작업 0 원칙 유지. |

## 상태와 인수 경계

Decision 범위 Done(2026-09-16): .56 전용 배치·정책·예약/자산·자원 영향·#74/#75 인계조건 확정. Squid/NetworkPolicy Runtime 및 G2 승인은 별도.

- GitHub lifecycle: closed; Milestone: G2 Security / Feature Ready
- 일정은 조정 가능한 계획이며 실제 완료일·Gate 승인일과 구분한다.
- 원문·후속 댓글: [원본 티켓](https://github.com/321Team/fds-project-baseline/issues/78), [고정 수집본](https://github.com/321Team/fds-project-baseline/blob/b2e4612cf2e417b10e7f145c5b1e5f58dbe1b948/tickets/v3.1.19/sources/issue-78.json).
- 상위 속성표는 이 후보의 현행 표다. 아래 원문은 수집 시점의 변경/승인/AC 이력이며 과거 버전 문구를 현재 발행 상태로 사용하지 않는다.

## 원문 보존

<details>
<summary>수집한 GitHub 본문 전체 — SHA256 c0c2cb91bc64ffee04373a656451d5e941e7f855ab0e00416fe1667c4a756692</summary>

<!-- fds-decision-close:20260916:start -->
## 결정 범위 종결 — 2026-09-16 KST

**판정: Done / completed. DEC-P1-EGRESS-01의 승인된 Decision Exit Criteria 충족.**

- **배치·예외 정책 기록:** server08의 비-K8S 전용 VM `egress-proxy01`, CentOS Stream 10 + Squid, `10.1.93.56/24`, `.57` 예비, Alertmanager 전용 제한 egress 및 `discord.com:443` CONNECT 범위를 결정·기록했다.
- **예약 IP/자산 충돌 확인:** 프로젝트 보유·타 담당자 예약 없음과 전원 꺼진 VM 포함 `.56` 기존 설정 없음에 대한 사용자 확인을 남겼고, 2026-09-14 14:18~14:19 KST LAN 검사에서 `.56/.57` 각각 ARP DAD 3회 송신/0회 응답/rc=0, 할당 직전 16:45:58~16:46:04 KST 재검사에서도 중복 미관측을 확보했다. 이는 검사 시점의 중복 미관측으로 한정한다.
- **자원 영향 검토:** server08 자원 실측, 추가 예정 VM 없음, Harbor/DB 동시 변경 작업창 부재를 확인했고 실제 VM 2 vCPU/2 GiB/30 GiB 구성과 `.56` 주소·DNS·관리 경로까지 후속 기록됐다.
- **#74/#75 구현·인계 조건 연결:** #74는 Squid 서버/endpoint·실제 Source·서비스 인수, #75는 selector/NetworkPolicy/Secret·허용/거부/복구 및 발송 시험 책임으로 분리·연결했다. 이 두 구현 티켓의 Runtime/독립 리뷰는 계속 별도 추적한다.
- Native Type=`Decision`, Milestone=`G2 Security / Feature Ready`도 현재 GitHub 속성과 정합화됐다.

따라서 #74/#75의 실제 Squid·NetworkPolicy 완료를 #78의 추가 AC로 확대하지 않는다. **본 종결은 Decision 범위 완료이며 #74/#75 Runtime PASS, G2 PASS 또는 Monitoring 인수 완료를 의미하지 않는다.**
<!-- fds-decision-close:20260916:end -->

---

<!-- fds-egress-review:20260915-pr12:start -->
## PR #12 최신 수정본 검토 — 2026-09-15 / ab48f52

검토 HEAD `ab48f5258bb80b17c858fbfb68b992d0a69bfe62`, open/미병합. 930b903 이후 커밋4개(7b17c2d/de98239/746385b/ab48f52)를 대조했다. [공식 REQUEST_CHANGES](https://github.com/321Team/infra-ansible/pull/12#pullrequestreview-5206541386)는 **2026-09-15 15:50:58 KST** 등록. [DR01–DR08 통합 추적 댓글](https://github.com/321Team/infra-ansible/pull/12#issuecomment-5674377321)을 같은 ID로 갱신한다.

- **새 코드 수용:** DR01 add/remove 전체 rule 일치(8개 대조군), DR02 {},[]·외부 host/change 거절, DR03 -n 역조회 차단(ACL 모델10), DR06 IP/CIDR 범위(원문 조건식12), DR07 config4조합·기존 설치 service 사후 대조, DR08 모든 non-localhost recap·localhost-only 거절·run/입력hash/rc·finalize 표시. DR05 NO_PROXY/curlrc 수정 수용 유지.
- **DR07/P1 잔여:** active+disabled에서는 enable 변경만으로 start.changed=true가 되어 reload를 생략하고 새 checksum을 기록한다. 다음 실행도 stale 상태를 유지한다. apply M→rollback O→같은 입력 apply M도 rollback이 marker를 무효화하지 않아 reload를 생략한다. 원문 task/실제 Ansible 모듈+합성 systemctl·localhost marker copy 근거이며 실제 Squid 장애 관측은 아니다.
- **DR02/P1 잔여:** 식별자만 맞고 필드/규칙 이력이 없는 baseline을 수용하고, force:false 제거로 orphan 원본 A를 B로 덮어쓴다. 원본 보존·불일치 거절·schema/백업 일치 검증, standalone verify 입력 연결·baseline 전환 안내가 필요하다.
- **DR04/P1 잔여:** 원문 Host 헤더가 남아 있으며 %<A 추가로 비노출 기준을 충족하지 않는다. 공식 logformat상 %<A는 서버 FQDN/peer 이름, %<a가 실제 서버/peer IP다. 현재 주석의 의미와 보장을 정정해야 한다.
- **DR06/DR08 잔여:** 소수 port·client/domain dict를 수용, candidate diff/실측근거 미완료. 같은 timestamp의 독립 실행 로그 덮어쓰기와 정확한 expected target 집합 대조가 남는다. DR01 원래 규칙 보존 확인 및 DR07 신규 설치 사후 서비스·config hash/mode 검사도 통합 기준에 유지한다.
- **본문 갱신 수용:** .56 확정, handler 참조 제거, 실제 apply HOLD는 반영됐다. “대상 미정” 불일치는 해소. 다만 작성자 15:47:01 종합 보고의 코드 전 항목 완료와 본문의 승인됨/실측만 잔여 표현은 현재 코드 반례·REQUEST_CHANGES와 구분해야 한다.
- **검증 수준:** PR13파일+ansible.cfg blob 일치. de98239 48개, 746385b delta31개, ab48f52 delta17개 기록은 PASS/반례/모형/동일성 확인을 구분한 증적이다. 합산 전체 PASS 수가 아니다. syntax-check4/bash 및 변경된 apply syntax/bash 재확인. check runs/statuses 각각0. 실제 Squid parser/firewalld/lab apply·verify·rollback NOT RUN.
- **인계:** 관리 계정 svc SSH/Ansible/root become PASS·비-K8S .56 배치 유지. **Squid apply HOLD**, 실제 Source와 #74 서비스 인수 후 #75 운영 적용. 기존 AC·담당·일정 기록은 당시 시점 이력으로 보존한다. GWONUK 측 AI 보조 검토이며 이재환님의 승인을 대신하지 않는다. PR #9는 ICR #14에서 대응한다.
<!-- fds-egress-review:20260915-pr12:end -->

---

<!-- fds-spec-audit:20260914:v1:start -->
## 사양·기록 전수 점검 후속 — 2026-09-14 점검 반영

사용자 “각 티켓에 내용 갱신” 지시에 따른 기록 보완. 재대조: `2026-09-14T15:11:45+00:00`. 발행 [docs-v3.1.18](https://github.com/321Team/fds-project-baseline/releases/tag/docs-v3.1.18)과 후속 결정·현재 Issue/PR를 기준으로 한다.

**이 티켓의 점검 결과:** 배치/IP 결정과 실제 구성은 기록됨. As-built/IF·svc 권한 인계 및 native Type/Milestone ; A07/R06.

- .56 자산 예약/꺼진 VM 미사용의 사용자 확인과 할당 전 DAD·자원/작업창 확인은 이미 기록됐다. 다시 모두 미확인으로 되돌리지 않는다. .57은 예비 유지, P0 작업 충돌 시 유예, 18:30은 최초 작업창 이력이며 이후 지속 가능 지시를 따른다.

**프록시 As-built·운영 계정 인계 (A07)** — server08/egress-proxy01·2vCPU/2GiB/30GiB·ens160 .56/24·DNS .52/.53, DNS UDP/TCP4/4와 관리 .10→.56:22 runtime/permanent·반환 .10/32 via .58·관리자 SSH 결과를 자산/IP/IF/inventory에 연결한다. 2026-09-15 제출 증적 대조로 프록시 svc_ansible의 공개키 적용·sudo/root become·새 SSH·Ansible module 검증 PASS를 확인했다(단일 호스트, ok=5/failed=0). 권한은 이 프록시의 (root) NOPASSWD: ALL이며 키 접속 Source는 10.250.10.10으로 제한한다. [계정 실행·권한·회수 및 증적 검토](https://github.com/321Team/fds-project-baseline/issues/74#issuecomment-5673246444)를 자산/IP/IF/저장소 inventory에 연결하는 문서 인계는 잔여다. Squid3128 적용은 rollback 결함/리뷰로 HOLD, 실제 Alertmanager source/selector·Secret 참조·허용/거부/복구·#75 인계는 잔여다.
근거: [배치/실측 #78](https://github.com/321Team/fds-project-baseline/issues/78) · [관리 경로](https://github.com/321Team/fds-project-baseline/issues/74#issuecomment-5663718791) · [계정](https://github.com/321Team/fds-project-baseline/issues/74#issuecomment-5663963879) · [변경 요청](https://github.com/321Team/infra-ansible/pull/12#pullrequestreview-5195815386)

**native 속성·보조 ID 매핑 (R06)** — 당시 #78 전체 Issue API에서 native Type/Milestone null을 확인했다. 이후 2026-09-16 사용자 조치로 Native Type=`Decision`, Milestone=`G2 Security / Feature Ready`로 정합화됐다. D/IF는 레지스터 대조 후 번호를 부여한다. P1-MSA-01/P1-DB-03/P1-DB-05는 현재 #15/#11 또는 로컬 세부작업과 매핑한다. 기존 Risk ID의 역사적 참조 제한을 유지하고 실제 위험 수용 전 현행 정의/승인 출처를 고정한다.
근거: [#78](https://github.com/321Team/fds-project-baseline/issues/78) · [DB 보조 ID](https://github.com/321Team/infra-db/issues/1) · [범위 결정 #4](https://github.com/321Team/fds-project-baseline/issues/4)

**인계·관련 티켓:** [#24](https://github.com/321Team/fds-project-baseline/issues/24) · [#74](https://github.com/321Team/fds-project-baseline/issues/74) · [#75](https://github.com/321Team/fds-project-baseline/issues/75).

점검 항목 A01~A07/R01~R06의 전체 대응은 [P1-DOC-01 #24](https://github.com/321Team/fds-project-baseline/issues/24)에서 추적한다. 미완료 티켓의 기록/시험값은 해당 실행·인수 전에 확정할 후속이며, 유예·조건부 P1/P2 항목을 현재 P0 차단으로 추가하지 않는다.

이번 내용 갱신은 기존 AC 체크·Status·Lead/Support·계획 일정·사람의 승인/종결을 변경하지 않는 당시 점검 기록이다. 아래 작성 당시의 미병합·검토대기 표현은 위 최신 확인 및 연결된 근거와 구분한다. 기존 본문·보관 원문·댓글은 보존한다.
<!-- fds-spec-audit:20260914:v1:end -->

---

# DEC-P1-EGRESS-01 — Alertmanager 전용 프록시 배치·예약 IP 사용 결정

## 속성

| Property | 입력값 |
|---|---|
| Record ID | DEC-P1-EGRESS-01 |
| Phase | Phase 1 |
| Category | Monitoring / Architecture / Egress |
| Type | Decision |
| Status | Done |
| Priority | P1 |
| Start | 2026-09-14 |
| End | 2026-09-21 |
| Calendar Days | 8 |
| Working Days | 6 |
| Lead | 이권욱 |
| Support | 이하영, 이재환 |
| Exit Criteria | 배치·예외 정책 기록, 예약 IP/자산 충돌 확인, 자원 영향 검토, #74/#75 구현·인계 조건 연결 |
| Related Decision IDs | D17; D33; D34; D35 — 기존 의미 유지. 신규 D/IF 순번은 정본 레지스터 대조 후 부여 |
| Related Risk IDs | RISK-04; RISK-07 |
| Source | 사용자 2026-09-14 “위 권장안 적용하고 예비 주소 사용을 위한 체크”; 발행 docs-v3.1.18; #74/#75; infra-ansible PR #12; 2026-09-14~15 실행·증적; 사용자 2026-09-16 전수 종결 지시 |
| Schedule Note | Decision 범위 종결. 초기 계획 End 2026-09-21은 G2 추적 목표로 보존한다. 배치·정책·예약 IP/자산·자원 영향·#74/#75 구현/인계 조건 확정이 완료되어 2026-09-16 Done 처리한다. #74/#75의 Squid/NetworkPolicy Runtime·독립 리뷰·서비스 인수는 계속 별도 추적하며 본 종결로 완료 처리하지 않는다. 교육장 주말 작업 0 원칙 유지. |

## 사용자 결정 적용

이권욱의 위 지시로 권장안의 배치·범위·운영 원칙을 채택한다. 독립 기술 리뷰나 실제 Runtime PASS를 대신하지 않는다.

- server08 위 비-K8S 전용 VM `egress-proxy01`, CentOS Stream 10 + Squid를 채택한다. 기존 3CP+3Worker 유지.
- `10.1.93.56/24`를 이 VM의 조건부 사용 대상으로 지정하고 endpoint는 `http://10.1.93.56:3128`로 계획한다. `.57`은 예비 유지하며 자동 전환하지 않는다.
- .56은 정본 v18의 Reserved에서 출발한다. **자산·예약 충돌, 실제 중복 IP, server08 자원/Harbor·DB 영향 확인 전 NIC에 할당하지 않는다.** 이 기록은 당시 결정 단계의 조건이며 이후 실제 할당·연결 결과는 아래 최신 진행 기록을 따른다.
- GW .254, 내부 DNS .52/.53은 기존 정본을 따른다. 실제 연결 interface와 관리 Source/Return Path는 실측한다.
- Alertmanager만 승인 프록시와 필요한 CoreDNS에 접근하고, 프록시는 discord.com:443 CONNECT만 허용한다. 다른 Pod/서비스의 일반 외부 egress로 확대하지 않는다.
- 합성 장애의 최소 alert 정보만 Discord로 전송한다. 업무·고객 데이터, 전체 로그, 자격증명 제외. Webhook URL은 Git/댓글/증적에 기록하지 않는다.
- #74/#75 기존 Lead 이하영 / Support 이재환 유지. Secret 생성·재발급은 이하영, 설정 인계·검증은 이재환의 기존 역할을 따른다. 실제 Discord 권한 확인 후 노출·담당 변경·단계 인계 시 폐기/재발급한다.
- P1 부가기능·비차단 범위 유지. P0 ICR/K8S·Harbor·CICD 작업창과 충돌하면 프록시 적용을 유예한다. 교육장 주말 작업 0.

## 2026-09-14 실행 착수 후속 기록

[사용자 작업창 확인](https://github.com/321Team/fds-project-baseline/issues/78#issuecomment-5659801981)에 따라 이번 확인 이후부터 **18:30 KST까지** server08 신규 VM 준비에 착수한다. 초기 구성은 **egress-proxy01 / 2 vCPU / RAM 2 GiB / 신규 디스크 30 GiB**, 첫 단계는 NIC 연결 해제 상태의 VM 생성·하드웨어 확인이다. 당시 VM 생성 전 안내이며, 이후 VM 생성·OS 부팅·주소 반영 결과는 아래 최신 진행 기록을 따른다. .56 할당은 잔여 자산 대조·할당 직전 DAD·관리 경로 확인 후 진행하고, Squid 적용은 PR #12 잔여 복원 결함 수정·독립 리뷰 이후 진행한다. 이번 작업창은 Harbor/DB 변경 작업이 없다는 확인이며 기존 서비스 중지를 뜻하지 않는다.

**최신 진행 — 2026-09-15 관리 계정 검증 반영:** [관리 계정 실행 증적 검토 PASS](https://github.com/321Team/fds-project-baseline/issues/74#issuecomment-5673246444). 계정 외 기존 네트워크·DNS·시간 결과는 2026-09-14 제출 증적 기준이다. [#74 관리 경로·영구 설정](https://github.com/321Team/fds-project-baseline/issues/74#issuecomment-5663718791) 및 [계정 준비 후속](https://github.com/321Team/fds-project-baseline/issues/74#issuecomment-5663963879)을 따른다.

| 구분 | 확인 결과 |
|---|---|
| 배치·주소 | server08 / 비-K8S egress-proxy01 / 2 vCPU·2 GiB·30 GiB / CentOS Stream 10 / ens160 10.1.93.56/24. 기본 GW .254, DNS .52/.53, .57 예비 유지 |
| 링크·DNS | VMware Connected 보완 후 UP/LOWER_UP·carrier=1 및 GW ping 3/3 성공. 양 DNS에 .56 BIND ACL·firewalld ipset runtime/permanent 반영, 프록시 UDP/TCP 4/4 질의 성공 |
| 시간 | chronyc refresh 후 선택 소스·Leap Normal·System clock synchronized=yes 확인. 고정 NTP 정책·장기/재부팅 후 지속성은 미검증 |
| 관리 경로 | ansible01 10.250.10.10 → mgmt-gw01 → 10.1.93.56:22 허용을 만료 없는 runtime/permanent에 반영. 반환 /32 경로 via .58을 NetworkManager에 저장. autoconnect=yes, 관리자 SSH 로그인 성공 |
| Ansible 준비 | 2026-09-15 svc_ansible 공개키·sudo 적용 및 새 SSH 확인(10.250.10.10 → 10.1.93.56:22). core 2.16.19로 단일 호스트 module·hostname·Python 명령·root become/assert 5개 통과(ok=5, changed=0, unreachable=0, failed=0). 키 Source 제한 from=10.250.10.10,restrict 및 (root) NOPASSWD: ALL. 기존 Python 3.12.13 확인 이력 유지; 이번 로그는 정확한 버전 문자열 미출력. 저장소 inventory·As-built/Interface 문서 연결은 잔여 |
| 서비스 인계 | http://10.1.93.56:3128 계획 유지. PR #12의 09-15 당시 리뷰/미병합 상태는 이력이다. 09-16에는 PR #12가 병합됐고 후속 hardening은 PR #18 및 증적 PR #13으로 계속 추적한다. 실제 Alertmanager client Source·Squid 서비스 인수·#75 운영 인계는 미완료이며 #74/#75 책임으로 유지한다. |

초기 NO-CARRIER·DNS 실패·NTP 미동기화·SSH timeout은 장애 이력으로 보존한다. **18:30 KST는 최초 작업창의 이력이며, 이후 사용자 “지속적으로 가능” 지시에 따라 같은 프록시 준비 범위의 후속 작업을 계속한다.** P0 작업 충돌 시 유예 원칙은 유지한다. VMware Connect at power on과 재부팅 후 지속성은 별도 확인 대상이다.

## 실측·실행 전 조건

- [x] .56/.57 프로젝트 보유·타 담당자 예약 없음 확인 — [2026-09-14 이권욱 확인](https://github.com/321Team/fds-project-baseline/issues/78#issuecomment-5659762020)
- [x] .56이 전원 꺼진 VM을 포함한 기존 VM에 설정되어 있지 않음 — [2026-09-14 이권욱 확인](https://github.com/321Team/fds-project-baseline/issues/78#issuecomment-5660803134); 사용자 확인 근거이며 도구를 통한 개별 VM 전수 검사로 표현하지 않음
- .57은 예비 유지. 이번 기존 사용 여부 확인은 .56에 한정하며 .57 실제 사용은 이번 실행 범위에 포함하지 않음
- [x] ansible01에서 조정하고 k8s-worker03(.108)/ens160에서 10.1.93.0/24 직접 연결·ARP 제어 응답 확인 — 2026-09-14 14:18~14:19 KST [실측 증적](https://github.com/321Team/fds-project-baseline/issues/78#issuecomment-5659409112)
- [x] .56/.57 ARP DAD 원문·시각·interface·source·종료 코드 확보 — 각 3회 송신/0회 응답/rc=0, 검사 시점 중복 미관측 [실측 증적](https://github.com/321Team/fds-project-baseline/issues/78#issuecomment-5659409112)
- [x] server08 CPU/RAM/디스크 여유 및 Harbor/DB 변경창 영향 확인 — [자원 실측](https://github.com/321Team/fds-project-baseline/issues/78#issuecomment-5659640955), [db01 경로 조회](https://github.com/321Team/fds-project-baseline/issues/78#issuecomment-5659726278), [추가 예정 VM 없음](https://github.com/321Team/fds-project-baseline/issues/78#issuecomment-5659762020), [2026-09-14 이번 확인 후~18:30 KST Harbor/DB 작업 없음·착수 가능: 이권욱 확인](https://github.com/321Team/fds-project-baseline/issues/78#issuecomment-5659801981); P0 작업 충돌 시 유예 원칙 유지
- [x] .56을 egress-proxy01 전용으로 용도 예약, .57 예비 유지 — [기존 채택안 및 타 예약 없음 확인에 따른 기록](https://github.com/321Team/fds-project-baseline/issues/78#issuecomment-5659762020)
- [x] .56 실제 할당 전 LAN DAD 재검사 — [2026-09-14 16:45:58~16:46:04 KST 증적](https://github.com/321Team/fds-project-baseline/issues/78#issuecomment-5660735779), 제어 응답 확인 및 중복 미관측
- [x] .56 실제 주소 반영 및 실행 결과 기록 — [제출 화면](https://github.com/321Team/fds-project-baseline/issues/78#issuecomment-5660971381)의 ens160에 10.1.93.56/24, DNS .52/.53, public zone 확인; 통신 성공 판정과 구분
- [x] ens160 링크 및 게이트웨이 통신 정상화 — VMware NIC Connected 보완 후 UP/LOWER_UP·carrier=1, .254 ping 3/3 성공. 이전 NO-CARRIER는 장애 이력이며 [#74 최신 실행 현황](https://github.com/321Team/fds-project-baseline/issues/74)을 따른다.
- [x] 현재 시간 동기화 확인 — 2026-09-14 20:00:38 KST 제출 화면에서 Asia/Seoul, chrony 선택 소스·Leap Normal·synchronized=yes. 복구 전 게스트 시각은 미동기화 이력이며 전체 과거 시각의 정확성·고정 NTP 정책·장기 지속성을 인증하지 않는다.
- [ ] **구현 후속(#74/#75):** Alertmanager 실제 client Source·3128 최소 허용·신규 Interface 인계 및 #74 Squid 서비스 인수
- [ ] **구현 후속(#74/#75):** PR #18 후속 hardening·독립 리뷰, #75 endpoint/TLS/Secret/NetworkPolicy·발송/거부/복구 인계

위 두 미체크 항목은 #74/#75의 구현·Runtime 후속이며 **DEC-P1-EGRESS-01의 Decision 종결조건을 확대하지 않는다.**

ARP 무응답은 그 시점의 중복 미관측이다. 꺼진 VM·다른 L2·분리된 네트워크의 미사용을 증명하지 않는다. .56 응답 또는 오류가 있으면 적용을 중단하고 원인을 확인한다. .57은 검사하더라도 즉시 사용 승인된 대체 주소가 아니다.

## 인계

#74는 서버·proxy endpoint·실제 Source·Squid 서비스 인수, #75는 실제 selector·NetworkPolicy·Secret·발송/거부/복구 시험을 담당한다. #75 초안은 병행 준비할 수 있으나 운영 적용은 #74 인수 후 진행한다. **본 Decision은 종결하고 구현 일정·완료 판정은 #74/#75에서 계속 추적한다.**

다른 권장안인 Harbor 유한 만료/Scanner 유지와 CI Threshold는 #13/#16에 별도 사용자 결정 기록으로 연결한다. NTP 수치·CP2 정리·Runtime 실행창은 실측 후 결정하며 새 값을 추정하지 않는다.

정본 v18은 소급 수정하지 않는다. 승인된 결정·검사·인계를 v19 수집 PR #73에 연결한다. 본 Decision 종결은 #74/#75 Runtime 완료, G2 PASS 또는 Monitoring 인수 완료를 뜻하지 않는다.

## Completion Record

- **Result:** Done — 프록시 배치·예외 정책, `.56` 예약/충돌 확인, server08 자원 영향, #74/#75 구현·인계 조건 확정 및 연결 완료
- **Status:** Done
- **Completed Date:** 2026-09-16 KST
- **Reviewer / Approver:** 이권욱 — 사용자 전수 종결 지시 및 Decision 범위 판정; #74/#75의 독립 기술 승인과 구분
- **Residual / Next:** #74 Squid 서비스 인수, #75 NetworkPolicy/Secret/발송·거부·복구 Runtime 및 관련 독립 리뷰

</details>

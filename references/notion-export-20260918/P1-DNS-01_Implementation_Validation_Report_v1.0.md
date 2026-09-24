# P1-DNS-01 구현·검증 결과 및 Lead 의사결정안

## 1. 문서 통제

| 항목 | 값 |
|---|---|
| 문서명 | P1-DNS-01 구현·검증 결과 및 Lead 의사결정안 |
| 버전 | v1.0 |
| 작성일 | 2026-09-01 |
| Record ID | P1-DNS-01 |
| Lead | 이권욱 |
| Support Reviewer | 이하영 |
| 구축 대상 | dns01 `10.1.93.52` / dns02 `10.1.93.53` |
| Zone | `fds.internal` |
| 기준 OS | CentOS Stream 10 |
| 권고 상태 | **In Review** |

## 2. 결론

P1-DNS-01의 기능 및 보안 Acceptance Criteria는 제출된 실행 결과 기준으로 모두 충족했다. dns01 Primary와 dns02 Secondary가 정상 작동하고, TSIG 기반 Zone Transfer, 승인 Source 제한, 외부 Forwarding, Primary 장애 시 Secondary 전환, Client Resolver Canary 및 Rollback을 검증했다.

따라서 Lead는 P1-DNS-01 상태를 `In Progress`에서 **`In Review`로 전환**하는 것을 권고한다. `Done` 전환은 Support Reviewer의 증적 검토 및 아래 비차단 후속항목의 처리방향 기록 후 수행한다.

본 결과는 P1-DNS-01 모듈에 대한 Technical PASS이며, G1 전체 Gate PASS를 의미하지 않는다.

## 3. 초기 장애 및 원인 분석

### 3.1 dns02 SSH 실패

| 현상 | 원인 | 조치 | 결과 |
|---|---|---|---|
| dns01에서 dns02 SSH 비밀번호 인증 실패 | `ssh 10.1.93.53` 실행 시 로컬 사용자 `server01_dns01`이 원격 사용자로 자동 사용됨 | 실제 dns02 계정 `server08`을 명시 | 복구 |

근거 로그는 `Invalid user server01_dns01 from 10.1.93.52`였다. 네트워크와 SSH 서비스 장애가 아니라 사용자명 불일치였다.

### 3.2 Secondary Zone 미로딩

| 현상 | 직접 원인 | 근본 원인 |
|---|---|---|
| dns02 `rndc zonestatus fds.internal` → `zone not loaded` | Primary `.52:53` 도달 실패 | dns01의 BIND Primary가 미구축 상태였음 |
| dns02 SOA Query → `SERVFAIL` | Secondary Zone 파일 미수신 | dns01 `named.service` 미존재/비활성, TCP·UDP 53 미리스닝 |

dns01에 Primary BIND를 구축하고 방화벽을 승인 Source 기반으로 허용한 후 문제가 해소됐다. TSIG는 전송 계층 복구 후 적용했으며, 기존 장애는 TSIG 인증 이전 단계의 문제였다.

## 4. 최종 구현 상태

### 4.1 DNS 배치

| 서버 | IP | 역할 | 서비스 상태 |
|---|---:|---|---|
| dns01 | `10.1.93.52` | Primary | Enabled / Active |
| dns02 | `10.1.93.53` | Secondary | Enabled / Active |

### 4.2 Zone 및 Record

- Zone: `fds.internal`
- Serial: `2026090101`
- TTL: 300초
- SOA Refresh/Retry/Expire/Negative TTL: `300 / 120 / 604800 / 300`
- Reverse/PTR: `N/A — Phase 1 Out of Scope`

| FQDN | IP |
|---|---:|
| `dns01.fds.internal` | `10.1.93.52` |
| `dns02.fds.internal` | `10.1.93.53` |
| `edge.fds.internal` | `10.1.93.50` |
| `vpn-gw.fds.internal` | `10.1.93.51` |
| `harbor.fds.internal` | `10.1.93.54` |
| `db.fds.internal` | `10.1.93.55` |
| `control01.fds.internal` | `10.1.93.102` |
| `control02.fds.internal` | `10.1.93.103` |
| `control03.fds.internal` | `10.1.93.104` |
| `worker01.fds.internal` | `10.1.93.105` |
| `worker02.fds.internal` | `10.1.93.107` |
| `worker03.fds.internal` | `10.1.93.108` |
| `k8s-api.fds.internal` | `10.1.93.109` |

### 4.3 보안 통제

| 통제 | 구현 결과 |
|---|---|
| SELinux | Enforcing 상태 유지 |
| Zone Transfer | HMAC-SHA256 TSIG 필수 |
| 미인증 AXFR | 차단 |
| Query/Recursion ACL | 승인 Source IP 명시 방식 |
| Open Resolver | 비승인 Source 차단 |
| External Forwarder | 승인값 `8.8.8.8`, `forward only` |
| Host Firewall | firewalld IPSet + Rich Rule |
| 광범위한 DNS Service | dns01/dns02 모두 비활성(`query-service=dns → no`) |
| Secret 보호 | TSIG Secret 및 인증 데이터 Evidence 평문 기록 금지 |

### 4.4 승인 DNS Source

현재 IPSet 및 BIND ACL에 다음 12개 Source가 반영됐다.

```text
10.1.93.50
10.1.93.51
10.1.93.52
10.1.93.53
10.1.93.54
10.1.93.55
10.1.93.102
10.1.93.103
10.1.93.104
10.1.93.105
10.1.93.107
10.1.93.108
```

`k8s-api 10.1.93.109`는 VIP이므로 DNS Query Source ACL에는 포함하지 않고 A Record로만 관리한다.

## 5. 검증 결과

| Test ID | 검증 항목 | 기대 결과 | 실제 결과 | 판정 |
|---|---|---|---|---|
| DNS-PT-01 | dns01 내부 A/SOA Query | 권한 응답 | `NOERROR`, `aa`, Serial 일치 | PASS |
| DNS-PT-02 | dns02 내부 A/SOA Query | 권한 응답 | `NOERROR`, `aa`, Serial 일치 | PASS |
| DNS-PT-03 | External Forwarding | 승인 외부 Query 성공 | dns01/dns02 모두 `NOERROR`, `ra`, `ad` | PASS |
| DNS-PT-04 | TSIG AXFR/Secondary Transfer | 인증 전송 성공 | TSIG `fds-transfer-key`, Serial `2026090101` 전송 성공 | PASS |
| DNS-PT-05 | Primary 장애 Failover | dns02가 내부·외부 질의 유지 | dns01 중지 중 dns02 정상 응답 | PASS |
| DNS-NT-01 | 비승인 Source 내부 Query | 차단 | monitor01 `.30` → `host unreachable` | PASS |
| DNS-NT-02 | 미인증 AXFR | Transfer 거부 | `Transfer failed` | PASS |
| DNS-NT-03 | 비승인 Source 재귀 Query | 차단 | monitor01의 `example.com` 질의 차단 | PASS |
| DNS-NT-04 | Reverse/PTR | N/A | P1 Scope Out | N/A |
| DNS-CR-01 | Client Resolver Canary | FQDN/Short/External 정상 | k8s-control01에서 모두 정상 | PASS |
| DNS-CR-02 | Client Resolver Rollback | 기존 `8.8.8.8` 복원 | 사설 FQDN `NXDOMAIN`, 외부 Query 정상 | PASS |
| DNS-CR-03 | Client Resolver 재적용 | `.52 → .53` 적용 | NetworkManager/`resolv.conf` 정상 | PASS |
| DNS-CR-04 | Client 자동 Failover | `.52` 장애 후 `.53` 사용 | tcpdump로 `.52` 실패 후 `.53` 질의·응답 확인 | PASS |

## 6. Failover 증적 요약

### 6.1 DNS Service Failover

dns01의 `named`를 중지한 상태에서 dns02가 다음을 모두 처리했다.

- `k8s-api.fds.internal → 10.1.93.109`
- `fds.internal SOA → Serial 2026090101`
- `example.com → 외부 A Record`

dns01 복구 후 Primary SOA와 Notify가 정상화됐다.

### 6.2 Client Resolver Failover

k8s-control01의 최종 Resolver는 다음 순서다.

```text
search fds.internal
nameserver 10.1.93.52
nameserver 10.1.93.53
```

dns01 중지 중 패킷 관측 결과:

1. Client `.102`가 dns01 `.52`에 Query
2. 응답 실패 후 dns02 `.53`으로 동일 Query 재시도
3. dns02가 내부 A Record와 외부 재귀 응답 반환

따라서 직접 Secondary Query뿐 아니라 실제 System Resolver의 자동 전환까지 검증됐다.

## 7. Rollback

### 7.1 Client Resolver Rollback 기준

```text
DNS: 8.8.8.8
DNS Search: 없음
ignore-auto-dns: yes
```

Rollback 후 사설 FQDN은 `NXDOMAIN`, 외부 DNS는 정상임을 확인했으며 이후 내부 DNS를 최종 재적용했다.

### 7.2 DNS Server Rollback 자산

- dns01: `/root/p1-dns-01-backup-20260901/named.conf.factory`
- dns02: `/root/p1-dns-01-backup-20260901/named.conf.pre-tsig`
- k8s-control01: `/root/p1-dns-01-backup-20260901/fds-k8s-control01.nmconnection.pre-dns`

백업은 각 서버의 root 전용 경로에 보관한다.

## 8. Lead 의사결정 및 권장안

### 8.1 상태 전환

**권장: `P1-DNS-01 → In Review`**

근거:

- 핵심 Positive/Negative Test 전부 PASS
- Primary/Secondary/TSIG/Firewall/Forwarding 정상
- 실제 Client Resolver Canary 및 Rollback 검증 완료
- Reverse/PTR은 승인된 P1 Scope Out

### 8.2 `Done` 전 필수 확인

1. 이하영 Support Reviewer가 본 문서와 원본 Evidence의 일치 여부를 확인한다.
2. TSIG Secret 및 AXFR 출력의 TSIG 서명 줄이 Evidence에서 제거·마스킹됐는지 확인한다.
3. dns01/dns02 설정 파일 및 Zone 파일의 무결성 Hash를 별도 Evidence로 남긴다. Hash에는 Secret 파일을 포함하지 않는다.
4. Client Resolver의 전체 배포 범위와 자동화 방식을 Completion Record에 명시한다.

### 8.3 Resolver 전체 배포

수동 변경은 k8s-control01 Canary까지만 허용한다. 나머지 승인 Host에는 동일 설정을 Ansible로 배포하여 구성 편차를 방지한다.

- P1-DNS-01: Resolver 목표값, 대상, Acceptance 및 Rollback 소유
- Ansible: 승인된 자동화 수단으로 사용
- CoreDNS: P1-K8S-01에서 실제 Pod/Node/SNAT Source를 관측한 뒤 ACL 연계

### 8.4 Management VM ACL

| 대상 | 권장안 |
|---|---|
| `ansible01 10.250.10.10` | FQDN 기반 자동화 사용이 확정될 때 개별 허용 |
| `cicd-runner01 10.250.10.20` | P1-CICD-01에서 API/Harbor FQDN 사용이 확정될 때 개별 허용 |
| `monitor01 10.250.10.30` | 외부 Watchdog 역할이므로 계속 차단 |

`10.250.10.0/24` 전체 허용은 금지한다. Source 관측 결과 monitor01의 실제 Source는 `.30`으로 보존됐으며 SNAT은 발생하지 않았다. 따라서 현재 D-NET ICR은 불필요하다.

## 9. 비차단 후속항목

| 항목 | 영향 | 권장 처리 |
|---|---|---|
| BIND 기본 `max-cache-size 90%` | 약 3.2GB 상한으로 소규모 P1 DNS에 과도할 수 있음 | P1 초기값 `256M` 적용 여부를 Lead가 결정하고 부하 기준으로 조정 |
| DNS 서버의 `cockpit` Firewall Service | DNS 이외 관리면 노출 | P1-LNX/P1-SEC Host Hardening 검토. 본 티켓에서 임의 제거 금지 |
| k8s-control01의 비활성 NM Profile | `fds-dns01`, `fds-vpn-gw01` 파일 존재 | P1-LNX 구성 정합성 후속 점검. 확인 전 삭제 금지 |
| CoreDNS Source | Pod/Node/SNAT Source 미확정 | P1-K8S-01에서 관측 후 ACL 변경 |
| Management Consumer | `.10`, `.20` 사용 필요성 미확정 | 해당 후속 티켓에서 FQDN 사용 확정 시 개별 추가 |

위 항목은 현재 P1-DNS-01 Technical PASS의 차단 사유가 아니다. 단, 처리방향은 Completion Record에 남긴다.

## 10. Evidence 보안 규칙

- `/etc/named/keys/fds-transfer.key` 내용은 출력·캡처·Hash Evidence 대상에서 제외한다.
- 인증 AXFR 결과의 마지막 TSIG Record는 다음처럼 마스킹한다.

```text
fds-transfer-key.  0  ANY  TSIG  <REDACTED>
```

- Cookie, TSIG 서명, 사용자 비밀번호, SSH 인증정보는 Evidence에서 제거한다.
- Zone Record와 설정 정책은 기록하되 Secret 값은 기록하지 않는다.

## 11. 최종 판정

| 구분 | 판정 |
|---|---|
| 기능 검증 | PASS |
| 보안 통제 검증 | PASS |
| 장애복구 검증 | PASS |
| Client Canary/Rollback | PASS |
| Reverse/PTR | N/A — P1 Out of Scope |
| P1-DNS-01 권고 상태 | **In Review** |
| G1 전체 Gate | 별도 Gate 평가 필요 |

---

## 릴리즈 노트

| 버전 | 일자 | 변경 내용 | 배포 상태 |
|---|---|---|---|
| v1.0 | 2026-09-01 | Primary/Secondary BIND 구축, TSIG Zone Transfer, Source ACL/Firewall, Forwarding, Failover, Client Canary/Rollback 검증 결과 및 Lead 의사결정안 작성 | 리뷰 배포 |

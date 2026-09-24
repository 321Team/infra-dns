# 정본 기준 DNS 범위

조회일: 2026-09-18T10:18:01+09:00. [발행 v3.1.19](https://github.com/321Team/fds-project-baseline/blob/966fc5365874b1d259a9810fc876b57c3bfa0e08/baseline/FDS_Project_Implementation_Baseline_v3.1.19.md), [P1-DNS-01 #12](https://github.com/321Team/fds-project-baseline/issues/12) 및 보관된 승인 기록을 대조했다. 아래 값은 근거 문서의 합의이며 이번 작업에서 Runtime을 새로 관측한 값이 아니다.

## Phase 1

- dns01 `10.1.93.52` / server01 Primary, dns02 `10.1.93.53` / server08 Secondary, BIND `fds.internal`.
- `cluster.local`은 Kubernetes/CoreDNS 소유다. BIND만 외부 `8.8.8.8`에 forward-only로 전달하는 정본 경계를 유지한다.
- TSIG HMAC-SHA256 인증 전송, 미인증 AXFR 차단, 승인 Source별 제한 Query/Recursion/Transfer 및 TCP/UDP 53 통제를 유지한다.
- [2026-09-03 승인 기록](../references/approved-20260903/P1-DNS-01_Notion_Description_v1.3_Review.md)의 13 A Record와 SOA serial `2026090101`은 당시 상태다. 현재 배포 파일이나 고정해야 할 최신 serial로 사용하지 않는다.
- 이후 egress-proxy01 `.56`의 양 DNS ACL·firewalld ipset runtime/permanent 및 UDP/TCP 4/4 결과는 [DEC-P1-EGRESS-01 #78](https://github.com/321Team/fds-project-baseline/issues/78) / #74의 후속 변경이다. [관련 정본 기록](../references/canonical-v3.1.19/DEC-P1-EGRESS-01.md)을 함께 읽는다. 이것만으로 `.56` A Record가 추가됐다고 추정하지 않는다.
- Management `.10/.20/.30`의 직접 DNS는 IF-13M/OID-04 P1 N/A 기준을 유지한다. monitor01 직접 질의 거부와 관리망 전체 허용을 혼동하지 않는다. CoreDNS의 BIND 도착 Source 관측은 P1-K8S-01에서 확인하고 필요한 고정 /32 변경을 연결한다.
- 클라이언트 Resolver 전환은 [CR-P1-ANS-01-01 #58](https://github.com/321Team/fds-project-baseline/issues/58)과 infra-ansible 책임으로 유지한다.
- Reverse/PTR, DNSSEC, 완전한 authoritative/recursive 분리는 P1 범위에 추가하지 않는다.

## Phase 2

[D23 / DEC-P2-DNS-01 #40](https://github.com/321Team/fds-project-baseline/issues/40)의 조건부 Hybrid DNS 결정과 [P2-DNS-01 #48](https://github.com/321Team/fds-project-baseline/issues/48)을 따른다. P0 IP endpoint 허용과 Non-blocker 구분을 유지한다. 저장소 개설만으로 VPN/Forwarding/Resolver의 새 주소·제품·방식을 확정하지 않는다.

P1-DNS-01의 2026-09-03 Done과 원 승인 이력은 보존한다. Source 입수 미완료와 당시 Runtime 인수 상태는 별개다.

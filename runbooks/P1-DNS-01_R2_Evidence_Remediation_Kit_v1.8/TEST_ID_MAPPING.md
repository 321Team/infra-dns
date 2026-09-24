# P1-DNS-01 정본 Test ID–Evidence 매핑

| Test ID | 검증 항목 | R2 Evidence |
|---|---|---|
| DNS-PT-01 | dns01 내부 A/SOA 및 승인 Record | `dns01/*_dns01_evidence.txt`, `inventory/*_dns_record_inventory_evidence.txt` |
| DNS-PT-02 | dns02 내부 A/SOA 및 승인 Record | `dns02/*_dns02_evidence.txt`, `inventory/*_dns_record_inventory_evidence.txt` |
| DNS-PT-03 | dns01/dns02 External Forwarding | `dns01/*_dns01_evidence.txt`, `dns02/*_dns02_evidence.txt` |
| DNS-PT-04 | HMAC-SHA256 TSIG Zone Transfer | `tsig/*_dns02_fresh_tsig_evidence.txt` |
| DNS-PT-05 | Primary 장애 중 Secondary 서비스 | 두 Consumer Failover 파일 및 `recovery/*_dns01_recovery_evidence.txt` |
| DNS-NT-01 | 비승인 Source 내부 Query 차단 | `monitor01/*_monitor01_negative.txt` |
| DNS-NT-02 | 미인증 AXFR 거부 | dns01/dns02 정상 상태 Evidence |
| DNS-NT-03 | Open Resolver 차단 | `monitor01/*_monitor01_negative.txt` |
| DNS-NT-04 | Reverse/PTR | N/A — Phase 1 Out of Scope |
| DNS-CR-01 | k8s-control01 Resolver Canary | `client/*_k8s_control01_evidence.txt` |
| DNS-CR-02 | Public Resolver Rollback | `rollback/*_k8s_control01_rollback_evidence.txt` |
| DNS-CR-03 | 승인 Resolver 재적용 | Rollback 및 Client 정상 상태 Evidence |
| DNS-CR-04 | k8s-control01 자동 Failover | `failover/*_k8s_control01_failover_evidence.txt` |
| DNS-CR-05 | k8s-api-lb01 `.109` Resolver/ACL/IPSet/Failover | LB 정상·Failover 및 dns01/dns02 Evidence |
| DNS-EV-01 | dns01 원본·Sidecar | dns01 및 Inventory Evidence |
| DNS-EV-02 | dns02 원본·Sidecar | dns02 및 Fresh TSIG Evidence |
| DNS-EV-03 | 중앙 무결성 | `EVIDENCE_INDEX.md`, `SHA256SUMS`, ZIP Sidecar |

`DNS-CR-05`는 R1에서 `.109` Source의 양쪽 DNS Query, Resolver 설정, ACL/IPSet 반영 및 `.52→.53` Failover가 모두 확인됐으므로 R2 정본에서는 `PASS`로 갱신한다.


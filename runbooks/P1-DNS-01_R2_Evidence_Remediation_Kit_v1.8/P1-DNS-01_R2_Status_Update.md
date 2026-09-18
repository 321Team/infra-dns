# P1-DNS-01 R2 증적 보완 상태 업데이트

> 실행 기준은 v1.8이다. v1.6은 배포 파일 목록 불일치, v1.7은 중앙 Hash Script 제공·실행 경로 설명 누락으로 폐기한다. R1 ZIP·R1 Sidecar·v1.8 Kit ZIP·v1.8 Kit Sidecar 네 파일을 모두 확보한 뒤 착수한다.

## 현재 판정

| 항목 | 상태 |
|---|---|
| DNS 기능·보안·HA | Technical PASS |
| Fresh R1 무결성 | PASS — Raw 9/9, Sidecar 9/9, 중앙 Hash 9/9 |
| `k8s-api-lb01 10.1.93.109` Delta | PASS |
| DNS-CR-05 | PASS로 갱신 |
| 중앙 취합 Host | `ansible01(10.250.10.10)` / `server01_ansible` |
| 티켓 | In Review 유지 |

## R2 보완 범위

- [ ] `DNS-PT-01/02`, `DNS-EV-01/02`: 승인 A Record 13개를 dns01/dns02 양쪽에서 전수 대조
- [ ] `DNS-PT-04`, `DNS-EV-02`: dns02 Fresh TSIG 재전송 성공을 timestamped 로그로 수집
- [ ] `DNS-EV-03`: Test ID–Evidence Path–SHA-256 인덱스와 중앙 `SHA256SUMS` 생성
- [ ] Secret/TSIG MAC/Key 파일 미포함 검사
- [ ] 이하영 Support Review

## 재실행 제외

- k8s-control01 Failover (`DNS-CR-04`)
- k8s-api-lb01 Failover (`DNS-CR-05`)
- dns01 Recovery
- Resolver Rollback/Restore (`DNS-CR-02/03`)

R1 원본과 Sidecar는 변경하지 않고 R2에 그대로 승계한다.

중앙 작업 Root는 `/home/server01_ansible/p1-dns-01-r2/`, 정본 Evidence 상위 경로는 `/home/server01_ansible/p1-dns-01-r2/docs/evidence/P1-DNS-01/`로 고정한다. Git 저장소는 본 절차의 전제조건이 아니다.

## Done 전환 조건

1. 신규 Inventory와 Fresh TSIG Collector가 모두 PASS한다.
2. `EVIDENCE_INDEX.md`가 전체 Test ID와 실제 상대경로·SHA-256을 연결한다.
3. R2 중앙 `SHA256SUMS`가 모든 원본 11개와 인덱스를 검증한다.
4. R2 ZIP 외부 Sidecar가 일치한다.
5. Support Review가 Secret 미노출 및 원본 일치 여부를 승인한다.

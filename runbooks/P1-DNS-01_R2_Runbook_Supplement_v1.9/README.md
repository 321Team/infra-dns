# P1-DNS-01 R2 Runbook Supplement v1.9

## 목적

본 보완본은 `P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8`의 검증된 Collector와 R2 정본을 변경하지 않고, 실행 가이드에서 확인된 다음 두 문제를 보완한다.

1. 대화형 SSH 터미널에 직접 붙여넣은 `|| exit 1`이 상위 셸을 종료할 수 있는 문제
2. 절대경로로 `sha256sum`을 실행할 때 ZIP Sidecar에 절대경로가 기록되는 문제

## 적용 관계

- v1.8의 Collector 및 검증 스크립트: 계속 사용
- v1.8의 R2 정본 Evidence: 변경 금지
- 터미널 직접 실행 절차: `P1-DNS-01_R2_SAFE_RUNBOOK_v1.9.md`가 우선
- 현재 정본 읽기 전용 재검증: `scripts/validate_canonical_r2_v1_9.sh`
- 본 보완본 자체 정적 검증: `scripts/validate_runbook_v1_9.sh`

## 배포 위치

ansible01에서 다음 위치에 둔다.

```text
/home/server01_ansible/p1-dns-01-r2/kit/P1-DNS-01_R2_Runbook_Supplement_v1.9/
```

## 실행 주체

| 항목 | 값 |
|---|---|
| 서버 | ansible01 |
| 계정 | server01_ansible |
| 시작 디렉터리 | `/home/server01_ansible/p1-dns-01-r2` |
| 정본 경로 | `/home/server01_ansible/p1-dns-01-r2/docs/evidence/P1-DNS-01` |

dns01, dns02, k8s-api-lb01 또는 Kubernetes Node에서 본 보완본을 실행하지 않는다.

## 현재 정본 기준값

| 항목 | 값 |
|---|---|
| Run ID | `P1-DNS-01-FRESH-20260902-R2` |
| Raw TXT | 11 |
| TXT Sidecar | 11 |
| Manifest 항목 | 12 |
| ZIP SHA-256 | `e23d02a8422fdc4943ce2e255b5b087f0e58e5ad2a0439ddcf7d041276f315ab` |
| DNS-EV-03 | PASS |

## 실행 여부

현재 R2 정본은 이미 검증됐으므로 Collector, TSIG, Failover, Recovery, Rollback 및 정본 승격을 다시 수행하지 않는다. Support Review 전에는 읽기 전용 정본 검증만 허용한다.

## Release Note

| Version | Date | 변경 내용 |
|---|---|---|
| v1.9 | 2026-09-03 | 대화형 셸 종료 방지, 서버·계정·실행 디렉터리 명시, 상대 ZIP Sidecar 규칙, 정본 읽기 전용 검증 및 중단 기준 추가 |


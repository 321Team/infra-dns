# P1-DNS-01 R2 파일 구분표 v1.8

## 1. 사용자에게 별도로 제공되는 배포 파일

| 파일 | 필수 | 설명 |
|---|---:|---|
| `P1-DNS-01-FRESH-20260902-R1.zip` | 예 | R2의 입력으로 승계할 검증 완료 R1 Evidence |
| `P1-DNS-01-FRESH-20260902-R1.zip.sha256` | 예 | R1 ZIP 외부 무결성 Sidecar |
| `P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8.zip` | 예 | 본 Kit |
| `P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8.zip.sha256` | 예 | Kit ZIP 외부 무결성 Sidecar |

R1 ZIP과 R1 Sidecar는 본 Kit ZIP 내부에 포함되지 않는다. Windows Host에서 위 네 파일을 같은 `packages` 디렉터리에 준비해야 한다.

## 2. Kit ZIP 내부 파일

| 파일 | 설명 |
|---|---|
| `README.md` | 범위와 보안 원칙 |
| `FILE_MANIFEST.md` | 제공·내부·생성 파일 구분표 |
| `R2_REMEDIATION_RUNBOOK.md` | Host·계정·실행 디렉터리를 포함한 실행 가이드 |
| `P1-DNS-01_R2_Status_Update.md` | 티켓 상태 갱신 문안 |
| `TEST_ID_MAPPING.md` | Test ID 매핑 |
| `PACKAGE_CONTENT_SHA256SUMS` | Kit 내부 파일 무결성 목록 |
| `scripts/collect_dns_record_inventory_evidence.sh` | dns01 Record Inventory 수집 |
| `scripts/collect_dns02_fresh_tsig_evidence.sh` | dns02 Fresh TSIG 수집 |
| `scripts/generate_evidence_index.sh` | ansible01 Evidence Index 생성 |
| `scripts/generate_checksums_r2.sh` | ansible01 R2 내부 Hash 생성·검증 |
| `scripts/validate_r2_package.sh` | ansible01 제출 ZIP 최종 검증 |

## 3. 실행 후 생성되는 파일

| 위치 | 생성 파일 |
|---|---|
| dns01 `output/inventory/` | `<timestamp>_dns_record_inventory_evidence.txt`와 동일 이름 `.sha256` |
| dns02 `output/tsig/` | `<timestamp>_dns02_fresh_tsig_evidence.txt`와 동일 이름 `.sha256` |
| ansible01 R2 작업본 | `EVIDENCE_INDEX.md`, `SHA256SUMS` |
| ansible01 정본 경로 | `P1-DNS-01-FRESH-20260902-R2/`, 동명 `.zip`, `.zip.sha256` |

Collector 결과와 최종 R2 산출물은 배포 시점에 제공되는 파일이 아니다. 각 지정 Host에서 절차를 수행한 후 생성된다.

`scripts/generate_checksums_r2.sh` 자체는 실행 후 생성되는 산출물이 아니다. v1.8 Kit에 포함된 배포 파일이며, ansible01에서 Kit를 압축 해제하면 `/home/server01_ansible/p1-dns-01-r2/kit/P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8/scripts/generate_checksums_r2.sh`로 배치된다.

# P1-DNS-01 R2 Evidence Remediation Kit v1.8

이 패키지는 Fresh R1 검수에서 확인된 증적 추적성 3건만 보완한다.

1. 승인된 13개 A Record를 dns01/dns02 양쪽에서 전수 대조한다.
2. dns02에서 현재 작업 세션의 TSIG Zone Transfer 성공 로그를 타임스탬프와 함께 수집한다.
3. 기존 Test Matrix와 실제 Evidence 경로·SHA-256을 연결한 `EVIDENCE_INDEX.md`를 생성한다.

기존 R1의 Failover, Recovery, Resolver Rollback은 기술·무결성 검수가 완료됐으므로 다시 실행하지 않는다. 원본 파일과 Sidecar를 수정하지 않고 그대로 R2에 승계한다.

실행 순서는 `R2_REMEDIATION_RUNBOOK.md`를 따른다. v1.8은 중앙 취합 Host를 `ansible01(10.250.10.10)`로 고정하고, dns01·dns02 수집 경로와 Windows WinSCP 중계 경로를 분리한다. Git 저장소를 전제로 하지 않는다. 모든 Script는 입력·출력 Root를 명시적으로 전달해야 하며 암묵적인 `$PWD` 기본 경로를 사용하지 않는다.

`generate_checksums_r2.sh`를 포함한 5개 Script는 ansible01에서 수기로 생성하지 않는다. 모두 Kit ZIP의 `scripts/`에 포함되며, Kit Sidecar와 `PACKAGE_CONTENT_SHA256SUMS` 검증 후 사용한다. ansible01의 실제 경로와 즉시 실행 블록은 Runbook 4.6 및 9.3 절에 있다.

## 배포 전 필수 확인

이 Kit만으로는 R2 조립을 시작할 수 없다. 사용자에게 별도 제공되는 아래 네 파일을 Windows Host의 동일한 `packages` 폴더에 준비한다.

1. `P1-DNS-01-FRESH-20260902-R1.zip`
2. `P1-DNS-01-FRESH-20260902-R1.zip.sha256`
3. `P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8.zip`
4. `P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8.zip.sha256`

R1 ZIP과 R1 Sidecar는 이 Kit ZIP 내부에 포함되지 않는다. 전체 파일 분류와 생성 시점은 `FILE_MANIFEST.md`를 따른다.

## 파일

| 파일 | 목적 |
|---|---|
| `FILE_MANIFEST.md` | 제공 파일·Kit 내부 파일·실행 후 생성 파일 구분 |
| `scripts/collect_dns_record_inventory_evidence.sh` | 13개 A Record × dns01/dns02 전수 대조 |
| `scripts/collect_dns02_fresh_tsig_evidence.sh` | 승인된 Fresh TSIG 재전송 및 시각 포함 로그 수집 |
| `scripts/generate_evidence_index.sh` | Test ID–Evidence–Hash 인덱스 생성 |
| `scripts/generate_checksums_r2.sh` | R2 필수 11종·Sidecar·중앙 Hash 검증 |
| `scripts/validate_r2_package.sh` | 제출 ZIP과 외부 Sidecar 최종 검증 |
| `TEST_ID_MAPPING.md` | 정본 Test ID 매핑 |
| `P1-DNS-01_R2_Status_Update.md` | Notion 티켓 상태 업데이트 문안 |

## 보안 원칙

- `/etc/named/keys/fds-transfer.key`의 Secret 내용과 파일 Hash는 수집하지 않는다.
- 인증 AXFR의 TSIG Record/MAC을 수집하지 않는다.
- Fresh TSIG는 dns02의 `rndc retransfer`와 timestamped `named` 로그로 증명한다.
- `.txt`, `.sha256`, Markdown 인덱스 외 Secret/Key 파일은 제출 ZIP에 포함하지 않는다.

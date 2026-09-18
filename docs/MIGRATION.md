# 자료 확인과 이관 범위

확인 시각: 2026-09-18T10:18:01+09:00. 사용자가 제공한 공유폴더의 ZIP 2개와 `.zip.sha256` 2개를 읽기 전용으로 복사하여 확인했다. 공유폴더 원본과 기존 GitHub 저장소는 변경하지 않았다.

| 자료 | 실제 SHA-256 | 확인 |
|---|---|---|
| `P1-DNS-01-FRESH-20260902-R2.zip` | `e23d02a8422fdc4943ce2e255b5b087f0e58e5ad2a0439ddcf7d041276f315ab` | 제공 sidecar·2026-09-03 승인 기록과 일치; CRC·내부 Manifest 12개·TXT sidecar 11개 일치 |
| `P1-DNS-01_R2_Runbook_Supplement_v1.9.zip` | `86587f04dba2798ff7e34a7314cce0a87bcb3539c3746de7bcb878c2a2932a07` | 제공 sidecar 일치; CRC·내부 Manifest 4개 일치 |

R2는 Raw TXT 11개, TXT sidecar 11개, `SHA256SUMS`, `EVIDENCE_INDEX.md` 총 24개 파일이며 [기존 증적 commit `90093f881670`](https://github.com/321Team/fds-project-evidence/tree/90093f88167055f81e8789d2a848f44ead0ee9ce/evidence/P1-DNS-01/received-20260907T063705Z/zip-contents)의 24개 Git blob과 모두 일치한다. 새 사본을 증적 저장소에 편입할 필요가 없다.

v1.9는 2026-09-03 README, 안전 실행 Runbook, `validate_runbook_v1_9.sh`, `validate_canonical_r2_v1_9.sh`, `PACKAGE_CONTENT_SHA256SUMS`의 5개 파일이다. [기존 승인 기록](../references/approved-20260903/P1-DNS-01_Notion_Description_v1.3_Review.md)의 이름·설치 경로·기능·R2 해시와 일치한다. 제공 sidecar는 바이트 무결성을 입증하며 작성자 서명은 아니다. 별도로 보존된 과거 승인 문서에 v1.9 ZIP 해시가 직접 기재된 근거는 이번 확인 범위에서 찾지 못했다. 따라서 복원된 당시 보완본 Source로 등록하고 이 PR의 최신 HEAD 독립 리뷰를 받는다.

## 실제 복사와 보존

- `runbooks/P1-DNS-01_R2_Runbook_Supplement_v1.9/` 5개 파일: 원본 바이트 그대로. ZIP의 script 권한 0750 중 Git이 지원하는 실행 비트만 보존(100755); 그룹/other 권한을 Git이 보존한다고 주장하지 않는다.
- `references/canonical-v3.1.19/` 4개 및 `references/approved-20260903/` 1개: commit 고정 snapshot. 상대 Markdown 링크만 원본 commit URL로 변환하며 Manifest에 변환·원본/대상 해시를 모두 남긴다. 과거 CANDIDATE·Support 승인·일정 표현은 새 사실로 수정하지 않는다.
- R2 ZIP·Raw 로그·원 승인 기록의 원본은 증적 저장소와 원 공유 경로에 보존한다. 정본·Ansible Resolver·CoreDNS 구현의 소유권을 가져오지 않는다.
- 원본 v1.9를 수정해 현재 정책을 덮어쓰지 않는다. 현재 승인 절차와 사용 제한은 상위 README·POLICY에서 안내한다.

## 아직 확보하지 못한 실행 Source

| 대상 | 이번 확인 결과 / 후속 인수 조건 |
|---|---|
| dns01/dns02의 `named.conf`·include 파일·Zone 원본 | 두 ZIP에 파일 없음. 과거 로그만으로 배포 파일을 만들어 넣지 않는다. 현재 호스트/시각/경로/serial 및 `.56` 후속 변경을 식별한 Secret 제거본과 Secret 제외 목록이 필요 |
| `P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8` Collector | v1.9 README가 의존성을 참조하지만 두 ZIP에는 없음. 해당 Kit·sidecar와 승인 출처 대조 후 별도 코드 PR |
| v1.9 설치/실행 검증 기록 원본 | 승인 설명에 `P1-DNS-01_Runbook_v1.9_Validation_Record_20260903.md`가 언급됨. 이번 ZIP에는 없음. 과거 RC 0은 승인 기록의 이력이고 이번 서버 실행 결과가 아님 |

기존 저장소 검색은 baseline/evidence/ansible/kubernetes/lb/cicd/monitoring의 조회된 main tree와 일부 코드 검색까지다. 채팅 목록 및 관련 대화 일부도 확인했으며 전체 채팅·모든 저장소를 확인했다고 주장하지 않는다. 이후 사용자가 제공한 원본 ZIP을 직접 검증해 v1.9 Source를 찾았다.

현재 Source 등록의 완료조건은 정확한 이관 Manifest, 정적 검사, 최신 HEAD 독립 리뷰와 PR 병합이다. DNS 설정 전체 이관과 운영 소비자 전환은 위 미확보 항목을 인수하고 별도 영향 검증 후 판단한다.

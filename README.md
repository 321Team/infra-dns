# infra-dns

Phase 1 BIND Primary/Secondary DNS의 구현 Source와 Runbook 저장소다. Private / 기본 브랜치 `main`을 유지한다. 요구사항·AC의 정본은 [fds-project-baseline](https://github.com/321Team/fds-project-baseline), Runtime 원본 증적은 [fds-project-evidence](https://github.com/321Team/fds-project-evidence)가 소유한다.

## 이번 이관

- [v1.9 원본 보완본](runbooks/P1-DNS-01_R2_Runbook_Supplement_v1.9/README.md): Runbook, 검증 스크립트 2개, README, 내부 체크섬을 원본 바이트 그대로 수록했다.
- [정본 기준과 DNS 범위](docs/DNS_SCOPE.md), [운영·리뷰 정책](docs/POLICY.md), [자료 확인 및 남은 이관](docs/MIGRATION.md), [검증](docs/VALIDATION.md).
- [R2 원본 증적](https://github.com/321Team/fds-project-evidence/tree/90093f88167055f81e8789d2a848f44ead0ee9ce/evidence/P1-DNS-01/received-20260907T063705Z/zip-contents)은 기존 증적 저장소에 보존한다. 제공된 R2 ZIP의 24개 파일 모두 해당 commit의 Git blob과 일치한다.
- `references/`는 당시 정본·승인 기록의 출처를 고정한 참고본이다. 최신 결정이나 현재 Runtime 설정으로 취급하지 않는다. 파일별 출처·SHA-256·링크 변환은 [이관 Manifest](docs/MIGRATION_MANIFEST.json)에 기록했다.

- [수동 노션 자료 확인](docs/NOTION_IMPORT.md): Done 본문과 이전 개정 첨부의 차이를 기록하고 역사 참고 문서 3개를 추가했다.

- [서버 수집 기록](docs/SERVER_INTAKE.md): ansible01에서 v1.8 Kit 11개 파일을 확보했고 설치본과 동일성을 확인했다. [보관된 v1.8](runbooks/P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8/README.md)은 Source 이관용이며 이번 수집에서 실행하지 않았다.

## 현재 사용 범위

이 PR은 Source 등록이다. 운영 서버에 설치하거나 DNS 설정·TSIG·Failover를 재실행하지 않았다. 두 서버의 정규화·Secret 마스킹 참고 설정은 [콘솔 수집 기록](docs/SERVER_INTAKE.md)에 있다. 2차 수집으로 [주 Zone 원본](zones/fds.internal.zone)을 확보했고 양쪽 정규화 Zone의 A 13개·내용 동일성을 확인했다. [Zone 수신·이관 판정](docs/ZONE_INTAKE_20260918.md)을 따른다. 원 named.conf/include 구조가 아직 없으므로 운영 배포 구성 전체가 이관됐다고 판단하지 않는다. 마스킹 참고 설정은 배포하지 않는다.

v1.9는 **2026-09-02 R2 묶음 검증 전용**이다. 내부의 고정 해시·11/11/12 개수는 그 묶음에만 적용한다. 현재 DNS 전체 상태를 검사하는 범용 도구가 아니다. 원본 문서의 당시 Support 승인 표현은 역사로 보존하며, 현재 사람 간 승인 절차는 [2026-09-18 정책](https://github.com/321Team/fds-project-baseline/blob/b2e4612cf2e417b10e7f145c5b1e5f58dbe1b948/governance/REVIEW_AUTHORITY_POLICY.md)을 적용한다.

## 로컬 Source 검사

저장소 루트에서 Python 3 및 Bash가 있는 환경으로 실행한다. 서버 접근·관리자 권한·Secret은 필요 없다.

```sh
python3 tools/verify_migration.py
bash runbooks/P1-DNS-01_R2_Runbook_Supplement_v1.9/scripts/validate_runbook_v1_9.sh runbooks/P1-DNS-01_R2_Runbook_Supplement_v1.9
```

두 검사 모두 종료 코드 0이면 이관 무결성·Runbook 정적 검사 성공이다. Runtime·독립 리뷰·병합 완료를 뜻하지 않는다. `validate_canonical_r2_v1_9.sh`는 지정 ansible01 계정과 원본 증적을 필요로 하므로 Source CI에서 실행하지 않는다.

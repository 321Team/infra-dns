# 이관 검증 기록

확인일: 2026-09-18 KST. 환경: Windows 로컬 작업 공간, Python 3, Git for Windows Bash. 공유폴더 원본은 읽기만 했으며 임시 사본에서 검사했다.

## 결과

| 구분 | 수행 내용 | 실제 결과 |
|---|---|---|
| STATIC / 입력 무결성 | ZIP 2개와 사용자가 제공한 sidecar의 SHA-256 및 상대 basename, ZIP CRC | 모두 일치 |
| STATIC / R2 내부 무결성 | Raw TXT 11개, TXT sidecar 11개, 중앙 Manifest 12개 | 해시 23항목 일치; 총 24개 파일 |
| STATIC / 기존 증적 대조 | R2 24개 파일을 evidence commit `90093f88167055f81e8789d2a848f44ead0ee9ce` Git blob과 비교 | 24/24 byte 일치 |
| STATIC / v1.9 내부 무결성 | PACKAGE_CONTENT_SHA256SUMS 4개 | 4/4 일치 |
| STATIC / 원본 및 대상 | Git 원본 5개 blob 검증; 복사 10개 대상 SHA-256; 상대 문서 링크 4개를 원본 commit URL로 변환 | 일치; 변환은 Manifest에 기록 |
| STATIC / 소스 검사 | `python3 tools/verify_migration.py` | RC 0; 10개 이관 파일, UTF-8 및 제한된 credential pattern 검사 통과 |
| STATIC / Runbook | `bash runbooks/P1-DNS-01_R2_Runbook_Supplement_v1.9/scripts/validate_runbook_v1_9.sh runbooks/P1-DNS-01_R2_Runbook_Supplement_v1.9` | RC 0; 두 스크립트 Bash 구문 및 원본 Runbook 규칙 검사 통과 |
| STATIC / 실패 탐지 | 별도 임시 사본에서 이관 README 1개 변조 후 checker 실행 | 예상 RC 1 및 Imported content changed 탐지; 등록 파일에는 변조 없음 |
| CI | 생성 당시 저장소 설정은 조직에서 Actions 비활성; 새 소스 검사 Workflow만 제출 | NOT RUN. 로컬 정적 검사를 CI PASS로 표현하지 않음 |
| MOCK / RUNTIME | dns01/dns02/ansible01 접속·키 변경·Failover·서비스 재시작·운영 배포 | 미실행 |
| REVIEW / MERGE | 코드·Workflow 포함 PR, 최신 HEAD에 대한 작성자 외 독립 검토와 수동 병합 | 이 문서 작성 시 대기; 실제 최신 상태는 PR 참조 |

검사 시간은 2026-09-18 10:14~10:19 KST 범위다. 상세 archive hash·수신 시각·파일별 provenance는 [MIGRATION_MANIFEST.json](MIGRATION_MANIFEST.json), 판정과 잔여는 [MIGRATION.md](MIGRATION.md)에 있다.

## 제한

- `validate_canonical_r2_v1_9.sh`의 ansible01/server01_ansible 가드를 우회해 성공을 만들지 않았다. 이 스크립트의 실제 호스트 RC 0은 이번 검증 결과가 아니다.
- 제공 ZIP sidecar 및 내부 Manifest 일치는 무결성 확인이며 작성자 서명, 최신 Runtime 또는 AC 재인수를 의미하지 않는다.
- 제한된 Secret 패턴 검사 외에도 이번 diff에 실제 TSIG key·private key·인증정보가 포함되지 않는지 검토한다. 패턴 미검출만으로 모든 종류의 비밀정보 부재를 보증하지 않는다.
- 정적 검증 범위를 넘어 스크립트의 전체 실패 경로를 새로 시험하지 않았다. v1.9의 실행 로직은 원본 그대로다. 이관 독립 검토자는 복원 출처·용도 제한·원본 동일성을 함께 확인한다.
- named.conf·Zone·v1.8 Collector 미확보는 [남은 이관 항목](MIGRATION.md)에 명시했다. 현재 운영 DNS 구성 전체 복제나 배포 가능 상태를 주장하지 않는다.

## 노션 자료 추가 검증 — 2026-09-18

- Export ZIP CRC 정상; 수신 파일 5개의 SHA-256 계산 및 문서·이미지 확인.
- 승인 회신 PNG의 SHA-256은 해당 Approval Record 기재값과 일치하며, Approval Record 자체는 앞서 공유폴더에서 받은 파일과 동일하다. 회신만으로 이번 PR의 독립 승인을 추정하지 않는다.
- 역사 문서 3개 추가 후 이관 검사 RC 0: imported files 13개 / UTF-8 source files 25개. 원본 바이트·제한된 credential pattern 및 로컬 문서 링크 확인.
- 노션 본문 Done, 첨부 v1.3-R2 In Review 및 v1.0의 .109 제외를 대조하고 [적용 기준 차이](NOTION_IMPORT.md)를 명시했다. 기존 v1.3-R5 및 최신 정본을 변경하지 않았다.
- 기존 Runbook 실행 코드·검증 도구·Workflow는 변경하지 않았다. 이번 추가는 문서/Manifest이며 전체 PR의 코드 포함 분류는 유지한다. 최신 HEAD의 독립 리뷰·병합은 PR 상태로 확인한다.
- CI/RUNTIME 재실행 없음. 설정 원본·Collector·v1.9 실행 검증 원본 문서는 이번 Export에도 없어 미확보를 유지한다.

## 서버 v1.8 Kit 추가 — 2026-09-18 10:50 KST

- 기존 SSH/SCP 인증과 호스트 키 검증으로 ansible01에서 ZIP/sidecar를 읽기 전용 수신했다. ZIP hash·CRC·내부 Manifest 10항목 일치, 설치본 11개 전부 byte 일치.
- 원본 스크립트 5개 `bash -n` 구문 검사 RC 0. Collector 기능, 재전송, index/checksum 생성은 실행하지 않았다.
- 11개 Source를 Manifest에 추가했다. 위 절의 v1.8 미확보 표기는 당시 이력이며 현재 v1.8은 확보됐다. named.conf/Zone 및 v1.9 원본 실행 검증 기록은 계속 미수집이다.

## 현장 콘솔 1차 수신 및 2차 수집기 — 2026-09-18 11:10~11:15 KST

- STATIC: dns01/dns02의 SHA256SUMS 대상 6개씩 총 12개 전부 일치. 원본 14개와 스크린샷 2개는 로컬 보존, 정규화·마스킹 참고 설정 2개만 소스 경로에 바이트 그대로 추가했다. 최종 이관 파일 26개 / UTF-8 source 42개 검사 RC 0.
- CONTENT: 양쪽 ACL의 14개 IPv4와 runtime/permanent ipset이 일치하고 `.109`/`.56`을 포함한다. zonestatus serial은 양쪽 2026090101이다. Zone 내용, 레코드 개수, 실제 방화벽 enforcement는 이 자료만으로 PASS 처리하지 않는다.
- STATIC: 새 Python 수집기의 구문 검사. 고정 Zone 경로만 조회하고 실제 config/root 확인, masked config hash 일치, symlink·journal·dynamic·include·파일/serial/process 변경 시 중단하도록 검토했다. 원본 v1.8/v1.9 스크립트와 CI Workflow에는 변경이 없다.
- MOCK: 외부 명령을 대체한 14개 시나리오 통과(두 호스트 정상/secondary raw fallback, chroot, 설정 변경, symlink, Secret, include, dynamic, journal, sudo 거부, 파일 변경, serial 변경, PID 변경, Zone 검사 실패). 별도 process config 인자 거부 3건 통과. stderr 및 가상 Secret 값이 산출물에 저장되지 않음을 확인했다. 이 테스트의 Zone 출력은 가상 자료이며 운영 증적이나 저장소의 Zone Source로 사용하지 않는다.
- RUNTIME: 1차 사용자 수신 관찰 자료만 확보. 2차 수집기와 실제 BIND binary 검사·기능 시험은 서버에서 미실행. CI는 별도 확인하며 검사 0건을 PASS로 표시하지 않는다. 최신 HEAD 독립 REVIEW·MERGE는 미완료다.
- 알려진 제한: 프로세스 실행 인자와 디스크 설정을 확인해도 모든 in-memory 설정이 현재 디스크와 같다고 입증하지 않는다. 정상 수집 표시는 AC 인수가 아니다. 원 named.conf/include 구조와 v1.9 과거 검증 원본은 계속 미확보다.

## 2차 콘솔 Runtime 수신 및 Zone 편입 — 2026-09-18 12:26~12:34 KST

- RECEIPT/STATIC: 호스트별 원 Manifest 23개씩 총 46개 일치. 두 SESSION의 Collector SHA-256은 제공한 091ecee Source와 일치한다. 실제 private key/TSIG key 및 그 hash를 수집하지 않았고 제한된 민감정보 패턴을 점검했다.
- RUNTIME 관찰(사용자 제출 원본): BIND 9.18.33, 실제 config `/etc/named.conf`, process root `/`, 고정 Zone 경로 확인. dns01 text RC 0 / dns02 text 시도 RC 1 후 raw RC 0. 두 상태 COMPLETE_COLLECTION_ONLY 및 수집 전후 stat/PID/serial 변경 미관측. 자세한 원 명령·RC·시각은 evidence PR #16에 있다. 전체 argv와 stderr 미저장 제한을 유지한다.
- CONTENT: 정규화 Zone 양쪽 882 bytes byte-identical, SHA-256 `7161d50eaaed299d4cc14eb409a5351e7c260aff572db04e8a3802c97c09b954`. A 13개 이름·주소를 승인 R5 문서 표와 직접 대조해 일치, NS 2/SOA 1/TTL 300/serial 2026090101 확인. 실제 네트워크 질의·전송 시험은 아니다.
- FIREWALL: 양쪽 zone 설정 및 DNS rich rule/ipset 일치. runtime/permanent의 active/interface 표기 차이는 기록하고 NM 지속성·dns service 정의·policy/direct/kernel 규칙·실제 패킷 시험 미확인 범위를 분리했다.
- SOURCE STATIC: 가져온 파일 28개 / UTF-8 source 45개 이관 검사 RC 0. Python 구문과 로컬 문서 링크 확인. 주 Zone 변조 시 hash 오류 RC 1, 미등록 Zone 추가 시 inventory 오류 RC 1을 격리 사본에서 확인했다. 기존 이관 원본과 Collector 코드는 변경하지 않았다.
- EVIDENCE: 원본 64개 + 관리 자료 3개를 증적 commit `f5f1537408a17672aed8581e7cbe2962bd4951f5`에 등록. 원격 67개 blob/mode 일치, 기존 680개 blob/mode 불변. PR #16 독립 검토 요청, 미병합.
- CI·독립 REVIEW·MERGE는 각 PR의 실제 상태를 따른다. 새 서버 기능 시험/변경/재시작, AC 전체 재인수, 정본 발행, 기존 Done 티켓 재종결은 수행하지 않았다. 앞 절의 2차 서버 미실행 표기는 수신 전 이력이며 이번 실제 실행본 수신으로 갱신됐다.

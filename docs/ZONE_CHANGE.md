# Zone Source 변경 절차

대상은 주 Zone [zones/fds.internal.zone](../zones/fds.internal.zone)이다. dns02의 Secondary 사본과 [비교용 정규화본](../references/console-20260918/dns02/fds.internal.normalized.reference.zone)은 편집 대상이 아니다. [Zone 수신 기록](ZONE_INTAKE_20260918.md)의 serial `2026090101`은 수신 시점 관찰값이며 고정값이 아니다.

## 저장소 변경

1. 레코드 추가·변경·삭제는 책임 티켓·승인 결정 근거가 있을 때만 한다. ACL/ipset 승인(예: `.56`)을 A Record 추가 근거로 확대하지 않는다.
2. 같은 변경에서 SOA serial을 이전 값보다 크게 올린다. 현재 표기는 `YYYYMMDDnn`이다. serial이 같거나 작으면 Secondary가 전송하지 않는다.
3. `named-checkzone fds.internal zones/fds.internal.zone`이 RC 0이어야 한다. 실행 환경·BIND 버전·RC를 PR에 기록한다.
4. [이관 Manifest](MIGRATION_MANIFEST.json)의 `zones/fds.internal.zone` 항목에서 `destination_sha256`을 새 파일 hash로 갱신하고 `transformation`에 변경 PR·사유를 적는다. `source_*` 필드는 최초 수집 원본의 provenance이므로 수정하지 않는다.
5. `python3 tools/verify_migration.py`가 RC 0이어야 한다.
6. Zone은 운영 DNS가 소비하는 실행 설정이다. [리뷰 정책](REVIEW_POLICY.md)의 코드 PR로 분류해 작성자 외 독립 리뷰 후 Lead가 병합한다. Pre-check 예외 대상이 아니다.

## 운영 반영 — 후속 과제

저장소 병합은 서버 반영이 아니다. dns01 반영 방식(파일 배치·권한·SELinux context·reload), dns02 전송과 serial 확인, 저장소와 서버 간 drift 확인, 중단·복구 기준은 아직 Runbook으로 정의되지 않았다.

정의 전에는 Zone 병합을 운영 반영 완료로 표시하지 않는다. 반영이 필요하면 [운영 정책](POLICY.md)에 따라 Lead가 검토된 SHA·대상·계정·선행조건·성공/중단 기준·복구안을 먼저 고정한다.

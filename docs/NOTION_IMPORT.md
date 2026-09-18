# 수동 노션 자료 추가 확인

수신·확인일: 2026-09-18 KST. 사용자가 제공한 Notion Export ZIP의 문서 4개와 이미지 1개를 확인했다. ZIP CRC 정상이며 SHA-256은 `3147bd95ba6ffa9192a933ef6302f7f7767fa5a441e2f6c64e0c371023b620c8`이다. ZIP 외부 sidecar는 제공되지 않아 이 값은 수신 시 계산값이다.

**노션 본문은 Done까지 갱신됐지만 첨부 문서는 이전 개정이 섞여 있다.** 이 묶음을 통째로 최신 실행 기준으로 채택하지 않는다. 기존 v1.3-R5 승인 참고본·발행 v3.1.19·이후 승인 변경을 유지하고 아래 파일은 과거 기록으로 구분한다.

## 파일별 판정

| 자료 | 확인 결과 | 이번 처리 |
|---|---|---|
| [노션 본문](../references/notion-export-20260918/BIND_Primary_Secondary.md) | Status Done, 완료 2026-09-03, v1.3-R5까지 이력. v1.9 검증 RC 0·.109 ACL 반영 포함 | 원본 바이트의 역사 참고본으로 보관 |
| [구현·검증 보고서 v1.0](../references/notion-export-20260918/P1-DNS-01_Implementation_Validation_Report_v1.0.md) | 작성 2026-09-01, In Review. .109를 Query Source에서 제외하는 초기 판단과 기존 백업 경로 포함 | 과거 보고서로 보관. 현재 설정/새 Runtime 증적으로 사용 금지 |
| [첨부 Description v1.3-R2](../references/notion-export-20260918/P1-DNS-01_Notion_Description_v1.3-R2.md) | 파일명은 v1.3_Review지만 실제 제목은 v1.3-R2, In Review, DNS-AC-15 OPEN·AC-16 PENDING | 개정이 드러나는 파일명으로 원본 보관. 기존 R5를 대체하지 않음 |
| Support Review Approval Record | 2026-09-03 승인 완료를 Lead가 확정했다는 기록. 이전 공유폴더에서 받은 동일 파일과 바이트 일치 | 수신 hash·판정만 기록. 원 승인 증적을 소스 repo에 새 승인으로 복제하지 않음 |
| 승인 회신 PNG | 실제 이미지 확인. SHA-256 `0d0652c6940529e42619adbb54b2444a419fa265bea37dc247f5507c6487c4eb`가 Approval Record 기재값과 일치 | 수신 hash·판정만 기록. 이미지 자체는 로컬 수신본에 보존 |

이미지의 확인 회신 자체에 명시적인 승인 단어가 없다는 점은 원 Approval Record도 구분한다. 과거 최종 승인은 그 기록의 Lead 확정 및 기존 정본 이력으로 해석하며, 이 이미지나 과거 승인을 이번 이관 PR의 독립 승인으로 사용하지 않는다. 원 승인 기록/이미지를 증적 저장소에 편입할 경우 해당 저장소의 독립 리뷰 절차를 적용한다.

## 현재 기준과의 차이

| 과거 문서의 표현 | 현재 적용 기준 |
|---|---|
| v1.0 §4.4: 승인 Query Source 12개, .109 제외 | 후속 R2/R5에서 k8s-api-lb01 .109가 DNS Consumer로 ACL/ipset·Resolver·Failover 검증 대상에 포함됐다. 이후 .56 후속 변경도 별도 유지한다. 초기 12개 목록으로 되돌리지 않는다. |
| v1.3-R2: In Review, Runbook 보완 및 승인 대기 | 노션 본문·기존 R5·P1-DNS-01 정본은 2026-09-03 Done. 과거 첨부파일을 근거로 재개방하지 않는다. |
| 노션 본문: Control Plane/Worker Resolver 전환 계획·미완료 체크 | 이후 CR-P1-ANS-01-01 #58의 완료/증적을 따른다. 노션 당시 체크를 현재 미완료로 복제하지 않는다. |
| v1.0: Management .10/.20 필요 시 개별 허용 권고 | 현행 IF-13M/OID-04 P1 N/A와 관측된 Source·승인 변경을 따른다. 옛 권고만으로 ACL을 확대하지 않는다. |
| 과거 Support 승인 절차, 고정 SOA serial, max-cache-size 권고 | 승인 절차는 2026-09-18 정책, 설정은 현재 승인 Source를 따른다. 이관으로 serial·cache-size를 새로 확정하거나 적용하지 않는다. |

현행 기준은 [DNS_SCOPE.md](DNS_SCOPE.md), [POLICY.md](POLICY.md), [기존 v1.3-R5 승인본](../references/approved-20260903/P1-DNS-01_Notion_Description_v1.3_Review.md)에 연결한다.

## 발견한 경로와 남은 Source

v1.0 §7.2는 아래 **당시 백업** 위치를 적고 있다.

- dns01: `/root/p1-dns-01-backup-20260901/named.conf.factory`
- dns02: `/root/p1-dns-01-backup-20260901/named.conf.pre-tsig`
- k8s-control01: `/root/p1-dns-01-backup-20260901/fds-k8s-control01.nmconnection.pre-dns`

이는 현재 유효 설정의 위치나 내용이 확인됐다는 뜻이 아니다. 특히 factory/pre-tsig는 구축 전 복구 자산이므로 현재 배포용 설정으로 채택하지 않는다. 서버 접근·내용 조회·복구는 이번에 수행하지 않았다.

이번 Export에는 `named.conf`, Zone 원본, v1.8 Collector 실행 파일, `P1-DNS-01_Runbook_v1.9_Validation_Record_20260903.md` 실파일이 없다. 마지막 파일은 문서 안에서 참조될 뿐이다. 구현·검증 보고서도 결과 요약이며 원본 실행 로그와 구분한다. 따라서 [기존 미확보 항목](MIGRATION.md)은 유지한다.

## 검증 범위

원본 3개 문서는 바이트 그대로 보관하고 SHA-256을 Manifest에 추가했다. 추가 자료에 대한 텍스트·이미지 확인, 개정 비교, 제한된 credential pattern 검사, 로컬 이관 검사와 링크 확인을 수행한다. Runtime 재시험·새 독립 승인·티켓 종결을 의미하지 않는다.

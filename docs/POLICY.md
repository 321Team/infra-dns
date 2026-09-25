# DNS 저장소 운영 정책

기준: [발행 정본 v3.1.19](https://github.com/321Team/fds-project-baseline/releases/tag/docs-v3.1.19), 이후 승인 결정, [병합된 리뷰 권한 정책](https://github.com/321Team/fds-project-baseline/blob/b2e4612cf2e417b10e7f145c5b1e5f58dbe1b948/governance/REVIEW_AUTHORITY_POLICY.md). 저장소명·폴더·snapshot-copy는 사용자 요청에 따른 운영 세칙이며 정본의 새 AC가 아니다.

## 소유권

| 대상 | 관리 저장소 / 책임 |
|---|---|
| BIND Primary/Secondary, Zone, DNS ACL, TSIG 참조, 검증·복구 Runbook | `infra-dns`; P1-DNS-01 Lead 이권욱, Support 이하영 유지 |
| 공통 Inventory, OS/VM 자동화, 클라이언트 Resolver, 교차 영역 orchestration | `infra-ansible` 유지 |
| CoreDNS, cluster.local, Kubernetes 내부 DNS·네트워크 정책 | `infra-kubernetes` 유지 |
| AC·Decision·CR·WBS·Release 정본 | `fds-project-baseline` 유지 |
| Runtime 원본 로그·해시·독립 증적 검토 | `fds-project-evidence` 유지 |

이관은 기존 파일 삭제나 운영 소비자 변경을 포함하지 않는다. 소비자 전환은 destination merge SHA, 영향·검증·복구를 명시한 후속 변경으로 처리한다.

## 리뷰·병합

- `main` 직접 push, 자동 병합, force push, main 삭제, 원본 이력 재작성을 금지한다. 작업 브랜치와 PR을 사용한다.
- 코드·스크립트·Workflow·실행 설정 또는 혼합 PR은 작성자 외 적격 검토자 1인의 독립 검토 후 Lead가 병합을 판단한다. 이번 작성 경로는 GWONUK이며 이하영 `hayeounglee`에게 리뷰를 요청한다. AI 점검은 독립 승인이 아니다.
- 문서만 변경하는 PR과 코드 외 실행·인수·종결은 기존 책임 Lead에게 위임한다. AC·시험·보안 통제는 유지한다. `fds-project-evidence`는 문서 포함 모든 PR에 독립 리뷰가 필요한 예외다.
- 병합 직전 최신 HEAD, 승인 대상 SHA, 필수 검사, 미해결 차단사항을 확인한다. Reviewer 지정과 GitHub APPROVED, 실제 Merge를 구분한다.
- 2026-09-23 Pre-check 예외를 포함한 현재 리뷰·병합 기준은 [리뷰 정책](REVIEW_POLICY.md)과 [중앙 정책 §3.2](https://github.com/321Team/fds-project-baseline/blob/49278c189dacb620e81d282c6401faa2a9c677a6/governance/REVIEW_AUTHORITY_POLICY.md)를 따른다. 두 문서가 이 절과 다르면 리뷰 정책이 우선한다. Zone·Workflow·수집기를 포함한 이 이관 PR은 혼합 PR이므로 예외 대상이 아니다.
- branch protection/ruleset·CODEOWNERS는 이번에 적용하지 않는다. 정책 문서만으로 기술적 강제가 활성화됐다고 표시하지 않는다. Private를 유지하고 PR/SHA/독립 리뷰/수동 병합 기록으로 관리한다.

## Secret·Runtime·증적

- TSIG secret, 실제 Key 파일 및 그 파일의 해시, private key, 토큰, 비밀번호, Secret을 포함한 백업, 인증된 AXFR의 TSIG MAC은 저장하지 않는다. TSIG는 비밀값 없이 알고리즘·키 식별자·보관 위치의 참조만 문서화한다. `.gitignore`만 믿지 않고 diff도 확인한다.
- SELinux enforcing, 제한된 방화벽·DNS ACL, 인증 통제를 유지한다. 모든 /24, 관리망, Pod CIDR를 편의상 허용하지 않는다.
- 운영 적용은 검토된 SHA, 대상/계정/권한/경로, 선행조건, 성공·중단 기준, 복구안을 고정하여 해당 Lead가 판단한다. 이관 승인은 서버 적용·키 발급/회전 승인으로 확대하지 않는다.
- STATIC / MOCK / CI / RUNTIME / REVIEW / MERGE / PUBLICATION을 별도로 기록한다. 해시 일치는 무결성, 검사 0건은 CI NOT RUN이다. 새 결과는 호스트·KST 시각·버전·명령·종료 코드·원본 로그·해시를 연결한다.
- 새 Source CI는 GitHub-hosted·contents read·고정 checkout SHA·credential 비보존으로 정적 검사와 모의 시험(`tests/`, 외부 명령을 가짜로 대체하며 서버·네트워크·Secret 불필요)만 한다. 내부 Runner·Secret·배포 권한은 필요 없다. Actions 미실행 시 아래 로컬 검증 결과를 기록하고 CI PASS라고 쓰지 않는다.

복구는 이관 PR의 revert로 저장소 변경을 되돌리는 범위다. 서버를 변경하지 않았으므로 서버 복구를 수행했다고 기록하지 않는다. 이미 Done인 P1-DNS-01은 이관 때문에 재종결하지 않는다.

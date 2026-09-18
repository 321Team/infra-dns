# 서버 Source 수집 기록 — 2026-09-18

## 실제 확보

사용자의 읽기 전용 수집 착수 지시에 따라 기존 SSH 인증·엄격한 호스트 키 검증으로 `server01_ansible@10.250.10.10`에 접속했고 `hostname -s` 결과 `ansible01`을 확인했다. 2026-09-18 10:47~10:50 KST에 아래 자료를 수신·대조했다.

- 원 ZIP/sidecar: `/home/server01_ansible/p1-dns-01-r2/incoming/P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8.zip`, 같은 이름 `.zip.sha256`.
- ZIP SHA-256: `9843c2b2b6f560226a187ec2e970cde06446094d7ec9713bed341f6fd91e4674`. 서버 sidecar와 로컬 수신본 모두 일치.
- ZIP CRC 정상, 내부 Manifest 10항목 일치. 총 11개 파일(스크립트 5개 포함).
- 서버 `/home/server01_ansible/p1-dns-01-r2/kit/P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8/` 설치본 11개와 ZIP의 바이트가 전부 일치한다. 대조 시각: 2026-09-18 10:49:58 KST.
- [이관 위치](../runbooks/P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8/README.md)에 원본 바이트 그대로 보관한다. 원본 배포시 승인 hash가 따로 서명됐다는 주장은 하지 않는다. 기존 승인 기록의 Kit 이름·역할 및 현재 설치본 동일성을 근거로 Source 복원 PR을 검토한다.

## 실행 제한

**v1.8은 과거 R2 증적 보완용 Kit이며 현재 설정 수집기로 실행하지 않는다.** `collect_dns02_fresh_tsig_evidence.sh`는 `rndc retransfer`를 수행하고, index/checksum 생성기는 출력 증적을 작성한다. 이번 작업에서는 어느 Collector도 실행하지 않았다. 로컬 `bash -n`으로 5개 스크립트 구문만 검사하여 모두 RC 0을 확인했다.

과거 R1/R2 증적·백업·stage·sidecar와 설치된 Kit는 변경하지 않았다. 복사한 Source의 이관·PR 병합은 재전송, Failover, TSIG 변경, 서비스 재시작, 증적 정본 승격을 승인하거나 수행한 것이 아니다. 실제 실행에는 상위 POLICY 및 v1.9 보완 Runbook을 함께 적용한다.

## dns01/dns02 현장 콘솔 수신 — 11:05 KST

사용자가 전달한 `dns-source-intake.dns01.Htu9rkHA`와 `dns-source-intake.dns02.qVRcutre`를 읽기 전용 인수했다. SESSION 기준 dns01은 11:05:05 KST / `server01_dns01`, dns02는 11:05:13 KST / `server08`이다. 서버 실행을 에이전트가 직접 관찰한 것은 아니며 명령별 종료 코드 기록은 제공되지 않았다.

각 폴더 7개 파일 중 SHA256SUMS의 대상 6개씩, 총 12개 해시가 일치한다. 원본 파일 14개와 스크린샷 2개는 로컬 수신 경로에 보존했다. [수신 Manifest](CONSOLE_INTAKE_20260918.json)에 모든 파일의 수신 hash·크기·제한을 기록했다. 원본 로그·화면의 증적 저장소 편입은 별도 독립 리뷰 PR로 진행하며 이번 소스 PR에 원본 로그를 혼합하지 않는다.

| 관찰 | dns01 | dns02 |
|---|---|---|
| Zone 역할 / serial | primary / 2026090101 | secondary / 2026090101 |
| Zone 파일 표기 | `fds.internal.zone` | `slaves/fds.internal.zone` |
| 정규화 설정의 directory | `/var/named` | `/var/named` |
| Query/Recursion ACL | loopback + 10.1.93의 지정 IP 14개 | 동일 |
| fds-dns-clients ipset | runtime/permanent 14개 일치 | 동일, dns01과도 일치 |
| active firewalld zone | public / ens160 | public / ens160 |

14개 허용 IP는 `.50 .51 .52 .53 .54 .55 .56 .102 .103 .104 .105 .107 .108 .109`이다. 승인된 `.109` 및 후속 DEC-P1-EGRESS-01의 `.56`을 포함하고, 관리 `.10/.20/.30`이나 전체 /24는 이 ACL/ipset에 없다. 다만 방화벽 rich rule·service·port·다른 경로의 허용 규칙은 미수집이므로 실제 TCP/UDP 53 접근 통제 PASS를 선언하지 않는다. 14개 IP 및 zonestatus의 nodes 14는 A Record 개수의 증거가 아니다.

수신 설정에는 TSIG 식별자 `fds-transfer-key`/`hmac-sha256`이 있으며 secret은 물음표로 마스킹됐다. dns01은 해당 키로 전송을 제한하고 dns02를 notify 대상으로 사용하며 dns02는 dns01을 master로 참조한다. 소스 2개를 아래 경로에 바이트 그대로 보관한다.

- [dns01 참고 설정](../references/console-20260918/dns01/named.expanded.sanitized.reference.conf)
- [dns02 참고 설정](../references/console-20260918/dns02/named.expanded.sanitized.reference.conf)

**배포 금지 참고본:** `named-checkconf -p -x /etc/named.conf`의 include 확장·정규화·마스킹 결과다. 원래 named.conf/include 파일의 경계·주석·바이트를 복원한 파일이 아니며 마스킹된 키로 실제 서비스를 구성하면 안 된다. 한정된 민감정보 패턴 및 TSIG 마스킹을 검사했지만 모든 Secret 부재를 증명하는 검사는 아니다.

화면에서 dns01 MainPID 1266, dns02 MainPID 1482, `/usr/lib/systemd/system/named.service`를 확인했다. ExecStart에는 `${NAMEDCONF}`와 `$OPTIONS`가 남아 있어 실제 프로세스의 config/chroot 경로는 아직 확정하지 않는다. 따라서 Zone의 후보 절대 경로는 각각 `/var/named/fds.internal.zone`, `/var/named/slaves/fds.internal.zone`이며 [2차 수집 절차](DNS_CONSOLE_SECOND_STEP.md)에서 프로세스 경로를 먼저 확인한다. 같은 serial만으로 두 Zone 내용의 동일성 또는 현재 모든 정책의 적용을 입증하지 않는다.

## 남은 수집 사항

- 실제 daemon의 config/chroot 경로, Zone 원본과 비교 가능한 정규화본, 방화벽 규칙 전문, 원 named.conf/include 구조가 남았다. 자동 SSH 인증 거부(RC 255)는 현장 콘솔 수신과 별개의 접속 제한이다. 검증을 끄거나 새로운 키·계정·권한을 설치하지 않았다.
- `/home/server01_ansible/p1-dns-01-r2/` 내 검증 기록 후보 파일명 검색에서 v1.9 실행 검증 원본을 찾지 못했다. 문서의 과거 RC 0 요약을 원본 로그로 바꾸지 않는다. 전체 서버를 검색한 결과라는 뜻도 아니다.
- 2차 수집은 이미 사용 중인 현장 콘솔 경로로 계속한다. private key/TSIG secret/TSIG key 파일 hash는 수집하지 않는다.

## 상태

READ-ONLY INTAKE: v1.8 수신·설치본 대조 및 DNS 1차 콘솔 수신 완료. STATIC: ZIP/Manifest/구문 검사와 콘솔 수신 hash 12개 일치. RUNTIME 관찰: 사용자가 전달한 zonestatus/ipset의 부분 관찰 자료 확보. 새 기능 시험·운영 변경: 미실행. 전체 AC 재검증, CI·독립 REVIEW·MERGE와 구분한다. 소스 등록 PR과 별도의 원본 증적 저장소 편입은 독립 리뷰 절차를 유지한다.

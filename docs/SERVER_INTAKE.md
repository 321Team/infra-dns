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

## 미수집 사항

- dns01/dns02의 현재 named.conf·include·Zone·DNS 방화벽/ipset 설정은 아직 미수집이다. 현재 PC에서는 해당 호스트 키가 미등록이라 strict 검증이 중단됐다. ansible01에는 기존 신뢰 키가 있지만 두 서버의 기존 일반 계정과 svc_ansible 모두 BatchMode 인증 거부(RC 255)였다. 검증을 끄거나 새로운 키·계정·권한을 설치하지 않았다.
- `/home/server01_ansible/p1-dns-01-r2/` 내 검증 기록 후보 파일명 검색에서 v1.9 실행 검증 원본을 찾지 못했다. 문서의 과거 RC 0 요약을 원본 로그로 바꾸지 않는다. 전체 서버를 검색한 결과라는 뜻도 아니다.
- 서버 설정 수집은 기존 접속 경로나 현장 콘솔 확인 후 계속한다. private key/TSIG secret/TSIG key 파일 hash는 수집하지 않는다.

## 상태

READ-ONLY INTAKE: v1.8 수신·설치본 대조 완료. STATIC: ZIP/Manifest/구문 검사 통과. DNS RUNTIME 시험·운영 변경: 미실행. CI·독립 REVIEW·MERGE는 PR의 실제 최신 상태로 구분한다. 소스 등록 PR과 별도의 원본 증적 저장소 편입은 그 저장소의 독립 리뷰 절차를 유지한다.

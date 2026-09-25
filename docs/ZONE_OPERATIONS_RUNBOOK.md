# Zone 운영 반영 Runbook — 초안

상태: **초안(DRAFT). 실행 승인 아님.** 책임 과제: [#5](https://github.com/321Team/infra-dns/issues/5). 저장소 안의 변경 조건은 [ZONE_CHANGE.md](ZONE_CHANGE.md)를 따른다. 이 문서는 그 다음 단계, 즉 병합된 주 Zone을 dns01에 반영하고 dns02 전송과 drift를 확인하는 절차다.

이 문서를 따라 실제로 반영하려면 두 가지가 먼저 있어야 한다.

1. 이 Runbook의 리뷰·병합
2. 반영할 Zone 변경 PR의 독립 리뷰·병합. 그 뒤 Lead가 [운영 정책](POLICY.md)과 중앙 정책 §4에 따라 대상·계정·작업창·성공/중단 기준·복구안을 고정한다.

이 문서의 병합은 운영 반영 승인이 아니다.

## 1. 확인된 사실과 미확인 사항

| 항목 | 값 | 근거 |
|---|---|---|
| 주 Zone 파일 | dns01 `/var/named/fds.internal.zone`, text, `type primary` | 2026-09-18 수집(evidence `source-intake/received-20260918T032605Z`) |
| 부 Zone 파일 | dns02 `/var/named/slaves/fds.internal.zone`, raw, `type secondary` | 같은 수집 |
| 설정 | 실제 config `/etc/named.conf`, process root `/`, BIND 9.18.33 | 같은 수집 |
| 전송·알림 | dns01 `notify yes`, `also-notify { 10.1.93.53 key "fds-transfer-key"; }`, Zone `allow-transfer` TSIG 키 한정. dns02 `masters { 10.1.93.52 key "fds-transfer-key"; }`, `allow-notify` 키 한정 | [마스킹 참고 설정](../references/console-20260918/) |
| SOA 타이머 | refresh 300 / retry 120 / expire 604800 / negative TTL 300, serial 표기 `YYYYMMDDnn` | [zones/fds.internal.zone](../zones/fds.internal.zone) |
| 작업 계정 | dns01 `server01_dns01`, dns02 `server08`(기존 관리 계정, sudo 사용) | [DNS_CONSOLE_SECOND_STEP.md](DNS_CONSOLE_SECOND_STEP.md), 2026-09-24 Lead 확인 |

아래 사항은 **확인되지 않았다.** 반영 전 §3의 읽기 전용 조회로 값을 기록하고, 이 값이 확인되지 않으면 반영하지 않는다.

- Zone 파일의 소유자·그룹·권한·SELinux context. 9/18 수집의 stat 형식에는 이 값들이 없다.
- 원 `named.conf`/include 파일 경계([#6](https://github.com/321Team/infra-dns/issues/6)). 이 Runbook은 Zone 파일만 바꾸며 설정 파일을 건드리지 않는다.

## 2. 사용하는 도구

| 도구 | 실행 위치 | 성격 |
|---|---|---|
| [`tools/collect_dns_zone_readonly.py`](../tools/collect_dns_zone_readonly.py) | dns01, dns02 콘솔 | 읽기 전용 수집기. PR #1 독립 리뷰·병합 코드이며 실행본 SHA-256은 `9458d9aa…`다. 마스킹 설정 hash가 9/18과 다르면 스스로 멈춘다. 이 경우 설정이 바뀐 것이므로 반영을 중단하고 원인을 확인한다 |
| [`tools/compare_zone_drift.py`](../tools/compare_zone_drift.py) | 작업자 PC(로컬) | 수집 결과 폴더와 저장소 Zone을 비교하는 오프라인 비교기다. 서버에 접속하지 않는다. 결과: 0=NO_DRIFT, 2=DRIFT, 1=입력 오류 |

수집기를 운영 서버에서 실행하는 것은 중앙 정책 §3.2 4-1의 순수 검증기 실행에 해당하도록 설계됐다. 서버 변경 없음, 1회 실행, 결과는 작업자 홈에만 남는다. 실행 기록에는 대상 서버, 실행 SHA, 명령, 계정, KST 시각, 판단 근거, 결과 경로를 남긴다.

## 3. 반영 전 확인 (읽기 전용)

1. **반영 대상을 고정한다.**
   - 병합된 Zone 변경 PR의 merge SHA를 `NEW_SHA`로 둔다.
   - 그 직전 main의 Zone을 기준본으로 쓴다(`PREV_SHA`).
   - 저장소에서 다음 파일을 준비한다.
     ```sh
     git show PREV_SHA:zones/fds.internal.zone > prev.zone
     git show NEW_SHA:zones/fds.internal.zone > new.zone
     named-checkzone fds.internal new.zone
     ```
   - `new.zone`의 serial이 `prev.zone`보다 커야 한다.
2. **현재 서버가 기준본과 같은지 확인한다.**
   - dns01·dns02에서 수집기를 각각 1회 실행하고, 결과 폴더 전체를 작업자 PC로 가져온다(`sha256sum -c SHA256SUMS` OK 확인).
   - 로컬에서 다음을 실행한다.
     ```sh
     python3 tools/compare_zone_drift.py --repo-zone prev.zone --dns01 <dns01 폴더> --dns02 <dns02 폴더> --report pre-drift.json
     ```
   - 결과가 `NO_DRIFT`가 아니면 반영하지 않는다. 서버에 저장소 밖 변경이 있었다는 뜻이므로 먼저 원인을 확인한다.
3. **파일 속성을 기록한다.** dns01에서 실행하며, 쓰기는 없다.
   ```sh
   sudo stat -c '%U:%G %a %C %s' /var/named/fds.internal.zone
   sudo ls -ldZ /var/named
   ```
   출력된 소유자·그룹·권한·context를 실행 기록에 적는다. 4-2단계에서 같은 값으로 배치한다.

## 4. 반영 (dns01) — 운영 쓰기 단계

아래는 운영 서버를 바꾸는 단계다. 검토된 SHA와 Lead의 실행 판단이 있어야 한다. 각 명령의 종료 코드를 기록하고, 0이 아니면 거기서 멈춘다.

1. **백업한다.** root 전용 경로를 쓴다.
   ```sh
   sudo install -d -m 0700 /root/dns-zone-backup
   sudo cp -p /var/named/fds.internal.zone /root/dns-zone-backup/fds.internal.zone.<PREV serial>
   ```
2. **새 파일을 임시 이름으로 배치하고 검사한다.** `OWNER`, `GROUP`, `MODE`는 §3-3에서 기록한 값이다.
   - 먼저 `new.zone`을 기존 VM 파일 전달 방법으로 dns01 작업 계정의 홈에 복사한다.
   - 서버에서 `sha256sum new.zone` 값이 저장소의 `git show NEW_SHA:zones/fds.internal.zone | sha256sum` 값과 같은지 확인한다. 다르면 중단한다.
   - 그다음 아래를 실행한다.
   ```sh
   sudo install -o OWNER -g GROUP -m MODE new.zone /var/named/fds.internal.zone.new
   sudo named-checkzone fds.internal /var/named/fds.internal.zone.new
   ```
   검사가 실패하면 `.new` 파일을 지우고 중단한다.
3. **교체한다.** 같은 파일시스템 안의 이름 바꾸기로 교체하고, context를 복원한다.
   ```sh
   sudo mv /var/named/fds.internal.zone.new /var/named/fds.internal.zone
   sudo restorecon -v /var/named/fds.internal.zone
   sudo stat -c '%U:%G %a %C %s' /var/named/fds.internal.zone
   ```
   출력이 §3-3의 값과 같아야 한다. 크기는 새 파일 크기다.
4. **이 Zone만 다시 읽힌다.** 서비스 전체를 재시작하지 않는다.
   ```sh
   sudo rndc reload fds.internal
   sudo rndc zonestatus fds.internal
   ```
   `serial:`이 새 serial이어야 한다.

## 5. 반영 뒤 확인

1. **dns02 전송을 확인한다.** dns01은 notify를 보내고, dns02는 늦어도 refresh(300초)와 retry(120초) 안에 새 serial을 가져와야 한다. dns02에서 다음을 실행한다.
   ```sh
   sudo rndc zonestatus fds.internal
   ```
   **15분** 안에 새 serial이 보이지 않으면 중단 기준에 해당한다.
2. **질의를 확인한다.** 허용 Source 목록(`fds-dns-clients`)에 있는 클라이언트에서 실행한다.
   ```sh
   dig +norec @10.1.93.52 fds.internal SOA
   dig +norec @10.1.93.53 fds.internal SOA
   dig +norec @10.1.93.52 <변경한 이름>.fds.internal A
   dig +norec @10.1.93.53 <변경한 이름>.fds.internal A
   ```
   두 서버 모두 새 serial과 변경한 레코드를 응답해야 한다. SERVFAIL이 없어야 한다.
3. **drift를 확인한다.** 수집기를 다시 실행한 뒤 다음을 실행한다.
   ```sh
   python3 tools/compare_zone_drift.py --repo-zone new.zone --dns01 <폴더> --dns02 <폴더> --report post-drift.json
   ```
   `NO_DRIFT`여야 한다.
4. **기록한다.** 실행 기록, 수집 폴더, `pre-drift.json`·`post-drift.json`을 fds-project-evidence의 새 수집회차로 편입한다(독립 리뷰).

## 6. 중단 기준

다음 중 하나라도 해당하면 추가 쓰기를 멈추고 §7로 판단한다.

- §3에서 `NO_DRIFT`가 아니거나 수집기가 `INCOMPLETE`로 끝남
- `named-checkzone` 실패
- 교체 뒤 소유자·권한·context가 §3-3과 다름
- `rndc reload` 실패, 또는 dns01 serial이 새 값이 아님
- 15분 안에 dns02가 새 serial을 가져오지 않음
- 질의에서 SERVFAIL, 변경하지 않은 레코드의 응답 변화, 또는 `DRIFT`

## 7. 복구

| 시점 | 방법 |
|---|---|
| dns01 교체 전(4-2까지) | `.new` 파일을 지운다. 운영 파일은 바뀌지 않았다 |
| dns01 교체 뒤, **dns02가 아직 새 serial을 가져가지 않음** | 백업 파일을 4-2~4-4와 같은 방식으로 다시 배치하고 `rndc reload fds.internal`을 실행한다. dns01 serial이 이전 값으로 돌아갔는지 확인한다 |
| **dns02가 이미 새 serial을 가져감** | secondary는 serial이 낮아지는 전송을 받지 않는다. 이전 내용에 **새 serial보다 더 큰 serial**을 붙인 복구용 Zone을 [ZONE_CHANGE.md](ZONE_CHANGE.md) 절차로 만들어 이 Runbook으로 다시 반영한다. dns02 사본을 지우고 재전송하는 등 다른 방법은 Lead가 따로 판단한다 |

복구 뒤에도 §5-2·§5-3으로 확인하고 기록한다.

## 8. 남은 사항

- 이 초안은 실제 운영 환경에서 시험되지 않았다. 첫 반영 때는 영향이 작은 변경(예: 새 테스트 레코드 추가)으로 절차를 검증하는 방안을 Lead가 판단한다.
- §1의 미확인 사항(파일 속성, include 구조)이 확인되면 이 문서를 갱신한다.
- 수집기는 9/18 마스킹 설정 hash에 고정돼 있다. 설정을 바꾸는 변경이 생기면 수집기의 고정값을 갱신하는 코드 PR이 먼저 필요하다.

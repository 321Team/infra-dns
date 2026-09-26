# named.conf include 구조·TSIG 키 참조 수집 절차 (#6)

상태: 수집 도구와 절차를 준비했다. **서버 실행 전이다.** 책임 과제: [#6](https://github.com/321Team/infra-dns/issues/6).

## 목적

저장소에 있는 named 설정은 `named-checkconf -p -x`로 펼치고 비밀값을 가린 참고본뿐이다(`references/console-20260918/`, 배포 금지). 이 절차는 원래 설정 파일들이 어떻게 나뉘어 있는지(include 경계), TSIG 키가 어느 파일에 정의되고 어디서 참조되는지를 비밀값 없이 확인한다. 결과는 설정 Source를 저장소에 둘지 판단하는 근거가 된다. 그 판단은 Lead가 한다.

## 도구

[`tools/collect_named_structure_readonly.py`](../tools/collect_named_structure_readonly.py)

- 대상: dns01·dns02. 기존 관리 계정으로 실행한다(dns01 `server01_dns01`, dns02 `server08`). 스크립트 자체를 sudo로 실행하지 않는다.
- 실행 중인 named의 실제 설정 경로가 `/etc/named.conf`인지 확인한다. 이 확인은 기존 수집기의 검증된 함수(`process_config`)를 그대로 쓴다.
- 이어서 그 파일과 include되는 파일을 차례로 **메모리에서만** 읽는다.
- 저장하는 것:
  - `structure.json`: include 트리(파일, 포함한 파일:줄), 파일 속성(종류·소유자·그룹·권한·SELinux context·크기), 최상위 문 목록, 키 정의(이름·알고리즘·줄; 비밀값 없음), 키 참조, 정의 없이 참조된 키 목록
  - `masked/NN-<파일명>`: 각 파일에서 `secret "…"` 값을 `????????`로 바꾼 사본. 길이도 드러나지 않는다.
  - `named.expanded.sanitized.conf`: `named-checkconf -p -x` 출력(참고). 9/18 고정 hash와 같은지 여부를 `structure.json`에 적는다.
  - `SESSION.json`, `COMMANDS.json`(명령·시각·종료 코드), `STATUS.json`, `SHA256SUMS`
- **저장하지 않는 것:** 파일 원문, 비밀값, 원문 파일의 hash, 프로세스 인자 원문, 명령 stderr
- **중단 조건(INCOMPLETE):**
  - 상대 경로 include
  - `/etc/`·`/var/named/` 밖의 include
  - symlink, 같은 파일 두 번 포함(순환 포함)
  - 32개 초과 파일, 깊이 8 초과, 256 KiB 초과
  - 읽는 중 크기 변경
  - 괄호 불균형
  - 가려지지 않은 비밀값, 따옴표 없는 secret, 개인키
  - 수집 중 named PID 변경
  - 중단하면 이미 만든 마스킹 사본도 지운다.
- 서버 변경은 없다. 파일, 서비스, 방화벽, 계정을 바꾸지 않고 reload·restart도 하지 않는다. 결과는 사용자 홈의 새 폴더 `dns-named-structure.<host>.*`에만 남는다. 중앙 정책 §3.2 4-1 순수 검증기 조건에 맞춰 설계했다.

## 실행

1. 병합된 main의 `tools/collect_named_structure_readonly.py`와 `tools/collect_dns_zone_readonly.py`를 기존 VM 파일 전달 방법으로 서버 사용자 홈의 같은 폴더에 복사한다. 앞의 도구가 뒤의 도구에서 함수를 가져오므로 두 파일이 같이 있어야 한다.
2. 서버에서 `sha256sum` 값이 병합 SHA의 파일과 같은지 확인한다.
3. 실행한다.

```bash
cd "$HOME"
hostname -s
sudo -v
python3 ./collect_named_structure_readonly.py
```

4. `COMPLETE_COLLECTION_ONLY`와 `COLLECTED_DIRECTORY=…`가 나오면 그 폴더에서 `sha256sum -c SHA256SUMS`를 실행한다. 모두 OK이면 폴더 전체를 가져온다.
5. `INCOMPLETE_DO_NOT_SUBMIT_AS_COMPLETE`이면 멈춘다. 가드를 고치거나 우회하지 않는다. 사유와 폴더명만 전달한다.

## 실행 기록 (순수 검증기 실행)

실행할 때 다음을 기록한다(중앙 정책 §3.2 4-1).

- 대상 서버
- 실행 SHA(병합 commit, 두 파일의 SHA-256)
- 명령
- 계정
- KST 시각
- 순수 검증기라고 판단한 근거
- 결과 경로

실행 전에 Lead가 코드에 쓰기·재시작·설치 명령이 없는지 확인한다. 이 확인은 독립 코드 리뷰가 아니다.

## 결과 처리

- 결과 폴더는 fds-project-evidence에 새 수집회차(예: `evidence/P1-DNS-01/named-structure-<수신시각>/`)로 편입한다(독립 리뷰).
- `structure.json`을 보고 Lead가 판단한다. 비밀값 없는 설정 파일(예: 키 파일을 뺀 `named.conf`)을 infra-dns Source로 등록할지, 키 파일은 위치·이름·알고리즘 참조만 문서로 남길지 정한다.
- `keys_referenced_but_not_defined`가 비어 있지 않거나, `expanded_matches_20260918_pinned_hash`가 `false`이면 설정이 9/18과 다르다는 뜻이다. 원인을 따로 확인한다.

## 함께 남은 항목

v1.9 Runbook 실행 검증의 원본 terminal log는 이 도구로 얻을 수 없다. 원본 보관 위치를 찾지 못하면 #6에 확보 불가로 기록하고 닫는다.

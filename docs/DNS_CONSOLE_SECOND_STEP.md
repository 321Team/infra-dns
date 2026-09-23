# DNS 콘솔 2차 수집: 실제 Zone과 방화벽 규칙

실행 이력: 2026-09-18 12:24 KST 두 서버의 수집본을 받아 검사했다. [Zone 수신 결과](ZONE_INTAKE_20260918.md)를 참조한다. 이미 완료된 이번 수집을 반복할 필요는 없다. 아래는 사용한 절차의 보존본이다.

수집기는 2026-09-18 1차 마스킹 설정 hash와 호스트별 Zone 경로에 고정된 일회성 도구다. 설정이 바뀌면 의도대로 중단한다. 재사용하려면 고정값을 갱신하는 새 코드 PR을 거친다. 실행본 SHA-256 `9458d9aa60d8589809eadc129cd4186f7084a2eea7fdba8302c5a090ae0e1346`과의 대응을 유지하려고 파일 자체는 수정하지 않는다.

대상은 dns01 / dns02, 계정은 각각 기존 `server01_dns01` / `server08` 관리 계정이다. 콘솔 로그인 상태에서 Python 3, sudo 조회 권한, BIND 도구, firewalld가 필요하다. 작업 경로는 사용자 홈의 새 `dns-zone-intake.<host>.*` 폴더이며 파일 생성 외 서비스·설정 변경은 없다.

## 전달과 실행

1. [collect_dns_zone_readonly.py](../tools/collect_dns_zone_readonly.py) 파일을 기존 VM 파일 전달 방법으로 두 서버의 사용자 홈에 복사한다. 비밀번호·개인키는 파일이나 채팅으로 전달하지 않는다. Python 코드를 터미널에 줄마다 붙여넣지 않는다.
2. 해당 서버 콘솔에서 아래 명령을 실행한다. Python 스크립트 자체를 sudo로 실행하지 않는다. 필요한 조회만 스크립트가 sudo로 수행한다.

```bash
cd "$HOME"
hostname -s
sudo -v
python3 ./collect_dns_zone_readonly.py
```

3. `COMPLETE_COLLECTION_ONLY` 및 `COLLECTED_DIRECTORY=...`가 나오면 출력 경로를 사용해 확인한다.

```bash
cd '위에서 출력된 COLLECTED_DIRECTORY의 실제 경로'
sha256sum -c SHA256SUMS
```

모두 OK이면 해당 **결과 폴더 전체**를 기존 전달 방법으로 가져온다. dns01과 dns02 폴더를 합치거나 이전 1차 수집본을 덮어쓰지 않는다. 수신 후 Secret 점검·Zone 레코드 비교를 거쳐 source/evidence의 독립 리뷰 PR로 나눈다. 자동 GitHub 업로드는 없다.

## 수집 내용과 중단 조건

- 현재 MainPID의 실제 executable·root·config 인자를 확인한다. `/usr/sbin/named`, 명시적인 `-c /etc/named.conf`, 일반 root(`/`), chroot 옵션 없음일 때만 진행한다. 원본 프로세스 인자 전체와 환경변수는 저장·출력하지 않는다.
- 마스킹된 디스크 설정이 1차 수신본과 같은지 확인한다. 다른 config/chroot, 변경된 설정, 다른 Zone 경로는 임의 추정하지 않고 중단한다.
- 고정된 Zone 파일 하나만 읽는다: dns01 `/var/named/fds.internal.zone`, dns02 `/var/named/slaves/fds.internal.zone`. symlink, dynamic zone, journal, `$INCLUDE`, 비밀정보 패턴, 과도한 크기 또는 수집 중 파일/serial 변경이 있으면 중단한다. `$INCLUDE` 중단은 보안 검토 경계이며 정본의 새 AC가 아니다.
- 원본 Zone 바이트와 해시를 보존하고, 로컬 사본에 `named-checkzone`을 실행해 text/raw 형식을 확인하고 비교용 text를 생성한다. dns02의 파일이 binary raw여도 바로 오류로 판단하지 않는다. 형식 변환본은 원본과 구분하며 운영 파일에 덮어쓰지 않는다.
- 모든 zone의 runtime/permanent firewalld 설정 및 DNS ipset을 수집한다. 실제 패킷 접근 시험이나 kernel/firewalld 외부 규칙 전체 검증은 수행하지 않는다.
- 호스트·KST 시각·수집기 hash·BIND 버전·각 명령·종료 코드·허용된 stdout·파일 hash를 남긴다. 실패한 설정/검사 명령의 stderr는 비밀정보 노출 방지를 위해 저장하지 않으며 COMMANDS.json에 이 제한을 표시한다.

`INCOMPLETE_DO_NOT_SUBMIT_AS_COMPLETE` 또는 예외/명령 실패이면 거기서 멈춘다. 가드를 제거하거나 파일 경로를 임의 변경하지 말고 마지막 상태·사유·결과 폴더명을 전달한다. 비밀번호·키 원문·실패 명령의 원문 stderr는 보내지 않는다. 완료 표시와 manifest가 없는 폴더는 완성된 수집본이 아니다.

## 영향·복구·검증 범위

원본 Zone·named 설정·방화벽·SELinux를 변경하지 않고 reload/restart/retransfer/AXFR를 실행하지 않는다. 따라서 서비스 원복 작업은 없다. 생성한 사용자 홈 결과 폴더만 검수 완료 후 별도 정리한다. 실제 TSIG key 파일 및 그 파일 hash는 수집하지 않는다.

2차 수집기는 로컬 정적·모의 검증 후 제공했고 이후 사용자 서버 실행본으로 실제 BIND 형식 검사와 Zone 동일성을 확인했다. 디스크 소스 확보 성공이 모든 in-memory 설정의 동일성, 네트워크 전송·질의 정상, AC PASS 또는 독립 승인이라는 뜻은 아니다. 원 named.conf/include의 배포 구조 복원은 별도 남은 작업이다.

형식 옵션과 읽기 동작의 근거: [ISC BIND named-checkzone / named-checkconf / rndc 공식 설명](https://bind9.readthedocs.io/en/stable/manpages.html).

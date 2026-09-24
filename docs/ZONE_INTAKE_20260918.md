# Zone 원본 수신 및 이관 — 2026-09-18

사용자의 2차 콘솔 수집본을 12:26:05 KST에 확인했다. dns01 수집은 12:24:50~12:24:51, dns02는 12:24:52~12:24:53 KST이다. **수집 성공과 Source 동일성 확인 완료, 독립 리뷰·병합 및 운영 적용 미완료**다.

## 확보한 Source

- [zones/fds.internal.zone](../zones/fds.internal.zone): dns01 `/var/named/fds.internal.zone`의 698 bytes 원본과 같다. SHA-256 `f4bbbc4818e9724b07c1452caecfdb8d0629c8bf6fb75ea092ae44adc31642d8`. 주 Zone의 관리 Source로 등록하며 이번 복사에서 serial이나 레코드를 수정하지 않았다.
- [dns02 비교용 정규화본](../references/console-20260918/dns02/fds.internal.normalized.reference.zone): `/var/named/slaves/fds.internal.zone`에서 BIND가 생성한 text 정규화 결과다. dns02의 원본은 822 bytes raw 형식이며 그 원본은 증적 저장소에 보관한다. Secondary의 전송 사본을 별도의 편집·배포 Source로 관리하지 않는다.
- 1차 마스킹 참고 named 설정은 2차 출력과 바이트가 같다. 실제 실행 인자의 `/etc/named.conf`, 프로세스 root `/`, executable `/usr/sbin/named`와 각 Zone 경로가 이번 수집에서 확인됐다. 이는 모든 in-memory 설정과 디스크 설정의 동일성까지 입증하지 않는다.
- 원본 로그·화면·raw Zone 등 64개와 관리 문서 3개는 [evidence PR #16](https://github.com/321Team/fds-project-evidence/pull/16), 고정 commit [f5f1537](https://github.com/321Team/fds-project-evidence/tree/f5f1537408a17672aed8581e7cbe2962bd4951f5/evidence/P1-DNS-01/source-intake/received-20260918T032605Z)에 추가했다. 미병합 상태이며 증적 저장소의 독립 리뷰를 유지한다.

## 검증 결과

각 호스트의 서버 SHA256SUMS 23개씩 총 **46개 일치**. 실행기 hash는 이 저장소 commit `091ecee21d777ab36877381a1b3f5bb8ef1f6eb2`의 수집기 SHA-256 `9458d9aa60d8589809eadc129cd4186f7084a2eea7fdba8302c5a090ae0e1346`과 일치한다. 상태는 양쪽 `COMPLETE_COLLECTION_ONLY`, 파일 stat/PID/serial은 수집 전후 변화가 관측되지 않았다.

실제 BIND 9.18.33에서 dns01 text 검사 RC 0, dns02 text 시도 RC 1 후 raw 검사 RC 0을 기록했다. dns02의 RC 1은 raw 형식에 대한 text 시도이며 뒤의 성공 결과와 함께 해석한다. 다른 수집 명령은 RC 0이다. 에이전트가 서버 실행을 직접 관찰한 것이 아니라 사용자 제출 파일과 명령 기록을 검증한 결과다.

정규화 결과는 양쪽 882 bytes로 byte-identical이며 SHA-256은 `7161d50eaaed299d4cc14eb409a5351e7c260aff572db04e8a3802c97c09b954`다. SOA 1개 / NS 2개 / A 13개, TTL 300, serial 2026090101, refresh 300 / retry 120 / expire 604800 / negative TTL 300이다. [승인 R5 기록](../references/approved-20260903/P1-DNS-01_Notion_Description_v1.3_Review.md)의 A Record 이름·주소와 대조했다.

| A Record (`.fds.internal`) | 주소 |
|---|---|
| dns01 / dns02 | 10.1.93.52 / 10.1.93.53 |
| edge / vpn-gw | 10.1.93.50 / 10.1.93.51 |
| harbor / db | 10.1.93.54 / 10.1.93.55 |
| control01 / control02 / control03 | 10.1.93.102 / .103 / .104 |
| worker01 / worker02 / worker03 | 10.1.93.105 / .107 / .108 |
| k8s-api | 10.1.93.109 |

`.56`의 후속 승인은 Query Source ACL/ipset 확대이며 현재 Zone에 .56 A Record는 없다. 별도 승인 없이 새 레코드를 합성하지 않는다. 위 수치는 현재 수신본에서 관찰한 값이며 향후 Zone 변경에서 serial을 영구 고정하라는 의미가 아니다.

## 방화벽 대조와 한계

양 호스트 runtime끼리·permanent끼리 출력이 같다. public/default zone의 runtime interface는 ens160이며 일반 services는 cockpit/dhcpv6-client/ssh, ports는 비어 있다. DNS 허용은 다음 rich rule로 제한된다.

```text
rule family="ipv4" source ipset="fds-dns-clients" service name="dns" accept
```

이 규칙과 IPSet 14개는 runtime/permanent가 일치한다. IPSet은 1차 BIND ACL의 loopback 외 주소와 같으며 `.56`/`.109`를 포함한다. 전체 텍스트에서는 active 표기와 permanent interface 공란의 차이가 있다. NetworkManager 또는 기본 zone 귀속이 가능하므로 이 차이만으로 결함을 단정하지 않는다([firewalld 공식 설명](https://firewalld.org/documentation/zone/connections-interfaces-and-sources)). 실제 NM profile·재기동 지속성은 미검증이다.

dns service 정의, firewalld policy/direct 및 kernel 규칙 전체, TCP/UDP 허용·거부 실제 패킷 시험은 미수집·미실행이다. 활성 interface가 없는 기본 nm-shared zone의 dns 항목만으로 ens160 무제한 개방을 주장하지 않는다.

## 완료 범위와 잔여

이번 단계는 Zone Source 복원과 부분 Runtime 관찰의 수신이다. 마스킹 named 설정은 여전히 배포 금지 참고본이며 원 named.conf/include 파일 경계·Secret 참조 구조는 남은 자료다. 과거 v1.9 실행 검증 원본도 미확보다. 완전한 DNS 배포 구성·재시작 지속성·AC 전체 재시험을 완료했다고 표시하지 않는다.

기존 R2/정본/서버는 변경하지 않았다. 새 query/AXFR/retransfer/failover/reload/restart는 수행하지 않았다. 저장소 변경 복구는 해당 PR revert이며 Source 병합은 Runtime 적용이나 기존 Done 티켓 재종결을 의미하지 않는다. 소스 혼합 PR과 증적 PR 양쪽에 최신 HEAD 독립 리뷰를 적용한다.

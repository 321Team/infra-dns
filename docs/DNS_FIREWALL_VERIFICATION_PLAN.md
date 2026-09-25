# DNS 방화벽 확인 계획 — 조회·패킷 시험·재기동 지속성 (#7)

상태: A는 수집 도구와 절차를 준비했고 **서버 실행 전**이다. B·C는 **계획이며 실행 승인이 아니다.** 책임 과제: [#7](https://github.com/321Team/infra-dns/issues/7).

2026-09-18 수집(evidence PR 16)으로 확인한 것과 확인하지 못한 것은 다음과 같다.

- 확인: 양쪽 `public` zone의 DNS 허용은 `fds-dns-clients` ipset(14개) 한정 rich rule이다. runtime과 permanent가 같다.
- 미확인:
  - permanent `public`의 interface 칸이 비어 있다. NetworkManager가 zone을 붙이는 방식과 재기동 뒤 유지 여부를 확인하지 않았다.
  - `dns` service 정의
  - policy·direct·nftables 전체
  - 실제 패킷 허용·거부

## A. 읽기 전용 조회 — 바로 실행 가능

도구: [`tools/collect_dns_firewall_readonly.py`](../tools/collect_dns_firewall_readonly.py)

**조회하는 것**

| 대상 | 명령 |
|---|---|
| firewalld 상태 | `systemctl is-active/is-enabled firewalld` |
| 기본 zone, 활성 zone | `firewall-cmd --get-default-zone`, `--get-active-zones` |
| 모든 zone | runtime·permanent `--list-all-zones` |
| `dns` service 정의 | `--info-service=dns` |
| ipset 정의·항목 | `--info-ipset=fds-dns-clients`, `--ipset=… --get-entries` |
| policy | `--list-all-policies` |
| direct 규칙 | `--direct --get-all-rules` |
| NetworkManager | `ens160` 활성 연결의 `connection.zone`, `connection.autoconnect`(`nmcli -g`, 비밀 필드 없음) |
| 커널 규칙 | `nft list ruleset` |

**안전장치**

- 모든 명령은 실행 전에 허용 목록으로 검사한다.
- 다음과 같은 쓰기성 옵션이나 동사가 있으면 실행하지 않고 멈춘다: `--add…`, `--remove…`, `--reload`, `--set…`, `--runtime-to-permanent`, `--panic…`, `nmcli … up/down/modify`, `nft flush`, `systemctl restart`.
- stderr는 저장하지 않는다.
- 결과는 사용자 홈의 새 폴더 `dns-firewall.<host>.*`에만 남는다. 중앙 정책 §3.2 4-1 순수 검증기 조건에 맞춰 설계했다.

**`summary.json` 관찰 항목**

아래 항목은 판정이 아니라 관찰값이다. 차이가 있어도 도구는 멈추지 않고 기록만 한다.

- 기본 zone이 `public`인지
- `dns` service 포트(기대값 `53/tcp`, `53/udp`, runtime과 permanent 동일)
- rich rule이 runtime·permanent에 모두 있는지
- ipset 항목 수, runtime과 permanent가 같은지
- `ens160`이 runtime `public`에 있는지, permanent `public`에 있는지
- NetworkManager 연결의 zone(빈 값이면 기본 zone을 따름)과 autoconnect
- `public`에 `dns` service가 직접 열려 있는지(기대값: 아니오)
- policy·direct 규칙 존재 여부

**실행 순서**

1. 병합된 main의 도구를 기존 VM 파일 전달 방법으로 서버 사용자 홈에 복사하고 `sha256sum`을 대조한다.
2. 콘솔에서 다음을 실행한다.
   ```bash
   cd "$HOME"; hostname -s; sudo -v
   python3 ./collect_dns_firewall_readonly.py
   ```
3. `COMPLETE_COLLECTION_ONLY`이면 결과 폴더에서 `sha256sum -c SHA256SUMS`를 실행하고, 폴더 전체를 가져온다. `INCOMPLETE…`이면 멈추고 사유만 전달한다.
4. 실행 기록을 남긴다: 대상 서버, 실행 SHA, 명령, 계정, KST 시각, 판단 근거, 결과 경로.
5. 결과는 fds-project-evidence에 새 수집회차로 편입한다(독립 리뷰).

## B. 실제 패킷 시험 — 계획, Lead 승인 뒤 실행

목적: 허용 Source는 UDP·TCP 53 질의에 응답을 받고, 비허용 Source는 받지 못하는지 확인한다. 이 시험은 DNS 서버 설정을 바꾸지 않는다. 클라이언트에서 질의 몇 개만 보낸다. 부하 시험이 아니다.

| 구분 | Source(예시, 실행 전 확정) | 기대 결과 |
|---|---|---|
| 허용 | `fds-dns-clients` 목록 안의 노드 1대 이상(예: control01 `10.1.93.102`) | `.52`·`.53` 모두 UDP·TCP로 `SOA` 응답, serial 일치 |
| 비허용(관리망) | ansible01 `10.250.10.10` 또는 monitor01 `10.250.10.30` | UDP·TCP 모두 응답 없음(시간 초과 또는 연결 거부). BIND의 `REFUSED` 응답이 오면 방화벽이 아니라 BIND ACL에서 막힌 것이므로 따로 기록한다 |

명령(각 Source에서 각 서버 `.52`·`.53`에 대해 실행):

```bash
dig +notcp +time=2 +tries=1 @10.1.93.52 fds.internal SOA
dig +tcp   +time=2 +tries=1 @10.1.93.52 fds.internal SOA
```

- **기록:** Source 호스트, 시각, 명령, 종료 코드, 출력 전문. 비허용 Source에서는 `status:` 줄 유무와 시간 초과 여부를 적는다.
- **중단 기준:** 허용 Source에서 응답이 없으면 추가 시험을 멈춘다. 운영 질의에 영향이 있을 수 있으니 A 수집 결과와 함께 원인을 먼저 확인한다.
- 기존 DNS-NT-01/03(2026-09-02 R2)의 비허용 시험과 같은 성격이다. 이번 결과가 기존 AC 판정을 바꾸지 않는다.

## C. 재기동 지속성 — 계획, 작업창·복구안 승인 뒤 실행

**목적:** 재기동 뒤에도 다음이 유지되는지 확인한다.

- `ens160`이 `public` zone에 붙는지(NetworkManager 경유)
- rich rule, ipset
- named 기동과 Zone 제공

**순서:** dns02(secondary)를 먼저 하고, dns01은 별도 작업창에서 한다. 한 번에 한 대만 재기동한다. 재기동 중에는 다른 서버가 질의를 받는다(DNS-AC-08의 Primary 중단 시 dns02 지속 PASS 이력 참고).

1. **재기동 전:** A 수집과 B 허용 Source 시험을 실행한다. 결과는 `pre` 폴더에 둔다.
2. Lead가 승인한 작업창에 대상 서버를 재기동한다. 재기동 명령과 시각을 기록한다.
3. **재기동 뒤:** `systemctl is-active named firewalld`로 상태를 확인하고, A 수집과 B 시험을 다시 실행한다. 결과는 `post` 폴더에 둔다.
4. **비교:** `pre`와 `post`의 `summary.json`에서 다음 필드가 같아야 한다.
   - `default_zone`
   - `interface_in_runtime_public`
   - `dns_rich_rule_runtime`
   - `ipset_entries_runtime`
   - `ipset_runtime_equals_permanent`
   - `dns_service_ports_runtime`

   B 허용 시험도 같은 결과여야 한다.

**중단·복구 기준:** 재기동 뒤 허용 Source 질의가 실패하거나 위 필드가 달라지면, 먼저 다른 서버가 응답하는지 확인한다. 복구는 아래 원칙을 따른다.

- 복구 명령(예: interface의 zone 재지정, permanent 설정으로 runtime 재적재)은 **서버를 바꾸는 명령**이다. 그래서 작업창 승인 때 Lead가 미리 확정한 명령만 실행한다.
- 복구 기준값은 재기동 전 `pre` 수집 결과(permanent·runtime 출력)다.
- 이 계획서는 복구 명령을 정하지 않는다. 작업창 승인 문서에서 정한다.

## 남은 판단

- B의 Source 호스트와 작업창, C의 작업창·복구 명령은 Lead가 정한다.
- 결과에서 결함이 나오면(예: 재기동 뒤 interface 누락) 별도 변경 요청으로 다룬다. P1-DNS-01 Done은 유지한다.

# P1-DNS-01 R2 증적 보완 실행 가이드 v1.8

## 문서 정정 이력

- v1.8은 v1.7에서 누락된 `generate_checksums_r2.sh`의 제공 위치, 설치 여부 확인, 문법·무결성 검증 및 실행 인자를 명시한다.
- `generate_checksums_r2.sh`는 ansible01에서 새로 작성하는 파일이 아니라 Kit ZIP에 포함된 배포 파일로 고정한다.
- 중앙 조립 단계에 그대로 붙여넣어 실행할 수 있는 Host·계정·경로 검증 포함 명령 블록을 추가한다.
- v1.8은 v1.6에서 가이드가 요구했으나 실제 배포하지 않았던 R1 ZIP과 R1 ZIP Sidecar를 배포 목록에 포함한다.
- `제공 파일`, `Kit 내부 파일`, `실행 후 생성 파일`을 구분한다.
- Kit ZIP도 외부 Sidecar로 검증한 후 압축을 해제하도록 절차를 보완한다.
- v1.6과 v1.7 가이드·Kit는 폐기하고 v1.8만 사용한다.

## 배포 파일 기준

사용자가 내려받아 Windows Host의 `packages` 폴더에 두어야 하는 파일은 정확히 다음 4개다.

| 구분 | 제공 파일 | Kit ZIP 내부 포함 여부 | 용도 |
|---|---|---:|---|
| R1 입력 | `P1-DNS-01-FRESH-20260902-R1.zip` | 아니요 | 검증 완료된 R1 원본 |
| R1 입력 무결성 | `P1-DNS-01-FRESH-20260902-R1.zip.sha256` | 아니요 | R1 ZIP 외부 Sidecar |
| R2 도구 | `P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8.zip` | 해당 없음 | 가이드·Collector·검증 Script |
| R2 도구 무결성 | `P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8.zip.sha256` | 아니요 | Kit ZIP 외부 Sidecar |

`R2_REMEDIATION_RUNBOOK.md`와 `P1-DNS-01_R2_Status_Update.md`가 별도 링크로 제공될 수 있으나, 이는 열람 편의를 위한 사본이며 Kit ZIP 안에도 포함되어 있다. R1 ZIP과 R1 Sidecar는 증적 입력물이므로 Kit ZIP 안에 중복 포함하지 않는다. Kit 압축 해제 후 실제 포함 파일은 `FILE_MANIFEST.md`와 일치해야 한다.

## 0. 이 가이드에서 고정하는 사항

- 기준 문서: `FDS Project Implementation Baseline v3.1.14`
- 중앙 취합 Host: `ansible01` / `10.250.10.10` / 계정 `server01_ansible`
- 중앙 작업 Root: `/home/server01_ansible/p1-dns-01-r2/`
- 정본 Evidence 상위 경로: `/home/server01_ansible/p1-dns-01-r2/docs/evidence/P1-DNS-01/`
- dns01 수집 Host: `dns01` / `10.1.93.52` / 계정 `server01_dns01`
- dns02 수집 Host: `dns02` / `10.1.93.53` / 계정 `server08`
- Windows Host는 WinSCP 파일 중계에만 사용한다.
- Kubernetes Control Plane과 `k8s-api-lb01`은 중앙 취합 Host로 사용하지 않는다.
- 기존 R1 Evidence 9종과 Sidecar는 수정하지 않는다.
- R2에서 새로 실행하는 Collector는 아래 두 개뿐이다.
  1. dns01에서 승인 A Record 13개 × DNS 서버 2대 전수 대조
  2. dns02에서 Fresh TSIG Zone Transfer 증적 수집
- 기존 Failover, Recovery, Resolver Rollback은 재실행하지 않는다.

> Lead 결정에 따라 중앙 취합 Host는 `ansible01`로 확정한다. Git 저장소는 요구사항이 아니며 본 절차에서 사용하지 않는다. dns01/dns02에서는 Host별 수집만 수행하고, 인덱스·중앙 Hash·제출 ZIP은 ansible01에서만 생성한다.

## 1. Host와 실행 디렉터리

| 단계 | 실행 위치 | 로그인 계정 | 작업 디렉터리 | 생성·보관 대상 |
|---|---|---|---|---|
| 중앙 준비·조립 | `ansible01` (`10.250.10.10`) | `server01_ansible` | `/home/server01_ansible/p1-dns-01-r2/` | R1 검증본, Kit, Host 수집본, R2 작업본 |
| Record Inventory | `dns01` (`10.1.93.52`) | `server01_dns01` | `/home/server01_dns01/p1-dns-01-r2/` | `output/inventory/` |
| Fresh TSIG | `dns02` (`10.1.93.53`) | `server08` | `/home/server08/p1-dns-01-r2/` | `output/tsig/` |
| 파일 중계 | Windows Host | `soldesk` | `C:\Users\soldesk\Documents\FDS\P1-DNS-01\R2-transfer\` | WinSCP 임시 전송본 |
| 정본 반영 | `ansible01` (`10.250.10.10`) | `server01_ansible` | `/home/server01_ansible/p1-dns-01-r2/docs/evidence/P1-DNS-01/` | R2 디렉터리, ZIP, ZIP Sidecar |

Host 로컬 경로와 중앙 경로는 서로 다른 파일시스템이다. 같은 `$PWD`를 공유 경로처럼 사용하지 않는다. ansible01과 DNS Host 사이의 직접 SFTP 경로는 검증되지 않았으므로 본 가이드는 Windows Host의 WinSCP를 전송 중계로 사용한다.

ansible01은 이번 R2에서 DNS 질의 Source가 아니라 중앙 파일 취합·검증 Host다. 따라서 ansible01의 DNS TCP/UDP 53 접근 허용을 새로 추가하지 않는다.

## 2. 실행 금지 위치와 명령 구분

| 명령 | 실행해야 하는 Host | 다른 Host에서 실행한 경우 |
|---|---|---|
| `sudo systemctl is-active named` | dns01 또는 dns02 | BIND가 없는 Host에서는 의미 없는 실패 결과가 됨 |
| `sudo rndc zonestatus fds.internal` | dns01 또는 dns02 | `k8s-api-lb01`에서 실행한 결과는 DNS 서버 증적으로 인정하지 않음 |
| `sudo rndc retransfer fds.internal` | **dns02만** | 다른 Host에서 실행 금지 |
| `dig @10.1.93.52 ...` | 질의 목적에 따라 어느 Client에서도 가능 | Client 도달성만 증명하며 DNS 서버 로컬 상태는 증명하지 못함 |
| `generate_evidence_index.sh` | ansible01만 | Host별 수집 전에 실행하면 불완전한 인덱스가 생성됨 |
| `generate_checksums_r2.sh` | ansible01만 | 모든 파일 취합 전에 실행하지 않음 |

## 3. 전체 실행 순서

1. Windows Host에서 전달 파일 폴더를 준비한다.
2. ansible01에서 중앙 작업 디렉터리와 Kit를 준비한다.
3. Inventory Collector 한 개를 dns01에 전송한다.
4. Fresh TSIG Collector 한 개를 dns02에 전송한다.
5. dns01에서 Inventory를 수집한다.
6. Lead가 작업창을 승인한 뒤 dns02에서 Fresh TSIG를 수집한다.
7. Windows Host가 dns01/dns02 결과를 내려받아 ansible01로 업로드한다.
8. ansible01에서 R1을 복제해 R2를 만들고 신규 두 결과를 추가한다.
9. ansible01에서 인덱스·Hash·ZIP을 생성하고 검증한다.
10. 검증된 결과만 ansible01의 정본 경로에 반영한다.

---

## 4. 단계 A — Windows 중계 폴더와 ansible01 중앙 경로 준비

### 4.1 Windows Host에서 전송 폴더 생성

Windows PowerShell에서 실행한다.

```powershell
$TransferRoot = 'C:\Users\soldesk\Documents\FDS\P1-DNS-01\R2-transfer'

New-Item -ItemType Directory -Force -Path `
  "$TransferRoot\packages", `
  "$TransferRoot\kit", `
  "$TransferRoot\host-output\dns01\inventory", `
  "$TransferRoot\host-output\dns02\tsig" | Out-Null

Get-ChildItem -Recurse $TransferRoot
```

위 `배포 파일 기준`의 다음 네 파일을 Windows의 `packages` 디렉터리에 둔다.

```text
C:\Users\soldesk\Documents\FDS\P1-DNS-01\R2-transfer\packages\P1-DNS-01-FRESH-20260902-R1.zip
C:\Users\soldesk\Documents\FDS\P1-DNS-01\R2-transfer\packages\P1-DNS-01-FRESH-20260902-R1.zip.sha256
C:\Users\soldesk\Documents\FDS\P1-DNS-01\R2-transfer\packages\P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8.zip
C:\Users\soldesk\Documents\FDS\P1-DNS-01\R2-transfer\packages\P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8.zip.sha256
```

PowerShell에서 누락 여부를 확인한다.

```powershell
$RequiredFiles = @(
  'P1-DNS-01-FRESH-20260902-R1.zip',
  'P1-DNS-01-FRESH-20260902-R1.zip.sha256',
  'P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8.zip',
  'P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8.zip.sha256'
)

$MissingFiles = $RequiredFiles | Where-Object {
  -not (Test-Path -LiteralPath "$TransferRoot\packages\$_" -PathType Leaf)
}

if ($MissingFiles) {
  $MissingFiles | ForEach-Object { Write-Error "MISSING: $_" }
  throw '필수 배포 파일이 누락되었습니다.'
}

$RequiredFiles | ForEach-Object { Write-Host "PRESENT: $_" }
```

Kit ZIP은 Windows에서 아래 위치로 압축 해제한다.

```powershell
Expand-Archive -Force `
  -Path "$TransferRoot\packages\P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8.zip" `
  -DestinationPath "$TransferRoot\kit"
```

### 4.2 ansible01 접속 및 Host 확인

Windows Host에서 ansible01에 접속한다.

```bash
ssh server01_ansible@10.250.10.10
```

ansible01 Prompt에서 실행한다.

```bash
hostnamectl --static
whoami
pwd
timedatectl show -p Timezone -p NTPSynchronized
command -v bash
command -v sha256sum
command -v unzip
command -v zip
```

예상 Host/계정은 다음과 같다.

```text
ansible01
server01_ansible
```

`unzip` 또는 `zip` 명령이 없으면 중앙 조립을 시작하지 않는다. 패키지 설치는 별도 승인 후 수행한다.

### 4.3 ansible01 중앙 디렉터리 생성

ansible01 Prompt에서 실행한다.

```bash
test "$(hostnamectl --static)" = "ansible01" || exit 1
test "$(whoami)" = "server01_ansible" || exit 1

umask 027
central_root="/home/server01_ansible/p1-dns-01-r2"
incoming_root="${central_root}/incoming"
work_root="${central_root}/work"
kit_extract_root="${central_root}/kit"
canonical_root="${central_root}/docs/evidence/P1-DNS-01"

install -d -m 0750 \
  "${incoming_root}/r1" \
  "${incoming_root}/dns01/inventory" \
  "${incoming_root}/dns02/tsig" \
  "${work_root}" \
  "${kit_extract_root}" \
  "${canonical_root}"

printf 'Central root   : %s\n' "${central_root}"
printf 'Incoming root  : %s\n' "${incoming_root}"
printf 'Work root      : %s\n' "${work_root}"
printf 'Canonical root : %s\n' "${canonical_root}"
```

`/approved/evidence/...`는 생성·권한 승인이 확인되지 않았으므로 사용하지 않는다. 중앙 Bash를 다시 열었다면 이후 중앙 단계 실행 전에 위 변수 정의 블록을 다시 실행한다.

### 4.4 Windows에서 ansible01로 R1과 Kit 업로드

WinSCP 접속 대상:

```text
Host: 10.250.10.10
User: server01_ansible
```

| Windows 원본 | ansible01 목적지 |
|---|---|
| `...\packages\P1-DNS-01-FRESH-20260902-R1.zip` | `/home/server01_ansible/p1-dns-01-r2/incoming/r1/` |
| `...\packages\P1-DNS-01-FRESH-20260902-R1.zip.sha256` | `/home/server01_ansible/p1-dns-01-r2/incoming/r1/` |
| `...\packages\P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8.zip` | `/home/server01_ansible/p1-dns-01-r2/incoming/` |
| `...\packages\P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8.zip.sha256` | `/home/server01_ansible/p1-dns-01-r2/incoming/` |

### 4.5 ansible01에서 R1과 Kit 검증·압축 해제

ansible01 Prompt에서 실행한다.

```bash
central_root="/home/server01_ansible/p1-dns-01-r2"
incoming_root="${central_root}/incoming"
work_root="${central_root}/work"
kit_extract_root="${central_root}/kit"

cd "${incoming_root}/r1" || exit 1
sha256sum --check P1-DNS-01-FRESH-20260902-R1.zip.sha256
unzip -t P1-DNS-01-FRESH-20260902-R1.zip

unzip -q \
  P1-DNS-01-FRESH-20260902-R1.zip \
  -d "${work_root}/r1-extract"

r1_root="${work_root}/r1-extract/P1-DNS-01-FRESH-20260902-R1"
test -d "${r1_root}"

cd "${r1_root}" || exit 1
sha256sum --check SHA256SUMS

cd "${incoming_root}" || exit 1
sha256sum --check P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8.zip.sha256
unzip -t P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8.zip

unzip -q \
  "${incoming_root}/P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8.zip" \
  -d "${kit_extract_root}"

kit_root="${kit_extract_root}/P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8"

cd "${kit_root}" || exit 1
sha256sum --check PACKAGE_CONTENT_SHA256SUMS

required_scripts=(
  collect_dns_record_inventory_evidence.sh
  collect_dns02_fresh_tsig_evidence.sh
  generate_evidence_index.sh
  generate_checksums_r2.sh
  validate_r2_package.sh
)

for script_name in "${required_scripts[@]}"; do
  script_path="${kit_root}/scripts/${script_name}"
  test -s "${script_path}"
  bash -n "${script_path}"
  chmod 0750 "${script_path}"
  printf 'SCRIPT READY: %s\n' "${script_path}"
done
```

완료 조건:

- R1 ZIP Sidecar가 `OK`
- `unzip -t`가 오류 없이 완료
- R1 중앙 `SHA256SUMS`가 모두 `OK`
- Kit ZIP Sidecar가 `OK`
- Kit ZIP의 `unzip -t`가 오류 없이 완료
- Kit의 `PACKAGE_CONTENT_SHA256SUMS`가 모두 `OK`
- `SCRIPT READY`가 5개 출력되고 각 Script의 `bash -n`이 성공

### 4.6 `generate_checksums_r2.sh` 제공·배치 원칙

`generate_checksums_r2.sh`는 ansible01에서 `tee`나 편집기로 생성하지 않는다. v1.8 Kit ZIP 내부에서 다음 경로로 제공된다.

```text
P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8/scripts/generate_checksums_r2.sh
```

ansible01에서 Kit를 4.5 절대로 압축 해제하면 실제 실행 경로는 다음과 같다.

```text
/home/server01_ansible/p1-dns-01-r2/kit/P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8/scripts/generate_checksums_r2.sh
```

ansible01 Prompt에서 파일을 다시 확인한다.

```bash
test "$(hostnamectl --static)" = "ansible01" || exit 1
test "$(whoami)" = "server01_ansible" || exit 1

checksum_script="/home/server01_ansible/p1-dns-01-r2/kit/P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8/scripts/generate_checksums_r2.sh"

test -s "${checksum_script}"
bash -n "${checksum_script}"
stat -c '%n | %s bytes | %a | %U:%G' "${checksum_script}"
```

파일이 없거나 `bash -n`이 실패하면 임의로 Script를 재작성하지 않는다. Kit ZIP/Sidecar와 `PACKAGE_CONTENT_SHA256SUMS`를 다시 검증한 뒤 Kit를 재배치한다.

---

## 5. 단계 B — Collector를 각 DNS Host에 배치

### 5.1 dns01 원격 디렉터리 생성

운영자 PC에서 dns01에 접속한다.

```bash
ssh server01_dns01@10.1.93.52
```

dns01 Prompt에서 실행한다.

```bash
hostnamectl --static
whoami

install -d -m 0750 \
  /home/server01_dns01/p1-dns-01-r2/scripts \
  /home/server01_dns01/p1-dns-01-r2/output
```

예상값:

```text
dns01
server01_dns01
```

WinSCP로 아래 파일 한 개만 업로드한다.

```text
Windows 원본:
C:\Users\soldesk\Documents\FDS\P1-DNS-01\R2-transfer\kit\P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8\scripts\collect_dns_record_inventory_evidence.sh

dns01 목적지:
/home/server01_dns01/p1-dns-01-r2/scripts/collect_dns_record_inventory_evidence.sh
```

업로드 후 dns01에서 실행한다.

```bash
chmod 0750 \
  /home/server01_dns01/p1-dns-01-r2/scripts/collect_dns_record_inventory_evidence.sh
```

### 5.2 dns02 원격 디렉터리 생성

운영자 PC에서 dns02에 접속한다.

```bash
ssh server08@10.1.93.53
```

dns02 Prompt에서 실행한다.

```bash
hostnamectl --static
whoami

install -d -m 0750 \
  /home/server08/p1-dns-01-r2/scripts \
  /home/server08/p1-dns-01-r2/output
```

예상값:

```text
dns02
server08
```

WinSCP로 아래 파일 한 개만 업로드한다.

```text
Windows 원본:
C:\Users\soldesk\Documents\FDS\P1-DNS-01\R2-transfer\kit\P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8\scripts\collect_dns02_fresh_tsig_evidence.sh

dns02 목적지:
/home/server08/p1-dns-01-r2/scripts/collect_dns02_fresh_tsig_evidence.sh
```

업로드 후 dns02에서 실행한다.

```bash
chmod 0750 \
  /home/server08/p1-dns-01-r2/scripts/collect_dns02_fresh_tsig_evidence.sh
```

---

## 6. 단계 C — dns01 Record Inventory 수집

### 6.1 실행 위치

- Host: `dns01`
- IP: `10.1.93.52`
- 계정: `server01_dns01`
- Script: `/home/server01_dns01/p1-dns-01-r2/scripts/collect_dns_record_inventory_evidence.sh`
- 출력 Root: `/home/server01_dns01/p1-dns-01-r2/output`
- 실제 생성 디렉터리: `/home/server01_dns01/p1-dns-01-r2/output/inventory`
- 변경 영향: 없음. `dig` 읽기 전용 질의만 수행

### 6.2 실행 명령

dns01 Prompt에서 실행한다.

```bash
test "$(hostnamectl --static)" = "dns01" || exit 1
test "$(whoami)" = "server01_dns01" || exit 1

work_root="/home/server01_dns01/p1-dns-01-r2"
script_path="${work_root}/scripts/collect_dns_record_inventory_evidence.sh"
output_root="${work_root}/output"

cd "${work_root}" || exit 1
pwd

bash "${script_path}" "${output_root}"
collector_rc=$?
printf 'Collector exit code: %s\n' "${collector_rc}"
test "${collector_rc}" -eq 0
```

### 6.3 dns01 로컬 검증

```bash
inventory_dir="/home/server01_dns01/p1-dns-01-r2/output/inventory"

find "${inventory_dir}" -maxdepth 1 -type f \
  -printf '%f | %s bytes\n' | sort

cd "${inventory_dir}" || exit 1
sha256sum --check ./*.sha256

grep -F 'SERVER SUMMARY: 10.1.93.52 passed 13/13 records' \
  ./*_dns_record_inventory_evidence.txt
grep -F 'SERVER SUMMARY: 10.1.93.53 passed 13/13 records' \
  ./*_dns_record_inventory_evidence.txt
grep -F 'TOTAL: 26/26 approved authoritative answers' \
  ./*_dns_record_inventory_evidence.txt
grep -F 'PASS: all 13 approved A records matched on dns01 and dns02' \
  ./*_dns_record_inventory_evidence.txt

if grep -Eq '^(FAIL|ERROR):' ./*_dns_record_inventory_evidence.txt; then
  echo 'STOP: inventory evidence contains FAIL/ERROR'
  exit 1
fi
```

완료 결과는 TXT 한 개와 같은 이름의 `.sha256` 한 개다.

---

## 7. 단계 D — dns02 Fresh TSIG 수집

### 7.1 실행 위치와 변경 영향

- Host: `dns02`
- IP: `10.1.93.53`
- 계정: `server08`
- Script: `/home/server08/p1-dns-01-r2/scripts/collect_dns02_fresh_tsig_evidence.sh`
- 출력 Root: `/home/server08/p1-dns-01-r2/output`
- 실제 생성 디렉터리: `/home/server08/p1-dns-01-r2/output/tsig`
- 변경 영향: `rndc retransfer fds.internal`로 Secondary가 Primary에서 Zone을 다시 전송받음
- Zone Record와 Serial은 수정하지 않음
- Lead 승인 작업창에서만 `--approved`로 실행

### 7.2 사전 확인

dns02 Prompt에서 실행한다.

```bash
test "$(hostnamectl --static)" = "dns02" || exit 1
test "$(whoami)" = "server08" || exit 1

sudo -v
sudo systemctl is-active named
sudo rndc zonestatus fds.internal
dig @10.1.93.52 fds.internal SOA +norecurse +nocookie
```

필수 사전 조건:

- `named`: `active`
- `type: secondary`
- Primary SOA 응답: `NOERROR`, `aa`, Serial `2026090101`

### 7.3 승인 후 실행

```bash
work_root="/home/server08/p1-dns-01-r2"
script_path="${work_root}/scripts/collect_dns02_fresh_tsig_evidence.sh"
output_root="${work_root}/output"

cd "${work_root}" || exit 1
pwd

bash "${script_path}" --approved "${output_root}"
collector_rc=$?
printf 'Collector exit code: %s\n' "${collector_rc}"
test "${collector_rc}" -eq 0
```

### 7.4 dns02 로컬 검증

```bash
tsig_dir="/home/server08/p1-dns-01-r2/output/tsig"

find "${tsig_dir}" -maxdepth 1 -type f \
  -printf '%f | %s bytes\n' | sort

cd "${tsig_dir}" || exit 1
sha256sum --check ./*.sha256

grep -F 'type: secondary' ./*_dns02_fresh_tsig_evidence.txt
grep -E 'connected using .*TSIG fds-transfer-key|TSIG .fds-transfer-key.' \
  ./*_dns02_fresh_tsig_evidence.txt
grep -E 'Transfer status: success|Transfer completed' \
  ./*_dns02_fresh_tsig_evidence.txt
grep -F 'PASS: fresh timestamped TSIG zone transfer was observed' \
  ./*_dns02_fresh_tsig_evidence.txt

if grep -Eq '^(FAIL|ERROR):' ./*_dns02_fresh_tsig_evidence.txt; then
  echo 'STOP: TSIG evidence contains FAIL/ERROR'
  exit 1
fi

if grep -E 'BADKEY|BADSIG' ./*_dns02_fresh_tsig_evidence.txt \
  | grep -Fvq 'PASS: no BADKEY/BADSIG occurred in the fresh transfer window'; then
  echo 'STOP: TSIG transfer log contains BADKEY/BADSIG'
  exit 1
fi
```

완료 결과는 TXT 한 개와 같은 이름의 `.sha256` 한 개다. TSIG Secret, Key 파일, Key Hash, 인증 AXFR MAC은 수집하거나 제출하지 않는다.

---

## 8. 단계 E — DNS Host 결과를 ansible01로 전송

### 8.1 Windows Host로 다운로드

Windows Host에서 WinSCP를 사용한다.

| 원격 Host | 원격 원본 | Windows 목적지 |
|---|---|---|
| dns01 `10.1.93.52` | `/home/server01_dns01/p1-dns-01-r2/output/inventory/` | `C:\Users\soldesk\Documents\FDS\P1-DNS-01\R2-transfer\host-output\dns01\inventory\` |
| dns02 `10.1.93.53` | `/home/server08/p1-dns-01-r2/output/tsig/` | `C:\Users\soldesk\Documents\FDS\P1-DNS-01\R2-transfer\host-output\dns02\tsig\` |

각 폴더에는 TXT 한 개와 동일 이름의 `.sha256` 한 개만 둔다. 실패한 실행 파일과 중복 Collector 파일은 복사하지 않는다.

### 8.2 Windows Host에서 ansible01로 업로드

WinSCP로 `ansible01(10.250.10.10)`에 `server01_ansible` 계정으로 접속한 후 업로드한다.

| Windows 원본 | ansible01 목적지 |
|---|---|
| `...\host-output\dns01\inventory\*.txt*` | `/home/server01_ansible/p1-dns-01-r2/incoming/dns01/inventory/` |
| `...\host-output\dns02\tsig\*.txt*` | `/home/server01_ansible/p1-dns-01-r2/incoming/dns02/tsig/` |

ansible01의 최종 수신 구조는 아래와 같아야 한다.

```text
/home/server01_ansible/p1-dns-01-r2/incoming/dns01/inventory/<timestamp>_dns_record_inventory_evidence.txt
/home/server01_ansible/p1-dns-01-r2/incoming/dns01/inventory/<timestamp>_dns_record_inventory_evidence.txt.sha256
/home/server01_ansible/p1-dns-01-r2/incoming/dns02/tsig/<timestamp>_dns02_fresh_tsig_evidence.txt
/home/server01_ansible/p1-dns-01-r2/incoming/dns02/tsig/<timestamp>_dns02_fresh_tsig_evidence.txt.sha256
```

`inventory/inventory` 또는 `tsig/tsig`처럼 디렉터리가 이중으로 생성되면 안 된다.

### 8.3 ansible01 중앙 수신 검증

ansible01 Prompt에서 실행한다.

```bash
test "$(hostnamectl --static)" = "ansible01" || exit 1
test "$(whoami)" = "server01_ansible" || exit 1

central_root="/home/server01_ansible/p1-dns-01-r2"
incoming_root="${central_root}/incoming"

cd "${incoming_root}/dns01/inventory" || exit 1
sha256sum --check ./*.sha256

cd "${incoming_root}/dns02/tsig" || exit 1
sha256sum --check ./*.sha256

test "$(find "${incoming_root}/dns01/inventory" -maxdepth 1 \
  -type f -name '*_dns_record_inventory_evidence.txt' | wc -l)" -eq 1

test "$(find "${incoming_root}/dns02/tsig" -maxdepth 1 \
  -type f -name '*_dns02_fresh_tsig_evidence.txt' | wc -l)" -eq 1
```

이번 R2 보완에서는 Inventory와 Fresh TSIG 원본을 각각 한 개만 사용한다. 실패한 이전 실행 파일이나 중복 파일을 중앙 R2에 넣지 않는다.

---

## 9. 단계 F — 중앙에서 R2 조립

### 9.1 R1을 검증한 뒤 R2 작업본 생성

ansible01 Prompt에서 실행한다.

```bash
test "$(hostnamectl --static)" = "ansible01" || exit 1
test "$(whoami)" = "server01_ansible" || exit 1

central_root="/home/server01_ansible/p1-dns-01-r2"
incoming_root="${central_root}/incoming"
work_root="${central_root}/work"
kit_extract_root="${central_root}/kit"
kit_root="${kit_extract_root}/P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8"

r1_root="${work_root}/r1-extract/P1-DNS-01-FRESH-20260902-R1"
r2_root="${work_root}/P1-DNS-01-FRESH-20260902-R2"

test -d "${r1_root}"
test ! -e "${r2_root}"

cd "${r1_root}" || exit 1
sha256sum --check SHA256SUMS

cp -a "${r1_root}" "${r2_root}"
```

`test ! -e`가 실패하면 기존 R2 작업본을 덮어쓰지 않는다. 원인을 확인하고 별도 보관 또는 승인된 정리 후 다시 시작한다.

### 9.2 신규 두 Evidence 추가

```bash
install -d -m 0750 \
  "${r2_root}/inventory" \
  "${r2_root}/tsig"

cp -a "${incoming_root}/dns01/inventory/." \
  "${r2_root}/inventory/"

cp -a "${incoming_root}/dns02/tsig/." \
  "${r2_root}/tsig/"

cd "${r2_root}/inventory" || exit 1
sha256sum --check ./*.sha256

cd "${r2_root}/tsig" || exit 1
sha256sum --check ./*.sha256
```

### 9.3 Test ID 인덱스와 중앙 Hash 생성

실행 위치는 `ansible01`, 계정은 `server01_ansible`이다. 아래 블록은 Script의 제공 위치와 R2 입력 구조를 먼저 확인한 다음 인덱스와 중앙 Hash를 생성한다.

```bash
(
  set -euo pipefail

  test "$(hostnamectl --static)" = "ansible01"
  test "$(whoami)" = "server01_ansible"

  central_root="/home/server01_ansible/p1-dns-01-r2"
  work_root="${central_root}/work"
  kit_root="${central_root}/kit/P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8"
  r2_root="${work_root}/P1-DNS-01-FRESH-20260902-R2"

  index_script="${kit_root}/scripts/generate_evidence_index.sh"
  checksum_script="${kit_root}/scripts/generate_checksums_r2.sh"

  test -d "${r2_root}"
  test -s "${index_script}"
  test -s "${checksum_script}"
  bash -n "${index_script}"
  bash -n "${checksum_script}"

  cd "${kit_root}"
  sha256sum --check PACKAGE_CONTENT_SHA256SUMS

  bash "${index_script}" "${r2_root}"
  bash "${checksum_script}" "${r2_root}"

  cd "${r2_root}"
  sha256sum --check SHA256SUMS

  test "$(find . -type f -name '*.txt' | wc -l)" -eq 11
  test "$(find . -type f -name '*.txt.sha256' | wc -l)" -eq 11
  test "$(grep -cE '^[0-9a-fA-F]{64}[[:space:]]+' SHA256SUMS)" -eq 12
  grep -F '| DNS-EV-03 | 중앙 무결성 | PASS |' EVIDENCE_INDEX.md

  echo 'PASS: R2 index and central SHA256SUMS are ready'
)
```

예상 결과:

- Raw TXT: 11개
- 신규 인덱스: `EVIDENCE_INDEX.md`
- 중앙 Manifest: `SHA256SUMS`
- 현재 고정 구성에서는 `SHA256SUMS`: 정확히 12개 항목
- 모든 원본 TXT에 동일 이름의 `.sha256` 존재
- `DNS-EV-03`: `PASS`

---

## 10. 단계 G — R2 ZIP 생성과 최종 검증

### 10.1 ZIP과 외부 Sidecar 생성

ansible01 Prompt에서 실행한다. 새 Shell이라면 아래 변수부터 다시 정의한다.

```bash
central_root="/home/server01_ansible/p1-dns-01-r2"
work_root="${central_root}/work"
kit_root="${central_root}/kit/P1-DNS-01_R2_Evidence_Remediation_Kit_v1.8"
r2_root="${work_root}/P1-DNS-01-FRESH-20260902-R2"

cd "${work_root}" || exit 1
run_id="P1-DNS-01-FRESH-20260902-R2"

test ! -e "${run_id}.zip"
test ! -e "${run_id}.zip.sha256"

zip -qr "${run_id}.zip" "${run_id}"
sha256sum "${run_id}.zip" > "${run_id}.zip.sha256"
```

기존 ZIP 또는 Sidecar가 있으면 위 `test ! -e`에서 중단한다. 기존 ZIP에 Update 방식으로 덮어쓰면 삭제된 과거 Entry가 남을 수 있으므로 재사용하지 않는다. 별도 보관 또는 삭제는 Lead 승인 후 수행한다.

### 10.2 Kit Validator 실행

```bash
bash "${kit_root}/scripts/validate_r2_package.sh" \
  "${work_root}/P1-DNS-01-FRESH-20260902-R2.zip" \
  "${work_root}/P1-DNS-01-FRESH-20260902-R2.zip.sha256"
```

완료 조건:

- `PASS: ZIP SHA-256`
- `No errors detected in compressed data`
- `PASS: required R2 package members are present`

### 10.3 Secret 포함 여부 최종 확인

```bash
if find "${r2_root}" -type f \
  \( -name '*.key' -o -path '*/keys/*' \) -print -quit \
  | grep -q .; then
  echo 'STOP: key file exists in R2 evidence'
  exit 1
fi

if grep -RIEq \
  'secret[[:space:]]+"[^"]+"|-----BEGIN [A-Z ]*PRIVATE KEY-----|authorization:[[:space:]]*(basic|bearer)|password[[:space:]]*[:=][[:space:]]*[^*[:space:]]+' \
  "${r2_root}" --include='*.txt' --include='*.md'; then
  echo 'STOP: possible plaintext secret exists in R2 evidence'
  exit 1
fi

echo 'PASS: no submitted key file or detected plaintext secret pattern'
```

---

## 11. 단계 H — 정본 Evidence 경로 반영

ansible01 Prompt에서만 실행한다.

```bash
test "$(hostnamectl --static)" = "ansible01" || exit 1
test "$(whoami)" = "server01_ansible" || exit 1

central_root="/home/server01_ansible/p1-dns-01-r2"
work_root="${central_root}/work"
canonical_root="${central_root}/docs/evidence/P1-DNS-01"
r2_root="${work_root}/P1-DNS-01-FRESH-20260902-R2"

final_run_root="${canonical_root}/P1-DNS-01-FRESH-20260902-R2"
final_zip="${canonical_root}/P1-DNS-01-FRESH-20260902-R2.zip"
final_zip_hash="${canonical_root}/P1-DNS-01-FRESH-20260902-R2.zip.sha256"

test ! -e "${final_run_root}"
test ! -e "${final_zip}"
test ! -e "${final_zip_hash}"

cp -a "${r2_root}" "${final_run_root}"
cp -a "${work_root}/P1-DNS-01-FRESH-20260902-R2.zip" \
  "${final_zip}"
cp -a "${work_root}/P1-DNS-01-FRESH-20260902-R2.zip.sha256" \
  "${final_zip_hash}"

cd "${canonical_root}" || exit 1
sha256sum --check P1-DNS-01-FRESH-20260902-R2.zip.sha256

cd "${final_run_root}" || exit 1
sha256sum --check SHA256SUMS

find "${canonical_root}" -maxdepth 2 -type f \
  -printf '%p | %s bytes\n' | LC_ALL=C sort
```

정본 반영 결과를 검수한 뒤 프로젝트의 승인·배포 절차에 따라 처리한다.

---

## 12. 기존 Failover 중복 처리 원칙

R1에서 수행한 한 번의 dns01 중단으로 다음 두 Consumer의 자동 Failover를 함께 검증했다.

- `k8s-control01` (`10.1.93.102`)
- `k8s-api-lb01` (`10.1.93.109`)

따라서 R2에서는 아래 기존 파일을 그대로 승계한다.

```text
failover/*_k8s_control01_failover_evidence.txt
failover/*_k8s_api_lb01_failover_evidence.txt
recovery/*_dns01_recovery_evidence.txt
rollback/*_k8s_control01_rollback_evidence.txt
```

동일 Failover를 다시 실행하거나 세 번째 중복 파일을 만들지 않는다. R2에서 재실행하는 장애성 작업은 없다.

## 13. 실패 시 처리

| 실패 지점 | 처리 |
|---|---|
| Inventory 13개 중 불일치 | dns01/dns02 Zone 상태를 확인하고 Inventory Collector만 다시 실행 |
| dns01 또는 dns02가 `aa` 응답 미제공 | 해당 DNS 서비스·Zone 상태 확인 후 Inventory Collector만 다시 실행 |
| Fresh TSIG 성공 로그 미수집 | 새 승인 작업창을 받은 뒤 dns02 Fresh TSIG Collector만 다시 실행 |
| `BADKEY`/`BADSIG` | TSIG 설정 불일치 원인 해결 전 중단 |
| Sidecar 불일치 | 전송 손상 여부 확인 후 해당 TXT와 Sidecar 쌍만 다시 전송 |
| 중앙 `SHA256SUMS` 실패 | R2 조립 중 파일 변경 여부 확인 후 인덱스·중앙 Hash 재생성 |
| Secret 탐지 | 제출 중단, 노출 파일 제거가 아니라 원 수집 절차를 수정해 Evidence 재수집 |

실패한 Collector 결과는 R2 정본에 포함하지 않는다. 기존 R1 승인 결과와 기존 Failover/Recovery/Rollback Evidence는 다시 생성하지 않는다.

## 14. 최종 제출 파일

ansible01의 정본 경로에는 아래 세 항목이 있어야 한다.

```text
/home/server01_ansible/p1-dns-01-r2/docs/evidence/P1-DNS-01/P1-DNS-01-FRESH-20260902-R2/
/home/server01_ansible/p1-dns-01-r2/docs/evidence/P1-DNS-01/P1-DNS-01-FRESH-20260902-R2.zip
/home/server01_ansible/p1-dns-01-r2/docs/evidence/P1-DNS-01/P1-DNS-01-FRESH-20260902-R2.zip.sha256
```

Support Review 전 상태는 `In Review`로 유지한다. 기술 검증과 Evidence 무결성이 모두 PASS여도 Support Review 승인 전에는 `DONE/CLOSED`로 변경하지 않는다.

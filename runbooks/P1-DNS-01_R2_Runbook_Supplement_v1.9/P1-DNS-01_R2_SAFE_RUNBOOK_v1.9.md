# P1-DNS-01 R2 안전 실행 Runbook v1.9

## 1. 적용 범위

이 Runbook은 P1-DNS-01 R2 증적의 중앙 검증·패키징 절차를 안전하게 실행하기 위한 보완본이다. 현재 정본에 대한 기본 작업은 **읽기 전용 검증**이다.

다음 작업은 수행하지 않는다.

- dns01/dns02 Collector 재실행
- TSIG 재전송 또는 Key Rotation
- dns01 `named` 중단
- Failover/Recovery/Resolver Rollback 재실행
- 기존 R2 정본 Directory, ZIP 또는 Sidecar 덮어쓰기
- Support Review 전 Backup/Stage 삭제

## 2. 실행 위치

| 구분 | 필수값 |
|---|---|
| 서버 | `ansible01` |
| 계정 | `server01_ansible` |
| 시작 디렉터리 | `/home/server01_ansible/p1-dns-01-r2` |
| Kit 경로 | `/home/server01_ansible/p1-dns-01-r2/kit/P1-DNS-01_R2_Runbook_Supplement_v1.9` |
| 정본 Root | `/home/server01_ansible/p1-dns-01-r2/docs/evidence/P1-DNS-01` |

본 절차에서 말하는 시작 디렉터리는 Git 저장소 최상위가 아니다. DNS 증적 중앙 작업 전용 디렉터리 `/home/server01_ansible/p1-dns-01-r2`를 의미한다.

## 3. 대화형 셸 안전 규칙

### 금지

터미널에 직접 붙여넣는 코드에서 다음 패턴을 사용하지 않는다.

<!-- FORBIDDEN-INTERACTIVE-EXAMPLE-START -->
```bash
test "$(hostnamectl --static)" = "ansible01" || exit 1
cd "${some_path}" || exit 1
```
<!-- FORBIDDEN-INTERACTIVE-EXAMPLE-END -->

위 `exit`는 별도 Script가 아니라 현재 SSH 셸에서 실행되면 세션 자체를 종료할 수 있다.

### 허용

위험 구간은 반드시 Subshell로 감싸고, 종료 후 상위 셸에서 Return Code를 확인한다.

```bash
(
  set -euo pipefail

  actual_host="$(hostnamectl --static)"
  actual_user="$(whoami)"

  test "${actual_host}" = "ansible01"
  test "${actual_user}" = "server01_ansible"

  central_root="/home/server01_ansible/p1-dns-01-r2"
  cd "${central_root}"

  printf 'host=%s\n' "${actual_host}"
  printf 'user=%s\n' "${actual_user}"
  printf 'pwd=%s\n' "$(pwd)"
)

guard_rc=$?
printf 'Guard return code: %s\n' "${guard_rc}"

if (( guard_rc != 0 )); then
  echo 'STOP: precondition failed; terminal remains active'
fi
```

`guard_rc`가 0이 아니면 다음 단계로 진행하지 않는다. 명령어를 추가로 붙여넣지 말고 실패 원인만 확인한다.

별도 `.sh` 파일 내부의 `exit`는 실행 Script 프로세스만 종료하므로 허용한다. Collector 내부 `exit`를 임의로 제거하지 않는다.

## 4. 세션 및 파일 Precheck

ansible01의 `server01_ansible` 계정으로 접속한 뒤 다음 블록 전체를 한 번에 실행한다.

```bash
(
  set -euo pipefail

  actual_host="$(hostnamectl --static)"
  actual_user="$(whoami)"

  test "${actual_host}" = "ansible01"
  test "${actual_user}" = "server01_ansible"

  central_root="/home/server01_ansible/p1-dns-01-r2"
  kit_root="${central_root}/kit/P1-DNS-01_R2_Runbook_Supplement_v1.9"
  canonical_root="${central_root}/docs/evidence/P1-DNS-01"
  run_id="P1-DNS-01-FRESH-20260902-R2"

  cd "${central_root}"

  echo '===== SESSION ====='
  printf 'host=%s\n' "${actual_host}"
  printf 'user=%s\n' "${actual_user}"
  printf 'pwd=%s\n' "$(pwd)"

  echo '===== REQUIRED COMMANDS ====='
  command -v bash
  command -v sha256sum
  command -v unzip
  command -v find
  command -v awk
  command -v grep

  echo '===== REQUIRED FILES ====='
  test -s "${kit_root}/scripts/validate_canonical_r2_v1_9.sh"
  test -s "${kit_root}/scripts/validate_runbook_v1_9.sh"
  test -d "${canonical_root}/${run_id}"
  test -s "${canonical_root}/${run_id}.zip"
  test -s "${canonical_root}/${run_id}.zip.sha256"

  echo 'PASS: precheck'
)

precheck_rc=$?
printf 'Precheck return code: %s\n' "${precheck_rc}"

if (( precheck_rc != 0 )); then
  echo 'STOP: do not run canonical validation'
fi
```

성공 기준은 `Precheck return code: 0`이다.

## 5. v1.9 Runbook 자체 검증

Precheck가 성공했을 때만 실행한다.

```bash
central_root="/home/server01_ansible/p1-dns-01-r2"
kit_root="${central_root}/kit/P1-DNS-01_R2_Runbook_Supplement_v1.9"

bash "${kit_root}/scripts/validate_runbook_v1_9.sh" \
  "${kit_root}"

runbook_rc=$?
printf 'Runbook validation return code: %s\n' "${runbook_rc}"
```

성공 기준은 다음과 같다.

- Script Syntax PASS
- 대화형 코드의 `|| exit` 금지 규칙 PASS
- 상대 ZIP Sidecar 규칙 PASS
- 서버·계정·실행 디렉터리 표기 PASS
- `Runbook validation return code: 0`

## 6. 현재 R2 정본 읽기 전용 검증

Runbook 자체 검증이 성공했을 때만 실행한다.

```bash
central_root="/home/server01_ansible/p1-dns-01-r2"
kit_root="${central_root}/kit/P1-DNS-01_R2_Runbook_Supplement_v1.9"

bash "${kit_root}/scripts/validate_canonical_r2_v1_9.sh" \
  "${central_root}/docs/evidence/P1-DNS-01"

canonical_rc=$?
printf 'Canonical validation return code: %s\n' "${canonical_rc}"
```

성공 기준은 다음과 같다.

- ZIP Sidecar 대상이 `P1-DNS-01-FRESH-20260902-R2.zip`
- ZIP Expected/Actual SHA-256 일치
- ZIP CRC PASS
- 내부 `SHA256SUMS` 전체 PASS
- Raw TXT 11개
- TXT Sidecar 11개
- Manifest 12개 항목
- DNS-EV-03 PASS
- `.109` Evidence 존재
- k8s-control01과 k8s-api-lb01 Failover Evidence 구분
- TSIG Secret Pattern 미검출
- `Canonical validation return code: 0`

## 7. ZIP Sidecar 상대경로 생성 규칙

이 절차는 현재 정본에 재실행하지 않는다. 향후 승인된 새 패키지를 생성할 때만 사용한다.

### 올바른 방식

```bash
(
  set -euo pipefail

  work_root="/home/server01_ansible/p1-dns-01-r2/work"
  run_id="P1-DNS-01-FRESH-20260902-R2"
  zip_name="${run_id}.zip"
  sidecar_name="${zip_name}.sha256"

  cd "${work_root}"

  test -s "${zip_name}"
  sha256sum "${zip_name}" > "${sidecar_name}"

  sidecar_target="$(awk 'NF >= 2 { print $2; exit }' "${sidecar_name}")"
  test "${sidecar_target}" = "${zip_name}"

  case "${sidecar_target}" in
    */*)
      echo "FAIL: sidecar target must be a basename: ${sidecar_target}" >&2
      false
      ;;
  esac

  sha256sum --check "${sidecar_name}"
  echo 'PASS: relative ZIP sidecar'
)

sidecar_rc=$?
printf 'Sidecar return code: %s\n' "${sidecar_rc}"

if (( sidecar_rc != 0 )); then
  echo 'STOP: do not promote this package'
fi
```

### 금지 방식

```bash
sha256sum "/home/server01_ansible/p1-dns-01-r2/work/P1-DNS-01-FRESH-20260902-R2.zip" \
  > P1-DNS-01-FRESH-20260902-R2.zip.sha256
```

절대경로 입력은 Sidecar의 두 번째 필드에 절대경로를 남길 수 있으므로 사용하지 않는다.

## 8. 중단 및 재개 기준

| 상황 | 조치 |
|---|---|
| Host/User/PWD 불일치 | 즉시 중단, 올바른 ansible01 세션에서 재시작 |
| Kit Script 누락 | 파일을 임의 생성하지 않고 배포본 재전송 |
| ZIP Hash 불일치 | 정본 덮어쓰기 금지, Support/Lead에게 보고 |
| 내부 `SHA256SUMS` 실패 | 정본 수정 금지, 실패 파일 식별 후 별도 Change 판단 |
| Raw/Sidecar/Manifest Count 불일치 | 정본 수정 금지, 중복·누락 원인 분석 |
| Secret Pattern 검출 | 배포 중단, Evidence 격리 및 Secret Rotation 검토 |
| Terminal은 살아 있으나 Return Code 비정상 | 실패 원인 확인 후 해당 단계만 재실행 |

## 9. 보존 대상

Support Review가 끝날 때까지 다음을 삭제하지 않는다.

- `/home/server01_ansible/p1-dns-01-r2/backup-canonical-pre-v18-*`
- `/home/server01_ansible/p1-dns-01-r2/canonical-stage-v18.*`
- `/home/server01_ansible/p1-dns-01-r2/backup-before-v18-20260903T103235+0900`
- 현재 정본 Directory, ZIP 및 ZIP Sidecar

`backup-before-v18-20260903T102956+0900`은 불완전 가능성이 있는 과거 작업 흔적으로, Support Review 전에는 삭제하지 않고 정본/복구본으로 사용하지 않는다.

## 10. P1-DNS-01 반영 기준

다음이 모두 충족되면 P1-DNS-01의 `DNS-AC-15`를 PASS로 전환할 수 있다.

- v1.9 보완본 배포
- `validate_runbook_v1_9.sh` Return Code 0
- `validate_canonical_r2_v1_9.sh` Return Code 0
- 정본 ZIP Hash 불변 확인
- 기존 R2 원본 Evidence 무수정 확인

이후 남는 직접 종료 게이트는 이하영 Support Review 승인이다.

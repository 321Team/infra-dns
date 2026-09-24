#!/usr/bin/env bash
set -euo pipefail
umask 027

if [[ $# -ne 1 || -z "${1:-}" ]]; then
  printf 'Usage: %s <central-r2-evidence-root>\n' "$0" >&2
  exit 64
fi

evidence_root="$1"

if [[ ! -d "${evidence_root}" || ! -w "${evidence_root}" ]]; then
  printf 'ERROR: Evidence root is missing or not writable: %s\n' "${evidence_root}" >&2
  exit 73
fi

required_patterns=(
  'dns01/*_dns01_evidence.txt'
  'dns02/*_dns02_evidence.txt'
  'client/*_k8s_control01_evidence.txt'
  'lb/*_k8s_api_lb01_evidence.txt'
  'monitor01/*_monitor01_negative.txt'
  'failover/*_k8s_control01_failover_evidence.txt'
  'failover/*_k8s_api_lb01_failover_evidence.txt'
  'recovery/*_dns01_recovery_evidence.txt'
  'rollback/*_k8s_control01_rollback_evidence.txt'
  'inventory/*_dns_record_inventory_evidence.txt'
  'tsig/*_dns02_fresh_tsig_evidence.txt'
)

missing_required=0
shopt -s nullglob
for required_pattern in "${required_patterns[@]}"; do
  matches=("${evidence_root}"/${required_pattern})
  if (( ${#matches[@]} == 0 )); then
    printf 'MISSING REQUIRED EVIDENCE: %s\n' "${required_pattern}" >&2
    missing_required=1
  fi
done
shopt -u nullglob

if [[ ! -s "${evidence_root}/EVIDENCE_INDEX.md" ]]; then
  echo 'MISSING REQUIRED EVIDENCE: EVIDENCE_INDEX.md' >&2
  missing_required=1
fi

if (( missing_required != 0 )); then
  echo 'SHA256SUMS was not generated because R2 is incomplete.' >&2
  exit 66
fi

sidecar_failure=0
result_failure=0
while IFS= read -r -d '' evidence_file; do
  sidecar_file="${evidence_file}.sha256"
  if [[ ! -f "${sidecar_file}" ]]; then
    printf 'MISSING SIDECAR: %s\n' "${sidecar_file}" >&2
    sidecar_failure=1
  else
    (
      cd "$(dirname "${sidecar_file}")"
      sha256sum --check "$(basename "${sidecar_file}")"
    ) || sidecar_failure=1
  fi

  if grep -Eq '^(FAIL|ERROR):' "${evidence_file}"; then
    printf 'FAILURE MARKER: %s\n' "${evidence_file}" >&2
    result_failure=1
  fi
done < <(find "${evidence_root}" -type f -name '*.txt' -print0)

if (( sidecar_failure != 0 )); then
  echo 'SHA256SUMS was not generated because a Sidecar check failed.' >&2
  exit 74
fi

if (( result_failure != 0 )); then
  echo 'SHA256SUMS was not generated because a Collector failure marker exists.' >&2
  exit 65
fi

if find "${evidence_root}" -type f \( -name '*.key' -o -path '*/keys/*' \) -print -quit | grep -q .; then
  echo 'SECURITY FAIL: Secret/Key file exists in the R2 Evidence root.' >&2
  exit 78
fi

if grep -RIEq \
  'secret[[:space:]]+"[^"]+"|-----BEGIN [A-Z ]*PRIVATE KEY-----|authorization:[[:space:]]*(basic|bearer)|password[[:space:]]*[:=][[:space:]]*[^*[:space:]]+' \
  "${evidence_root}" --include='*.txt' --include='*.md'; then
  echo 'SECURITY FAIL: potential plaintext secret pattern detected.' >&2
  exit 78
fi

manifest="${evidence_root}/SHA256SUMS"
temporary_manifest="$(mktemp "${evidence_root}/.SHA256SUMS.tmp.XXXXXX")" || exit 73
trap 'rm -f "${temporary_manifest}"' EXIT

(
  cd "${evidence_root}"
  find . -type f \
    ! -name '*.sha256' \
    ! -name 'SHA256SUMS' \
    ! -name '.SHA256SUMS.tmp.*' \
    ! -name '*.key' \
    ! -path '*/keys/*' \
    -print0 \
    | LC_ALL=C sort -z \
    | xargs -0 -r sha256sum
) > "${temporary_manifest}"

entry_count="$(wc -l < "${temporary_manifest}")"
if (( entry_count < 12 )); then
  printf 'ERROR: central manifest has %d entries; at least 12 required.\n' "${entry_count}" >&2
  exit 65
fi

mv "${temporary_manifest}" "${manifest}"
chmod 0640 "${manifest}"
trap - EXIT

printf 'Created: %s (%d entries)\n' "${manifest}" "${entry_count}"
(
  cd "${evidence_root}"
  sha256sum --check SHA256SUMS
)

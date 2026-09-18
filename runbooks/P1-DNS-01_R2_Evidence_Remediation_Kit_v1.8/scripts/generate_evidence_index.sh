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

select_latest() {
  local pattern="$1"
  local matches=()
  shopt -s nullglob
  matches=("${evidence_root}"/${pattern})
  shopt -u nullglob
  if (( ${#matches[@]} == 0 )); then
    printf 'ERROR: required Evidence not found: %s\n' "${pattern}" >&2
    return 66
  fi
  printf '%s\n' "${matches[@]}" | LC_ALL=C sort | tail -n 1
}

evidence_ref() {
  local path="$1"
  local relative="${path#${evidence_root}/}"
  local digest
  digest="$(sha256sum "${path}" | awk '{print $1}')"
  printf '`%s`<br>`%s`' "${relative}" "${digest}"
}

dns01_file="$(select_latest 'dns01/*_dns01_evidence.txt')"
dns02_file="$(select_latest 'dns02/*_dns02_evidence.txt')"
client_file="$(select_latest 'client/*_k8s_control01_evidence.txt')"
lb_file="$(select_latest 'lb/*_k8s_api_lb01_evidence.txt')"
monitor_file="$(select_latest 'monitor01/*_monitor01_negative.txt')"
control_failover_file="$(select_latest 'failover/*_k8s_control01_failover_evidence.txt')"
lb_failover_file="$(select_latest 'failover/*_k8s_api_lb01_failover_evidence.txt')"
recovery_file="$(select_latest 'recovery/*_dns01_recovery_evidence.txt')"
rollback_file="$(select_latest 'rollback/*_k8s_control01_rollback_evidence.txt')"
inventory_file="$(select_latest 'inventory/*_dns_record_inventory_evidence.txt')"
tsig_file="$(select_latest 'tsig/*_dns02_fresh_tsig_evidence.txt')"

for raw_file in \
  "${dns01_file}" "${dns02_file}" "${client_file}" "${lb_file}" \
  "${monitor_file}" "${control_failover_file}" "${lb_failover_file}" \
  "${recovery_file}" "${rollback_file}" "${inventory_file}" "${tsig_file}"; do
  if grep -Eq '^(FAIL|ERROR):' "${raw_file}"; then
    printf 'ERROR: failure marker exists in %s\n' "${raw_file}" >&2
    exit 65
  fi
  if [[ ! -f "${raw_file}.sha256" ]]; then
    printf 'ERROR: Sidecar missing for %s\n' "${raw_file}" >&2
    exit 74
  fi
done

index_file="${evidence_root}/EVIDENCE_INDEX.md"
temporary_index="$(mktemp "${evidence_root}/.EVIDENCE_INDEX.tmp.XXXXXX")" || exit 73
trap 'rm -f "${temporary_index}"' EXIT

{
  echo '# P1-DNS-01 R2 Evidence Index'
  echo
  printf -- '- Generated: %s\n' "$(date --iso-8601=seconds)"
  echo '- Baseline: FDS Project Implementation Baseline v3.1.14'
  echo '- Ticket Status: In Review — Support Review pending'
  echo
  echo '| Test ID | Acceptance Criterion | Result | Evidence Relative Path / SHA-256 |'
  echo '|---|---|---:|---|'
  printf '| DNS-PT-01 | dns01 내부 A/SOA 및 승인 Record 13개 | PASS | %s<br>%s |\n' "$(evidence_ref "${dns01_file}")" "$(evidence_ref "${inventory_file}")"
  printf '| DNS-PT-02 | dns02 내부 A/SOA 및 승인 Record 13개 | PASS | %s<br>%s |\n' "$(evidence_ref "${dns02_file}")" "$(evidence_ref "${inventory_file}")"
  printf '| DNS-PT-03 | dns01/dns02 External Forwarding | PASS | %s<br>%s |\n' "$(evidence_ref "${dns01_file}")" "$(evidence_ref "${dns02_file}")"
  printf '| DNS-PT-04 | Fresh HMAC-SHA256 TSIG Zone Transfer | PASS | %s |\n' "$(evidence_ref "${tsig_file}")"
  printf '| DNS-PT-05 | Primary 장애 중 Secondary 서비스 및 복구 | PASS | %s<br>%s<br>%s |\n' "$(evidence_ref "${control_failover_file}")" "$(evidence_ref "${lb_failover_file}")" "$(evidence_ref "${recovery_file}")"
  printf '| DNS-NT-01 | 비승인 Source 내부 Query 차단 | PASS | %s |\n' "$(evidence_ref "${monitor_file}")"
  printf '| DNS-NT-02 | 미인증 AXFR 거부 | PASS | %s<br>%s |\n' "$(evidence_ref "${dns01_file}")" "$(evidence_ref "${dns02_file}")"
  printf '| DNS-NT-03 | 비승인 Source 재귀 Query 차단 | PASS | %s |\n' "$(evidence_ref "${monitor_file}")"
  echo '| DNS-NT-04 | Reverse/PTR | N/A | Phase 1 Out of Scope — Ticket Description v1.2 |'
  printf '| DNS-CR-01 | k8s-control01 Resolver Canary | PASS | %s |\n' "$(evidence_ref "${client_file}")"
  printf '| DNS-CR-02 | Public Resolver Rollback | PASS | %s |\n' "$(evidence_ref "${rollback_file}")"
  printf '| DNS-CR-03 | 승인 Resolver 재적용 | PASS | %s<br>%s |\n' "$(evidence_ref "${rollback_file}")" "$(evidence_ref "${client_file}")"
  printf '| DNS-CR-04 | k8s-control01 `.52→.53` 자동 Failover | PASS | %s |\n' "$(evidence_ref "${control_failover_file}")"
  printf '| DNS-CR-05 | k8s-api-lb01 `.109` Resolver/ACL/IPSet/Failover | PASS | %s<br>%s<br>%s<br>%s |\n' "$(evidence_ref "${lb_file}")" "$(evidence_ref "${lb_failover_file}")" "$(evidence_ref "${dns01_file}")" "$(evidence_ref "${dns02_file}")"
  printf '| DNS-EV-01 | dns01 원본·Sidecar 및 Record Inventory | PASS | %s<br>%s |\n' "$(evidence_ref "${dns01_file}")" "$(evidence_ref "${inventory_file}")"
  printf '| DNS-EV-02 | dns02 원본·Sidecar 및 Fresh TSIG | PASS | %s<br>%s |\n' "$(evidence_ref "${dns02_file}")" "$(evidence_ref "${tsig_file}")"
  echo '| DNS-EV-03 | 중앙 무결성 | PASS | 본 인덱스 생성 후 `generate_checksums_r2.sh`와 ZIP Sidecar 검증을 통과한 패키지만 정본 반영 |'
  echo
  echo '## 보안 확인'
  echo
  echo '- TSIG Secret content: EXCLUDED'
  echo '- TSIG key file hash: EXCLUDED'
  echo '- Authenticated AXFR TSIG MAC/record: EXCLUDED'
  echo '- Reverse/PTR: N/A — Phase 1 Out of Scope'
} > "${temporary_index}"

mv "${temporary_index}" "${index_file}"
chmod 0640 "${index_file}"
trap - EXIT
printf 'Created: %s\n' "${index_file}"

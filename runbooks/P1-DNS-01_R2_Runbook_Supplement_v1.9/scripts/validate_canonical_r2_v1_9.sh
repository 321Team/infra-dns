#!/usr/bin/env bash

set -uo pipefail

canonical_root="${1:-/home/server01_ansible/p1-dns-01-r2/docs/evidence/P1-DNS-01}"
run_id="P1-DNS-01-FRESH-20260902-R2"
run_root="${canonical_root}/${run_id}"
zip_name="${run_id}.zip"
zip_path="${canonical_root}/${zip_name}"
sidecar_name="${zip_name}.sha256"
sidecar_path="${canonical_root}/${sidecar_name}"
expected_zip_hash="e23d02a8422fdc4943ce2e255b5b087f0e58e5ad2a0439ddcf7d041276f315ab"
failures=0

pass() {
  printf 'PASS: %s\n' "$1"
}

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  failures=$((failures + 1))
}

actual_host="$(hostnamectl --static 2>/dev/null || hostname -s)"
actual_user="$(whoami)"

if [[ "${actual_host}" == "ansible01" ]]; then
  pass 'host is ansible01'
else
  fail "expected host ansible01, actual=${actual_host}"
fi

if [[ "${actual_user}" == "server01_ansible" ]]; then
  pass 'user is server01_ansible'
else
  fail "expected user server01_ansible, actual=${actual_user}"
fi

for required_path in \
  "${run_root}" \
  "${zip_path}" \
  "${sidecar_path}" \
  "${run_root}/EVIDENCE_INDEX.md" \
  "${run_root}/SHA256SUMS"
do
  if [[ -e "${required_path}" ]]; then
    pass "required path exists: ${required_path}"
  else
    fail "required path missing: ${required_path}"
  fi
done

if [[ ! -d "${run_root}" || ! -s "${zip_path}" || ! -s "${sidecar_path}" ]]; then
  printf 'RESULT: FAIL (%s issue(s))\n' "${failures}" >&2
  exit 1
fi

sidecar_hash="$(awk 'NF >= 2 { print $1; exit }' "${sidecar_path}")"
sidecar_target="$(awk 'NF >= 2 { print $2; exit }' "${sidecar_path}")"
actual_zip_hash="$(sha256sum "${zip_path}" | awk '{print $1}')"

if [[ "${sidecar_target}" == "${zip_name}" ]]; then
  pass 'ZIP sidecar target is relative basename'
else
  fail "ZIP sidecar target must be ${zip_name}, actual=${sidecar_target}"
fi

if [[ "${sidecar_target}" == */* ]]; then
  fail "ZIP sidecar target contains a path separator: ${sidecar_target}"
else
  pass 'ZIP sidecar target contains no path separator'
fi

if [[ "${sidecar_hash}" == "${expected_zip_hash}" ]]; then
  pass 'sidecar hash matches approved R2 hash'
else
  fail "sidecar hash mismatch: ${sidecar_hash}"
fi

if [[ "${actual_zip_hash}" == "${expected_zip_hash}" ]]; then
  pass 'actual ZIP hash matches approved R2 hash'
else
  fail "actual ZIP hash mismatch: ${actual_zip_hash}"
fi

if (
  cd "${canonical_root}" &&
  sha256sum --check "${sidecar_name}"
); then
  pass 'ZIP sidecar verification'
else
  fail 'ZIP sidecar verification'
fi

if unzip -t "${zip_path}" >/dev/null; then
  pass 'ZIP CRC verification'
else
  fail 'ZIP CRC verification'
fi

if (
  cd "${run_root}" &&
  sha256sum --check SHA256SUMS
); then
  pass 'internal SHA256SUMS verification'
else
  fail 'internal SHA256SUMS verification'
fi

raw_count="$(find "${run_root}" -type f -name '*.txt' | wc -l | tr -d '[:space:]')"
sidecar_count="$(find "${run_root}" -type f -name '*.txt.sha256' | wc -l | tr -d '[:space:]')"
manifest_count="$(grep -cE '^[0-9a-fA-F]{64}[[:space:]]+' "${run_root}/SHA256SUMS")"

if [[ "${raw_count}" == '11' ]]; then
  pass 'Raw TXT count is 11'
else
  fail "Raw TXT count expected 11, actual=${raw_count}"
fi

if [[ "${sidecar_count}" == '11' ]]; then
  pass 'TXT sidecar count is 11'
else
  fail "TXT sidecar count expected 11, actual=${sidecar_count}"
fi

if [[ "${manifest_count}" == '12' ]]; then
  pass 'SHA256SUMS entry count is 12'
else
  fail "SHA256SUMS entry count expected 12, actual=${manifest_count}"
fi

if grep -Fq '| DNS-EV-03 | 중앙 무결성 | PASS |' "${run_root}/EVIDENCE_INDEX.md"; then
  pass 'DNS-EV-03 is PASS'
else
  fail 'DNS-EV-03 PASS row is missing'
fi

if grep -RFl --include='*.txt' '10.1.93.109' "${run_root}" >/dev/null; then
  pass 'k8s-api-lb01 .109 evidence exists'
else
  fail 'k8s-api-lb01 .109 evidence is missing'
fi

control_failover_count="$(find "${run_root}/failover" -type f -name '*k8s_control01_failover_evidence.txt' 2>/dev/null | wc -l | tr -d '[:space:]')"
lb_failover_count="$(find "${run_root}/failover" -type f -name '*k8s_api_lb01_failover_evidence.txt' 2>/dev/null | wc -l | tr -d '[:space:]')"

if [[ "${control_failover_count}" == '1' && "${lb_failover_count}" == '1' ]]; then
  pass 'two failover consumers are independently identified'
else
  fail "failover evidence count mismatch: control=${control_failover_count}, lb=${lb_failover_count}"
fi

if grep -RIEq --include='*.txt' 'secret[[:space:]]+"[^"[:space:]]+"' "${run_root}"; then
  fail 'possible TSIG secret pattern detected'
else
  pass 'no TSIG secret pattern detected'
fi

if (( failures == 0 )); then
  echo 'RESULT: PASS'
  exit 0
fi

printf 'RESULT: FAIL (%s issue(s))\n' "${failures}" >&2
exit 1


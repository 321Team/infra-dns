#!/usr/bin/env bash
set -euo pipefail

zip_file="${1:-}"
sidecar_file="${2:-${zip_file}.sha256}"

if [[ -z "${zip_file}" || ! -f "${zip_file}" || ! -f "${sidecar_file}" ]]; then
  printf 'Usage: %s <R2.zip> [R2.zip.sha256]\n' "$0" >&2
  exit 64
fi

expected_hash="$(awk 'NF >= 1 { print $1; exit }' "${sidecar_file}")"
actual_hash="$(sha256sum "${zip_file}" | awk '{print $1}')"

printf 'Expected ZIP SHA-256: %s\n' "${expected_hash}"
printf 'Actual ZIP SHA-256:   %s\n' "${actual_hash}"

if [[ ! "${expected_hash}" =~ ^[0-9a-fA-F]{64}$ || "${actual_hash}" != "${expected_hash}" ]]; then
  echo 'FAIL: ZIP SHA-256 mismatch' >&2
  exit 74
fi

echo 'PASS: ZIP SHA-256'
unzip -t "${zip_file}"

if zipinfo -1 "${zip_file}" \
  | awk 'BEGIN{bad=0} /^\//{bad=1} /(^|\/)\.\.($|\/)/{bad=1} END{exit !bad}'; then
  echo 'FAIL: unsafe ZIP path detected' >&2
  exit 78
fi

required_names=(
  '/EVIDENCE_INDEX.md'
  '/SHA256SUMS'
  '_dns_record_inventory_evidence.txt'
  '_dns02_fresh_tsig_evidence.txt'
)

inventory="$(zipinfo -1 "${zip_file}")"
for required_name in "${required_names[@]}"; do
  if ! printf '%s\n' "${inventory}" | grep -Fq "${required_name}"; then
    printf 'FAIL: required ZIP member missing: %s\n' "${required_name}" >&2
    exit 66
  fi
done

echo 'PASS: required R2 package members are present'


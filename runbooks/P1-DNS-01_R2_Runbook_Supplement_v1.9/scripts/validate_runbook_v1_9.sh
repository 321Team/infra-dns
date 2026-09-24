#!/usr/bin/env bash

set -uo pipefail

kit_root="${1:-/home/server01_ansible/p1-dns-01-r2/kit/P1-DNS-01_R2_Runbook_Supplement_v1.9}"
runbook="${kit_root}/P1-DNS-01_R2_SAFE_RUNBOOK_v1.9.md"
canonical_validator="${kit_root}/scripts/validate_canonical_r2_v1_9.sh"
self_validator="${kit_root}/scripts/validate_runbook_v1_9.sh"
failures=0

pass() {
  printf 'PASS: %s\n' "$1"
}

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  failures=$((failures + 1))
}

for required_file in "${runbook}" "${canonical_validator}" "${self_validator}"
do
  if [[ -s "${required_file}" ]]; then
    pass "required file exists: ${required_file}"
  else
    fail "required file missing: ${required_file}"
  fi
done

if [[ ! -s "${runbook}" || ! -s "${canonical_validator}" || ! -s "${self_validator}" ]]; then
  printf 'RESULT: FAIL (%s issue(s))\n' "${failures}" >&2
  exit 1
fi

for script_path in "${canonical_validator}" "${self_validator}"
do
  if bash -n "${script_path}"; then
    pass "script syntax: ${script_path}"
  else
    fail "script syntax: ${script_path}"
  fi
done

if awk '
  /FORBIDDEN-INTERACTIVE-EXAMPLE-START/ { skip = 1; next }
  /FORBIDDEN-INTERACTIVE-EXAMPLE-END/   { skip = 0; next }
  !skip { print }
' "${runbook}" \
  | grep -E '\|\|[[:space:]]+exit([[:space:]]|$)' >/dev/null
then
  fail 'interactive || exit pattern detected outside fenced example context'
else
  pass 'no active interactive || exit pattern'
fi

if grep -Fq '<!-- FORBIDDEN-INTERACTIVE-EXAMPLE-START -->' "${runbook}" \
  && grep -Fq '<!-- FORBIDDEN-INTERACTIVE-EXAMPLE-END -->' "${runbook}"
then
  pass 'forbidden interactive example is explicitly delimited'
else
  fail 'forbidden interactive example delimiters are missing'
fi

for required_text in \
  'ansible01' \
  'server01_ansible' \
  '/home/server01_ansible/p1-dns-01-r2' \
  'Subshell' \
  'Sidecar return code' \
  'sha256sum "${zip_name}" > "${sidecar_name}"' \
  'test "${sidecar_target}" = "${zip_name}"'
do
  if grep -Fq "${required_text}" "${runbook}"; then
    pass "runbook rule: ${required_text}"
  else
    fail "runbook rule missing: ${required_text}"
  fi
done

if grep -Fq 'sha256sum "/home/server01_ansible/p1-dns-01-r2/work/P1-DNS-01-FRESH-20260902-R2.zip"' "${runbook}"; then
  pass 'forbidden absolute-sidecar example is documented'
else
  fail 'forbidden absolute-sidecar example is missing'
fi

if (( failures == 0 )); then
  echo 'RESULT: PASS'
  exit 0
fi

printf 'RESULT: FAIL (%s issue(s))\n' "${failures}" >&2
exit 1

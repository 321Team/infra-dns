#!/usr/bin/env bash
set -uo pipefail
umask 027

if [[ $# -ne 2 || "${1:-}" != "--approved" || -z "${2:-}" ]]; then
  printf 'ERROR: Fresh TSIG retransfer requires an approved work window.\n' >&2
  printf 'Usage: %s --approved <evidence-root>\n' "$0" >&2
  exit 64
fi

evidence_root="$2"
output_dir="${evidence_root}/tsig"
stamp="$(date +%Y%m%dT%H%M%S%z)"
output_file="${output_dir}/${stamp}_dns02_fresh_tsig_evidence.txt"

if ! mkdir -p "${output_dir}"; then
  printf 'ERROR: cannot create Evidence directory: %s\n' "${output_dir}" >&2
  exit 73
fi

if [[ ! -d "${output_dir}" || ! -w "${output_dir}" ]]; then
  printf 'ERROR: Evidence directory is not writable: %s\n' "${output_dir}" >&2
  exit 73
fi

if ! sudo -v; then
  printf 'ERROR: sudo validation failed before collection.\n' >&2
  exit 77
fi

temporary_file="$(mktemp "${output_dir}/.${stamp}_dns02_fresh_tsig.tmp.XXXXXX")" || exit 73
trap 'rm -f "${temporary_file}"' EXIT

section() {
  printf '\n===== %s =====\n' "$1"
}

{
  validation_status=0

  section "EVIDENCE METADATA"
  printf 'Ticket: P1-DNS-01\n'
  printf 'Test ID: DNS-PT-04, DNS-EV-02\n'
  printf 'Role: dns02 Fresh TSIG Zone Transfer\n'
  printf 'Change authorization flag: --approved\n'
  printf 'Sensitive data: TSIG secret, key hash, authenticated AXFR MAC are EXCLUDED\n'
  date --iso-8601=seconds
  hostnamectl --static
  id

  section "PRECONDITION"
  pre_status="$(sudo rndc zonestatus fds.internal 2>&1)"
  printf '%s\n' "${pre_status}"
  pre_serial="$(printf '%s\n' "${pre_status}" | awk '$1 == "serial:" { print $2; exit }')"

  if ! printf '%s\n' "${pre_status}" | grep -Fq 'type: secondary'; then
    echo 'FAIL: fds.internal is not loaded as a secondary zone on this host'
    validation_status=1
  fi

  if [[ -z "${pre_serial}" ]]; then
    echo 'FAIL: pre-transfer serial was not detected'
    validation_status=1
  else
    printf 'PASS: pre-transfer serial %s\n' "${pre_serial}"
  fi

  section "FRESH RETRANSFER"
  transfer_start="$(date --iso-8601=seconds)"
  printf 'Transfer start: %s\n' "${transfer_start}"

  if sudo rndc retransfer fds.internal; then
    echo 'PASS: rndc retransfer command accepted'
  else
    echo 'FAIL: rndc retransfer command failed'
    validation_status=1
  fi

  transfer_log=''
  for attempt in 1 2 3 4 5 6 7 8 9 10; do
    transfer_log="$(sudo journalctl -u named \
      --since "${transfer_start}" --no-pager -o short-iso-precise \
      | grep -E 'fds\.internal|connected using .*TSIG|transferred serial|Transfer status: success|Transfer completed|BADKEY|BADSIG' \
      || true)"

    if printf '%s\n' "${transfer_log}" | grep -Eq 'Transfer status: success|Transfer completed'; then
      break
    fi
    sleep 1
  done

  section "TIMESTAMPED TRANSFER LOG"
  printf '%s\n' "${transfer_log}"

  if printf '%s\n' "${transfer_log}" \
      | grep -Eq 'connected using .*TSIG fds-transfer-key|TSIG .fds-transfer-key.' \
    && printf '%s\n' "${transfer_log}" \
      | grep -Eq 'Transfer status: success|Transfer completed' \
    && [[ -n "${pre_serial}" ]] \
    && printf '%s\n' "${transfer_log}" \
      | grep -Eq "transferred serial ${pre_serial}|serial ${pre_serial}"; then
    printf 'PASS: fresh TSIG-authenticated transfer of serial %s observed\n' "${pre_serial}"
  else
    echo 'FAIL: fresh timestamped TSIG transfer success was not fully observed'
    validation_status=1
  fi

  if printf '%s\n' "${transfer_log}" | grep -Eq 'BADKEY|BADSIG'; then
    echo 'FAIL: BADKEY/BADSIG occurred in the fresh transfer window'
    validation_status=1
  else
    echo 'PASS: no BADKEY/BADSIG occurred in the fresh transfer window'
  fi

  section "POSTCONDITION"
  post_status="$(sudo rndc zonestatus fds.internal 2>&1)"
  printf '%s\n' "${post_status}"
  post_serial="$(printf '%s\n' "${post_status}" | awk '$1 == "serial:" { print $2; exit }')"

  if [[ -n "${pre_serial}" && "${post_serial}" == "${pre_serial}" ]] \
    && printf '%s\n' "${post_status}" | grep -Fq 'type: secondary'; then
    printf 'PASS: secondary post-transfer serial remains %s\n' "${post_serial}"
  else
    printf 'FAIL: secondary postcondition mismatch (pre=%s, post=%s)\n' \
      "${pre_serial:-missing}" "${post_serial:-missing}"
    validation_status=1
  fi

  section "COLLECTOR RESULT"
  if (( validation_status == 0 )); then
    echo 'PASS: fresh timestamped TSIG zone transfer was observed'
  else
    echo 'FAIL: fresh TSIG zone transfer evidence is incomplete or failed'
  fi

  exit "${validation_status}"
} 2>&1 | tee "${temporary_file}"

pipeline_status=("${PIPESTATUS[@]}")
collector_status="${pipeline_status[0]}"
tee_status="${pipeline_status[1]}"

if (( tee_status != 0 )); then
  printf 'ERROR: tee failed while writing Evidence: %s\n' "${temporary_file}" >&2
  exit "${tee_status}"
fi

mv "${temporary_file}" "${output_file}"
chmod 0640 "${output_file}"
trap - EXIT

output_name="$(basename "${output_file}")"
(
  cd "${output_dir}"
  sha256sum "${output_name}" > "${output_name}.sha256"
  chmod 0640 "${output_name}.sha256"
  sha256sum --check "${output_name}.sha256"
) || exit 74

printf 'Evidence: %s\nHash: %s\n' "${output_file}" "${output_file}.sha256"
exit "${collector_status}"

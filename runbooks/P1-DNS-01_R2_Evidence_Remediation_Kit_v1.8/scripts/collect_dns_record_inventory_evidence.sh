#!/usr/bin/env bash
set -uo pipefail
umask 027

if [[ $# -ne 1 || -z "${1:-}" ]]; then
  printf 'Usage: %s <host-local-output-root>\n' "$0" >&2
  exit 64
fi

evidence_root="$1"
output_dir="${evidence_root}/inventory"
stamp="$(date +%Y%m%dT%H%M%S%z)"
output_file="${output_dir}/${stamp}_dns_record_inventory_evidence.txt"

if ! mkdir -p "${output_dir}"; then
  printf 'ERROR: cannot create Evidence directory: %s\n' "${output_dir}" >&2
  exit 73
fi

if [[ ! -d "${output_dir}" || ! -w "${output_dir}" ]]; then
  printf 'ERROR: Evidence directory is not writable: %s\n' "${output_dir}" >&2
  exit 73
fi

temporary_file="$(mktemp "${output_dir}/.${stamp}_dns_record_inventory.tmp.XXXXXX")" || exit 73
trap 'rm -f "${temporary_file}"' EXIT

servers=(10.1.93.52 10.1.93.53)
names=(
  dns01 dns02 edge vpn-gw harbor db
  control01 control02 control03
  worker01 worker02 worker03 k8s-api
)
expected_ips=(
  10.1.93.52 10.1.93.53 10.1.93.50 10.1.93.51 10.1.93.54 10.1.93.55
  10.1.93.102 10.1.93.103 10.1.93.104
  10.1.93.105 10.1.93.107 10.1.93.108 10.1.93.109
)

section() {
  printf '\n===== %s =====\n' "$1"
}

{
  validation_status=0
  total_pass=0

  section "EVIDENCE METADATA"
  printf 'Ticket: P1-DNS-01\n'
  printf 'Test ID: DNS-PT-01, DNS-PT-02, DNS-EV-01, DNS-EV-02\n'
  printf 'Role: Approved A Record Inventory Validator\n'
  printf 'Safety: read-only DNS queries; no configuration change\n'
  date --iso-8601=seconds
  hostnamectl --static
  id
  ip -br addr

  for server in "${servers[@]}"; do
    section "APPROVED RECORDS VIA ${server}"
    server_pass=0

    for index in "${!names[@]}"; do
      fqdn="${names[$index]}.fds.internal"
      expected_ip="${expected_ips[$index]}"
      query_output="$(dig "@${server}" "${fqdn}" A \
        +norecurse +nocookie +time=3 +tries=1 \
        +noall +comments +answer 2>&1)"

      printf 'CHECK: %s -> %s via %s\n' "${fqdn}" "${expected_ip}" "${server}"
      printf '%s\n' "${query_output}"

      if printf '%s\n' "${query_output}" | grep -Fq 'status: NOERROR' \
        && printf '%s\n' "${query_output}" | grep -Eq '^;; flags:.*[[:space:]]aa([[:space:];]|$)' \
        && printf '%s\n' "${query_output}" \
          | awk -v q="${fqdn}." -v ip="${expected_ip}" \
              '$1 == q && $4 == "A" && $5 == ip { found=1 } END { exit !found }'; then
        printf 'PASS: %s returned authoritative A %s\n' "${fqdn}" "${expected_ip}"
        server_pass=$((server_pass + 1))
        total_pass=$((total_pass + 1))
      else
        printf 'FAIL: %s expected authoritative A %s via %s\n' \
          "${fqdn}" "${expected_ip}" "${server}"
        validation_status=1
      fi
    done

    printf 'SERVER SUMMARY: %s passed %d/13 records\n' "${server}" "${server_pass}"
    if (( server_pass != 13 )); then
      validation_status=1
    fi
  done

  section "COLLECTOR RESULT"
  printf 'TOTAL: %d/26 approved authoritative answers\n' "${total_pass}"
  if (( validation_status == 0 && total_pass == 26 )); then
    echo 'PASS: all 13 approved A records matched on dns01 and dns02'
  else
    echo 'FAIL: one or more approved A records did not match'
    validation_status=1
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

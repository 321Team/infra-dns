#!/usr/bin/env python3
"""Offline drift check between the repository zone and collected server copies.

Reads only local files: the repository zone and the output folders produced by
tools/collect_dns_zone_readonly.py on dns01 and dns02. It never connects to a
server and never writes outside the optional --report path.

Checks
  1. each collected folder is COMPLETE_COLLECTION_ONLY and its SHA256SUMS verify
  2. dns01 disk source bytes == repository zones/fds.internal.zone bytes
  3. dns01 and dns02 normalized zones (named-checkzone -D output) are identical
  4. SOA serial is the same in the repository, both normalized zones and both
     runtime zonestatus observations (before/after)

Exit codes: 0 no drift, 2 drift found, 1 invalid or incomplete input.
The result is a pre-check observation. It is not a deployment input, an AC
PASS or a runtime approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ZONE_NAME = 'fds.internal'


class InputError(Exception):
    pass


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def repo_serial(text):
    """SOA serial from a text zone: first number after 'SOA <mname> <rname> ('."""
    m = re.search(r'\bSOA\s+\S+\s+\S+\s*\(?\s*(\d+)', text)
    if not m:
        raise InputError('repository zone has no parsable SOA serial')
    return m.group(1)


def normalized_serial(text):
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 7 and parts[0] == ZONE_NAME + '.' and 'SOA' in parts:
            i = parts.index('SOA')
            if len(parts) > i + 3 and parts[i + 3].isdigit():
                return parts[i + 3]
    raise InputError('normalized zone has no SOA record')


def zonestatus_serial(text):
    m = re.search(r'^serial:\s*(\d+)\s*$', text, re.M)
    if not m:
        raise InputError('zonestatus has no serial')
    return m.group(1)


def load_host(folder, expected_host):
    folder = Path(folder)
    if not folder.is_dir():
        raise InputError(f'{expected_host}: folder not found')
    sums = folder / 'SHA256SUMS'
    if not sums.is_file():
        raise InputError(f'{expected_host}: SHA256SUMS missing')
    for line in sums.read_text(encoding='utf-8').splitlines():
        m = re.fullmatch(r'([0-9a-f]{64})  (.+)', line.rstrip('\r'))
        if not m:
            raise InputError(f'{expected_host}: malformed SHA256SUMS line')
        name = m.group(2)
        if '/' in name or '\\' in name or name in ('.', '..'):
            raise InputError(f'{expected_host}: unsafe name in SHA256SUMS')
        target = folder / name
        if not target.is_file() or sha256(target.read_bytes()) != m.group(1):
            raise InputError(f'{expected_host}: {name} does not match SHA256SUMS')
    status = json.loads((folder / 'STATUS.json').read_text(encoding='utf-8'))
    if status.get('status') != 'COMPLETE_COLLECTION_ONLY':
        raise InputError(f'{expected_host}: collection is not complete ({status.get("status")})')
    session = json.loads((folder / 'SESSION.json').read_text(encoding='utf-8'))
    if session.get('host') != expected_host:
        raise InputError(f'{expected_host}: SESSION host is {session.get("host")!r}')
    need = ['fds.internal.source', 'fds.internal.normalized.zone', 'zonestatus-before.txt', 'zonestatus-after.txt']
    missing = [n for n in need if not (folder / n).is_file()]
    if missing:
        raise InputError(f'{expected_host}: missing {", ".join(missing)}')
    normalized = (folder / 'fds.internal.normalized.zone').read_text(encoding='utf-8')
    return {
        'host': expected_host,
        'collected_at_kst': status.get('finished_at_kst'),
        'collector_sha256': session.get('collector_sha256'),
        'source_sha256': sha256((folder / 'fds.internal.source').read_bytes()),
        'source_bytes': (folder / 'fds.internal.source').read_bytes(),
        'normalized_sha256': sha256(normalized.encode('utf-8')),
        'normalized_serial': normalized_serial(normalized),
        'runtime_serial_before': zonestatus_serial((folder / 'zonestatus-before.txt').read_text(encoding='utf-8')),
        'runtime_serial_after': zonestatus_serial((folder / 'zonestatus-after.txt').read_text(encoding='utf-8')),
    }


def compare(repo_zone, dns01_dir, dns02_dir):
    repo_bytes = Path(repo_zone).read_bytes()
    repo = {'sha256': sha256(repo_bytes), 'serial': repo_serial(repo_bytes.decode('utf-8'))}
    d1 = load_host(dns01_dir, 'dns01')
    d2 = load_host(dns02_dir, 'dns02')
    findings = []
    if d1['source_bytes'] != repo_bytes:
        findings.append('dns01 disk source differs from repository zone')
    if d1['normalized_sha256'] != d2['normalized_sha256']:
        findings.append('dns01 and dns02 normalized zones differ')
    serials = {
        'repository': repo['serial'],
        'dns01_normalized': d1['normalized_serial'],
        'dns02_normalized': d2['normalized_serial'],
        'dns01_runtime_before': d1['runtime_serial_before'],
        'dns01_runtime_after': d1['runtime_serial_after'],
        'dns02_runtime_before': d2['runtime_serial_before'],
        'dns02_runtime_after': d2['runtime_serial_after'],
    }
    if len(set(serials.values())) != 1:
        findings.append('SOA serial differs: ' + ', '.join(f'{k}={v}' for k, v in serials.items()))
    hosts = {}
    for d in (d1, d2):
        hosts[d['host']] = {k: v for k, v in d.items() if k not in ('host', 'source_bytes')}
    return {
        'result': 'DRIFT' if findings else 'NO_DRIFT',
        'findings': findings,
        'repository': repo,
        'hosts': hosts,
        'serials': serials,
        'scope': 'offline comparison of collected files; not a deployment input, AC PASS or runtime approval',
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--repo-zone', default=str(Path(__file__).resolve().parents[1] / 'zones' / 'fds.internal.zone'))
    p.add_argument('--dns01', required=True, help='dns01 output folder of collect_dns_zone_readonly.py')
    p.add_argument('--dns02', required=True, help='dns02 output folder of collect_dns_zone_readonly.py')
    p.add_argument('--report', help='write the JSON report to this path')
    a = p.parse_args(argv)
    try:
        report = compare(a.repo_zone, a.dns01, a.dns02)
    except (InputError, OSError, ValueError, UnicodeError) as exc:
        print(f'INVALID_INPUT: {exc}')
        return 1
    text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if a.report:
        Path(a.report).write_text(text, encoding='utf-8', newline='\n')
    print(report['result'])
    for f in report['findings']:
        print('  - ' + f)
    return 0 if report['result'] == 'NO_DRIFT' else 2


if __name__ == '__main__':
    sys.exit(main())

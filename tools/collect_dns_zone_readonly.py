#!/usr/bin/env python3
"""Bounded console intake, pinned to the masked 2026-09-18 configuration.

Run as the existing non-root administrator after sudo -v. No service writes.
Raw process arguments and command stderr are never persisted or printed.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import tempfile

EXPECTED = {
    'dns01': ('3a269aa35800afee638fcc9a6768cfdd21ab81a6b6a5c1945f6b8391bec3345d', '/var/named/fds.internal.zone'),
    'dns02': ('ea12325ab17893b25c112914432f045fd574af2a9704d12601a41486fa058f48', '/var/named/slaves/fds.internal.zone'),
}


class Stop(Exception):
    pass


def safe_content(data, zone=False):
    text = data.decode('latin1')
    if re.search(r'-----BEGIN (?:\w+ )*PRIVATE KEY-----|(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}', text):
        raise Stop('sensitive content detected; value suppressed')
    if any(not re.fullmatch(r'\?+', v) for v in re.findall(r'\bsecret\s+"([^"]*)"', text, re.I)):
        raise Stop('unmasked shared secret detected; value suppressed')
    if zone and re.search(r'\$INCLUDE\b', text, re.I):
        raise Stop('zone INCLUDE requires separate path review')


def process_config(data):
    args = data.rstrip(b'\0').split(b'\0')
    if not args or args[0] != b'/usr/sbin/named':
        raise Stop('unexpected named executable argument')
    # Only the explicit standard config, without chroot, is authorized here.
    if any(a.startswith(b'-t') for a in args[1:]):
        raise Stop('chroot option requires separate path review')
    if args.count(b'-c') != 1:
        raise Stop('explicit -c /etc/named.conf required')
    index = args.index(b'-c')
    if index + 1 >= len(args) or args[index + 1] != b'/etc/named.conf':
        raise Stop('nonstandard configuration path requires review')
    if any(a.startswith(b'-c') and a != b'-c' for a in args[1:]):
        raise Stop('ambiguous configuration option')
    return '/etc/named.conf'


def zone_status(data, source):
    fields = dict(line.split(':', 1) for line in data.decode('utf-8').splitlines() if ':' in line)
    if fields.get('dynamic', '').strip() != 'no':
        raise Stop('dynamic zone requires separate collection procedure')
    if fields.get('files', '').strip() != source[len('/var/named/'):]:
        raise Stop('loaded zone file differs from intake path')
    serial = fields.get('serial', '').strip()
    if not serial.isdigit():
        raise Stop('missing zone serial')
    return serial


def now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()


def main():
    os.umask(0o077)
    host = socket.gethostname().split('.')[0]
    if host not in EXPECTED or os.geteuid() == 0:
        print('STOP: use the existing non-root administrator on dns01 or dns02')
        return 1
    out = Path(tempfile.mkdtemp(prefix='dns-zone-intake.' + host + '.', dir=str(Path.home())))
    commands = []

    def run(label, argv, allowed=(0,)):
        item = {'label': label, 'command': argv, 'started_at_kst': now(), 'stderr': 'suppressed; may contain sensitive diagnostics'}
        commands.append(item)
        try:
            result = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,
                                    env=dict(os.environ, LC_ALL='C'))
        except (OSError, subprocess.TimeoutExpired):
            item.update({'finished_at_kst': now(), 'exit_code': None})
            raise Stop(label + ': unavailable or timed out')
        item.update({'finished_at_kst': now(), 'exit_code': result.returncode})
        if result.returncode not in allowed:
            raise Stop(label + ': nonzero exit; diagnostics suppressed')
        return result

    def save(name, data, zone=False):
        safe_content(data, zone)
        (out / name).write_bytes(data)

    def query(label, argv):
        data = run(label, argv).stdout
        save(label + '.txt', data)
        return data

    try:
        cfg_hash, source = EXPECTED[host]
        session = {'host': host, 'started_at_kst': now(), 'uid': os.getuid(), 'zone_source_path': source,
                   'collector_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   'scope': 'read-only disk source and partial runtime observations; no DNS AC test'}
        (out / 'SESSION.json').write_text(json.dumps(session, indent=2) + '\n', encoding='utf-8')
        pid_cmd = ['systemctl', 'show', 'named', '--property=MainPID', '--value']
        pid = query('named-mainpid-before', pid_cmd).strip().decode('ascii')
        if not pid.isdigit() or int(pid) <= 0:
            raise Stop('named is not running')
        proc = '/proc/' + pid
        if query('named-executable', ['sudo', '-n', 'readlink', '-e', proc + '/exe']).strip() != b'/usr/sbin/named':
            raise Stop('unexpected process executable')
        if query('named-root', ['sudo', '-n', 'readlink', '-e', proc + '/root']).strip() != b'/':
            raise Stop('process root requires separate path review')
        args = run('process-arguments-read-in-memory', ['sudo', '-n', 'cat', proc + '/cmdline']).stdout
        config = process_config(args)
        save('effective-config-path.txt', (config + '\n').encode())
        cfg = run('masked-config', ['sudo', '-n', 'named-checkconf', '-p', '-x', config]).stdout
        safe_content(cfg)
        if hashlib.sha256(cfg).hexdigest() != cfg_hash:
            raise Stop('masked disk configuration changed since first intake')
        save('named.expanded.sanitized.conf', cfg)
        before = query('zonestatus-before', ['sudo', '-n', 'rndc', 'zonestatus', 'fds.internal'])
        serial = zone_status(before, source)
        if query('zone-resolved-path', ['sudo', '-n', 'readlink', '-e', source]).strip().decode() != source:
            raise Stop('zone symlink or nonstandard resolved path')
        journal = run('journal-presence', ['sudo', '-n', 'sh', '-c',
                      'if [ -e "$1" ] || [ -L "$1" ]; then printf "present\\n"; else printf "absent\\n"; fi',
                      'sh', source + '.jnl']).stdout.strip()
        if journal != b'absent':
            raise Stop('zone journal present; do not claim complete disk snapshot')
        stat_cmd = ['sudo', '-n', 'stat', '-Lc', '%F|%d|%i|%s|%y|%z', source]
        stat_before = query('zone-stat-before', stat_cmd)
        fields = stat_before.decode().split('|')
        if fields[0] != 'regular file' or not (0 < int(fields[3]) <= 4 * 1024 * 1024):
            raise Stop('unexpected zone type or size')
        original = run('zone-file-read', ['sudo', '-n', 'cat', source]).stdout
        if len(original) != int(fields[3]):
            raise Stop('zone size changed while reading')
        save('fds.internal.source', original, zone=True)
        query('named-version', ['named', '-v'])
        query('checkzone-version', ['named-checkzone', '-v'])
        # Run unprivileged against the local snapshot; no original file writes.
        for fmt in ('text', 'raw'):
            result = run('checkzone-' + fmt, ['named-checkzone', '-q', '-D', '-f', fmt, '-F', 'text', '-o', '-',
                                             'fds.internal', str(out / 'fds.internal.source')], allowed=(0, 1))
            if result.returncode == 0 and result.stdout.strip():
                save('fds.internal.normalized.zone', result.stdout, zone=True)
                save('zone-source-format.txt', (fmt + '\n').encode())
                break
        else:
            raise Stop('zone failed both text and raw format validation')
        if query('zone-stat-after', stat_cmd) != stat_before:
            raise Stop('zone changed during intake')
        after = query('zonestatus-after', ['sudo', '-n', 'rndc', 'zonestatus', 'fds.internal'])
        if zone_status(after, source) != serial:
            raise Stop('runtime serial changed during intake')
        for state in ('runtime', 'permanent'):
            flags = ['--permanent'] if state == 'permanent' else []
            query('firewall-zones-' + state, ['sudo', '-n', 'firewall-cmd'] + flags + ['--list-all-zones'])
            query('dns-ipset-' + state, ['sudo', '-n', 'firewall-cmd'] + flags + ['--ipset=fds-dns-clients', '--get-entries'])
        if query('named-mainpid-after', pid_cmd).strip().decode() != pid:
            raise Stop('named process changed during intake')
        if run('process-arguments-recheck-in-memory', ['sudo', '-n', 'cat', proc + '/cmdline']).stdout != args:
            raise Stop('named arguments changed during intake')
        status = {'status': 'COMPLETE_COLLECTION_ONLY', 'finished_at_kst': now(), 'runtime_serial_observed': serial,
                  'claims_excluded': ['AC PASS', 'all in-memory config matches disk', 'effective firewall traffic test', 'independent review']}
        rc = 0
    except (Stop, ValueError, UnicodeError) as exc:
        # All Stop messages above are constants or internal command labels.
        status = {'status': 'INCOMPLETE_DO_NOT_SUBMIT_AS_COMPLETE', 'finished_at_kst': now(),
                  'reason': str(exc) if isinstance(exc, Stop) else 'unexpected output format; value suppressed'}
        rc = 1
    finally:
        (out / 'COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n', encoding='utf-8')
    (out / 'STATUS.json').write_text(json.dumps(status, indent=2) + '\n', encoding='utf-8')
    lines = [hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name for p in sorted(out.iterdir()) if p.is_file()]
    (out / 'SHA256SUMS').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(status['status'])
    print('COLLECTED_DIRECTORY=' + str(out))
    if rc:
        print(status['reason'])
    return rc


if __name__ == '__main__':
    raise SystemExit(main())

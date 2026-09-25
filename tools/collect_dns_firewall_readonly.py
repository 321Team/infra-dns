#!/usr/bin/env python3
"""Read-only firewall/NetworkManager intake for the DNS hosts (#7).

Run on dns01 or dns02 as the existing non-root administrator after `sudo -v`.
Collects, without changing anything:
  - firewalld state, default/active zones, all zones (runtime/permanent)
  - `dns` service definition (runtime/permanent)
  - fds-dns-clients ipset definition and entries (runtime/permanent)
  - policies and direct rules (runtime/permanent)
  - NetworkManager zone/autoconnect of the active connection on the DNS interface
  - kernel nftables ruleset (`nft list ruleset`)
and writes summary.json with the comparisons below. No reload, no --add/--remove,
no NM change, no packet test. Every command is checked against an allow-list and
any write-like option is refused before execution.

summary.json checks (observations, not an AC verdict):
  default_zone_is_public, dns_service_ports (expect 53/tcp and 53/udp),
  ipset_runtime_equals_permanent, dns_rich_rule_runtime/permanent,
  interface_in_runtime_zone, nm_connection_zone (empty means the default zone),
  nm_autoconnect, policies/direct rule presence
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

HOSTS = ('dns01', 'dns02')
IFACE = 'ens160'
IPSET = 'fds-dns-clients'
RICH_RULE = 'rule family="ipv4" source ipset="fds-dns-clients" service name="dns" accept'
MAX_OUTPUT = 4 * 1024 * 1024
WRITE_LIKE = re.compile(r'^--(add|remove|reload|complete-reload|set|new|delete|load|runtime-to-permanent|'
                        r'change|query-|panic|lockdown|reset|check-config)|^(up|down|modify|delete|add|reload|flush|'
                        r'destroy|insert|replace|create|import)$')
READ_COMMANDS = {'firewall-cmd', 'nmcli', 'nft', 'systemctl'}


class Stop(Exception):
    pass


def now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()


def check_read_only(argv):
    cmd = argv[2:] if argv[:2] == ['sudo', '-n'] else argv
    if not cmd or cmd[0] not in READ_COMMANDS:
        raise Stop('command outside the read-only allow-list')
    if cmd[0] == 'systemctl' and cmd[1] not in ('is-active', 'is-enabled'):
        raise Stop('systemctl verb outside the read-only allow-list')
    if cmd[0] == 'nft' and cmd[1:] != ['list', 'ruleset']:
        raise Stop('nft usage outside the read-only allow-list')
    if cmd[0] == 'nmcli' and not (('-g' in cmd or '-t' in cmd) and 'show' in cmd):
        raise Stop('nmcli usage outside the read-only allow-list')
    for a in cmd[1:]:
        if WRITE_LIKE.search(a):
            raise Stop('write-like option refused')


def execute(argv):
    """Run one allow-listed read-only command. The guard runs before anything is executed."""
    check_read_only(argv)
    return subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60,
                          env=dict(os.environ, LC_ALL='C'))


def zone_block(text, zone):
    m = re.search(r'(?ms)^' + re.escape(zone) + r'\b[^\n]*\n(.*?)(?=^\S|\Z)', text)
    return m.group(1) if m else ''


def field(block, name):
    m = re.search(r'(?m)^\s*' + re.escape(name) + r':[ \t]*(.*)$', block)
    return m.group(1).strip() if m else None


def rich_rules(block):
    m = re.search(r'(?ms)^\s*rich rules:[ \t]*\n(.*)', block)
    return [l.strip() for l in (m.group(1) if m else '').splitlines() if l.strip()]


def summarize(o):
    rt_public = zone_block(o['zones-runtime'], 'public')
    pm_public = zone_block(o['zones-permanent'], 'public')
    ports_rt = sorted((field(o['dns-service-runtime'], 'ports') or '').split())
    ports_pm = sorted((field(o['dns-service-permanent'], 'ports') or '').split())
    set_rt = sorted(o['ipset-entries-runtime'].split())
    set_pm = sorted(o['ipset-entries-permanent'].split())
    active = [l for l in o['nm-active'].splitlines() if l.endswith(':' + IFACE)]
    nm_line = (o.get('nm-connection', '').splitlines() or [''])[0]
    nm_zone = [v.replace('\\:', ':') for v in re.split(r'(?<!\\):', nm_line)]  # terse: fields joined by ':'
    return {
        'firewalld_active': o['firewalld-active'].strip() == 'active',
        'firewalld_enabled': o['firewalld-enabled'].strip() == 'enabled',
        'default_zone': o['default-zone'].strip(),
        'default_zone_is_public': o['default-zone'].strip() == 'public',
        'active_zones': o['active-zones'].strip().splitlines(),
        'interface_in_runtime_public': IFACE in (field(rt_public, 'interfaces') or '').split(),
        'interface_in_permanent_public': IFACE in (field(pm_public, 'interfaces') or '').split(),
        'dns_service_ports_runtime': ports_rt,
        'dns_service_ports_permanent': ports_pm,
        'dns_service_ports_expected': ports_rt == ports_pm == ['53/tcp', '53/udp'],
        'dns_rich_rule_runtime': RICH_RULE in rich_rules(rt_public),
        'dns_rich_rule_permanent': RICH_RULE in rich_rules(pm_public),
        'public_services_runtime': (field(rt_public, 'services') or '').split(),
        'public_services_permanent': (field(pm_public, 'services') or '').split(),
        'dns_service_directly_in_public': 'dns' in (field(rt_public, 'services') or '').split()
        or 'dns' in (field(pm_public, 'services') or '').split(),
        'ipset_entries_runtime': len(set_rt),
        'ipset_entries_permanent': len(set_pm),
        'ipset_runtime_equals_permanent': set_rt == set_pm,
        'nm_active_connection_on_interface': len(active) == 1,
        'nm_connection_zone': nm_zone[0] if nm_zone else None,
        'nm_connection_zone_note': 'empty means the connection follows the firewalld default zone',
        'nm_autoconnect': nm_zone[1] if len(nm_zone) > 1 else None,
        'policies_runtime_present': bool(o['policies-runtime'].strip()),
        'policies_permanent_present': bool(o['policies-permanent'].strip()),
        'direct_rules_runtime': [l for l in o['direct-runtime'].splitlines() if l.strip()],
        'direct_rules_permanent': [l for l in o['direct-permanent'].splitlines() if l.strip()],
        'nft_ruleset_bytes': len(o['nft-ruleset'].encode()),
        'scope': 'read-only observation; not a packet test, reboot test or AC verdict',
    }


def main():
    os.umask(0o077)
    host = socket.gethostname().split('.')[0]
    if host not in HOSTS or os.geteuid() == 0:
        print('STOP: use the existing non-root administrator on dns01 or dns02')
        return 1
    out = Path(tempfile.mkdtemp(prefix='dns-firewall.' + host + '.', dir=str(Path.home())))
    commands, outputs = [], {}

    def run(label, argv):
        item = {'label': label, 'command': argv, 'started_at_kst': now(),
                'stderr': 'suppressed; may contain sensitive diagnostics'}
        commands.append(item)
        try:
            r = execute(argv)
        except (OSError, subprocess.TimeoutExpired):
            item.update({'finished_at_kst': now(), 'exit_code': None})
            raise Stop(label + ': unavailable or timed out')
        item.update({'finished_at_kst': now(), 'exit_code': r.returncode})
        if r.returncode != 0:
            raise Stop(label + ': nonzero exit; diagnostics suppressed')
        if len(r.stdout) > MAX_OUTPUT:
            raise Stop(label + ': output larger than limit')
        text = r.stdout.decode('utf-8')
        (out / (label + '.txt')).write_text(text, encoding='utf-8', newline='\n')
        outputs[label] = text
        return text

    fc = ['sudo', '-n', 'firewall-cmd']
    try:
        session = {'host': host, 'started_at_kst': now(), 'uid': os.getuid(),
                   'collector_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   'scope': 'read-only firewall and NetworkManager observation; no packet test'}
        (out / 'SESSION.json').write_text(json.dumps(session, indent=2) + '\n', encoding='utf-8')
        run('firewalld-active', ['systemctl', 'is-active', 'firewalld'])
        run('firewalld-enabled', ['systemctl', 'is-enabled', 'firewalld'])
        run('default-zone', fc + ['--get-default-zone'])
        run('active-zones', fc + ['--get-active-zones'])
        for state, flag in (('runtime', []), ('permanent', ['--permanent'])):
            run('zones-' + state, fc + flag + ['--list-all-zones'])
            run('dns-service-' + state, fc + flag + ['--info-service=dns'])
            run('ipset-info-' + state, fc + flag + ['--info-ipset=' + IPSET])
            run('ipset-entries-' + state, fc + flag + ['--ipset=' + IPSET, '--get-entries'])
            run('policies-' + state, fc + flag + ['--list-all-policies'])
            run('direct-' + state, fc + flag + ['--direct', '--get-all-rules'])
        active = run('nm-active', ['nmcli', '-t', '-f', 'NAME,DEVICE', 'connection', 'show', '--active'])
        names = [l.rsplit(':', 1)[0] for l in active.splitlines() if l.endswith(':' + IFACE)]
        if len(names) != 1:
            raise Stop('expected exactly one active NetworkManager connection on ' + IFACE)
        run('nm-connection', ['nmcli', '-g', 'connection.zone,connection.autoconnect', 'connection', 'show', names[0]])
        run('nft-ruleset', ['sudo', '-n', 'nft', 'list', 'ruleset'])
        summary = summarize(outputs)
        summary['host'] = host
        (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        status = {'status': 'COMPLETE_COLLECTION_ONLY', 'finished_at_kst': now(),
                  'claims_excluded': ['packet test', 'reboot persistence', 'AC PASS', 'independent review']}
        rc = 0
    except (Stop, ValueError, UnicodeError) as exc:
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

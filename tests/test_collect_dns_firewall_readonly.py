"""Mock tests for tools/collect_dns_firewall_readonly.py (no server, no firewall, no NetworkManager)."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('fw', ROOT / 'tools' / 'collect_dns_firewall_readonly.py')
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)

RULE = 'rule family="ipv4" source ipset="fds-dns-clients" service name="dns" accept'
ENTRIES = '\n'.join(f'10.1.93.{n}' for n in (50, 51, 52, 53, 54, 55, 56, 102, 103, 104, 105, 107, 108, 109)) + '\n'


def zones(active, interfaces, rule=True):
    head = 'public (default, active)' if active else 'public (default)'
    rules = f'\n\t{RULE}' if rule else ''
    return (f'block\n  target: %%REJECT%%\n  services: \n\n'
            f'{head}\n  target: default\n  interfaces: {interfaces}\n  sources: \n'
            f'  services: cockpit dhcpv6-client ssh\n  ports: \n  rich rules: {rules}\n\n'
            f'trusted\n  target: ACCEPT\n  services: \n')


def service(ports='53/tcp 53/udp'):
    return f'dns\n  ports: {ports}\n  protocols: \n  source-ports: \n  modules: \n  destination: \n'


class FakeHost:
    def __init__(self, **f):
        self.f = f
        self.calls = []

    def __call__(self, argv, **kwargs):
        self.calls.append(list(argv))
        F.check_read_only(list(argv))  # the tool must never send a refused command
        out, rc = self.answer(list(argv))
        return subprocess.CompletedProcess(argv, rc, out.encode(), b'SENSITIVE-STDERR')

    def answer(self, a):
        cmd = a[2:] if a[:2] == ['sudo', '-n'] else a
        perm = '--permanent' in cmd
        if cmd[:2] == ['systemctl', 'is-active']:
            return ('inactive\n', 3) if self.f.get('inactive') else ('active\n', 0)
        if cmd[:2] == ['systemctl', 'is-enabled']:
            return 'enabled\n', 0
        if cmd[0] == 'firewall-cmd':
            opt = [x for x in cmd[1:] if x != '--permanent']
            if opt == ['--get-default-zone']:
                return 'public\n', 0
            if opt == ['--get-active-zones']:
                return 'public (default)\n  interfaces: ens160\n', 0
            if opt == ['--list-all-zones']:
                rule = not (perm and self.f.get('no_perm_rule'))
                return zones(not perm, '' if perm else 'ens160', rule), 0
            if opt == ['--info-service=dns']:
                return service(self.f.get('ports', '53/tcp 53/udp')), 0
            if opt[0].startswith('--info-ipset='):
                return 'fds-dns-clients\n  type: hash:ip\n  entries: \n', 0
            if opt == ['--ipset=fds-dns-clients', '--get-entries']:
                if perm and self.f.get('ipset_diff'):
                    return ENTRIES.replace('10.1.93.56\n', ''), 0
                return ENTRIES, 0
            if opt == ['--list-all-policies']:
                return 'allow-host-ipv6 (active)\n  priority: -15000\n', 0
            if opt == ['--direct', '--get-all-rules']:
                return '', 0
        if cmd[0] == 'nmcli' and '--active' in cmd:
            rows = self.f.get('nm_rows', ['ens160:ens160', 'lo:lo'])
            return '\n'.join(rows) + '\n', 0
        if cmd[0] == 'nmcli':
            return self.f.get('nm_values', '\nyes') + '\n', 0
        if cmd == ['nft', 'list', 'ruleset']:
            return 'table inet firewalld {\n}\n', 0
        raise AssertionError(f'unexpected {a}')


class FirewallBase(unittest.TestCase):
    def run_tool(self, host='dns01', euid=1000, **f):
        home = tempfile.TemporaryDirectory()
        self.addCleanup(home.cleanup)
        fake = FakeHost(**f)
        with mock.patch.object(F.subprocess, 'run', fake), \
                mock.patch.object(F.socket, 'gethostname', return_value=host), \
                mock.patch.object(F.os, 'geteuid', return_value=euid), \
                mock.patch.object(F.os, 'getuid', return_value=euid), \
                mock.patch.object(F.Path, 'home', return_value=Path(home.name)), \
                mock.patch('builtins.print'):
            rc = F.main()
        dirs = [p for p in Path(home.name).iterdir() if p.is_dir()]
        return rc, (dirs[0] if dirs else None), fake

    def summary(self, out):
        return json.loads((out / 'summary.json').read_text(encoding='utf-8'))

    def assert_clean(self, out):
        for p in out.iterdir():
            self.assertNotIn(b'SENSITIVE-STDERR', p.read_bytes(), p.name)
        for line in (out / 'SHA256SUMS').read_text(encoding='utf-8').splitlines():
            digest, name = line.split('  ', 1)
            self.assertEqual(hashlib.sha256((out / name).read_bytes()).hexdigest(), digest)


class FirewallNormalTest(FirewallBase):
    def test_complete_summary(self):
        rc, out, fake = self.run_tool()
        self.assertEqual(rc, 0)
        s = self.summary(out)
        self.assertTrue(s['default_zone_is_public'])
        self.assertEqual(s['dns_service_ports_runtime'], ['53/tcp', '53/udp'])
        self.assertTrue(s['dns_service_ports_expected'])
        self.assertTrue(s['dns_rich_rule_runtime'] and s['dns_rich_rule_permanent'])
        self.assertEqual((s['ipset_entries_runtime'], s['ipset_entries_permanent']), (14, 14))
        self.assertTrue(s['ipset_runtime_equals_permanent'])
        self.assertTrue(s['interface_in_runtime_public'])
        self.assertFalse(s['interface_in_permanent_public'])
        self.assertEqual((s['nm_connection_zone'], s['nm_autoconnect']), ('', 'yes'))
        self.assertFalse(s['dns_service_directly_in_public'])
        self.assertEqual(s['direct_rules_runtime'], [])
        self.assert_clean(out)

    def test_only_allow_listed_commands(self):
        _, _, fake = self.run_tool()
        self.assertGreater(len(fake.calls), 10)
        for argv in fake.calls:
            F.check_read_only(argv)

    def test_nm_zone_value_with_colon(self):
        rc, out, _ = self.run_tool(nm_values='pub:lic\nno')
        s = self.summary(out)
        self.assertEqual((s['nm_connection_zone'], s['nm_autoconnect']), ('pub:lic', 'no'))

    def test_observations_report_differences_without_stopping(self):
        rc, out, _ = self.run_tool(ipset_diff=True, no_perm_rule=True, ports='53/tcp 53/udp 853/tcp')
        self.assertEqual(rc, 0)
        s = self.summary(out)
        self.assertFalse(s['ipset_runtime_equals_permanent'])
        self.assertFalse(s['dns_rich_rule_permanent'])
        self.assertFalse(s['dns_service_ports_expected'])


class FirewallStopTest(FirewallBase):
    def assert_stopped(self, rc, out, reason):
        self.assertEqual(rc, 1)
        st = json.loads((out / 'STATUS.json').read_text(encoding='utf-8'))
        self.assertEqual(st['status'], 'INCOMPLETE_DO_NOT_SUBMIT_AS_COMPLETE')
        self.assertIn(reason, st['reason'])
        self.assertFalse((out / 'summary.json').exists())
        self.assert_clean(out)

    def test_refuses_root_and_unknown_host(self):
        self.assertEqual(self.run_tool(euid=0)[:2], (1, None))
        self.assertEqual(self.run_tool(host='db01')[:2], (1, None))

    def test_firewalld_inactive(self):
        rc, out, _ = self.run_tool(inactive=True)
        self.assert_stopped(rc, out, 'nonzero exit')

    def test_ambiguous_nm_connection(self):
        rc, out, _ = self.run_tool(nm_rows=['a:ens160', 'b:ens160'])
        self.assert_stopped(rc, out, 'exactly one active NetworkManager connection')

    def test_malformed_nm_property_output(self):
        rc, out, _ = self.run_tool(nm_values='yes')
        self.assert_stopped(rc, out, 'unexpected NetworkManager property output')

    def test_unexpected_nm_autoconnect_value(self):
        rc, out, _ = self.run_tool(nm_values='\nmaybe')
        self.assert_stopped(rc, out, 'unexpected NetworkManager autoconnect value')


class ReadOnlyGuardTest(unittest.TestCase):
    def refused(self, argv):
        with self.assertRaises(F.Stop):
            F.check_read_only(argv)

    def test_refuses_write_like_commands(self):
        fc = ['sudo', '-n', 'firewall-cmd']
        for argv in (fc + ['--reload'], fc + ['--complete-reload'], fc + ['--add-rich-rule=' + RULE],
                     fc + ['--permanent', '--remove-service=dns'], fc + ['--runtime-to-permanent'],
                     fc + ['--set-default-zone=trusted'], fc + ['--ipset=fds-dns-clients', '--add-entry=10.0.0.1'],
                     fc + ['--panic-on'], fc + ['--direct', '--add-rule', 'ipv4'],
                     ['nmcli', 'connection', 'up', 'ens160'], ['nmcli', 'connection', 'modify', 'ens160'],
                     ['nmcli', '-g', 'connection.zone', 'connection', 'modify', 'x'],
                     ['sudo', '-n', 'nft', 'flush', 'ruleset'], ['systemctl', 'restart', 'firewalld'],
                     ['sudo', '-n', 'rm', '-f', '/etc/firewalld/zones/public.xml']):
            self.refused(argv)

    def test_execute_refuses_before_running(self):
        with mock.patch.object(F.subprocess, 'run') as run:
            with self.assertRaises(F.Stop):
                F.execute(['sudo', '-n', 'firewall-cmd', '--reload'])
            run.assert_not_called()
            F.execute(['sudo', '-n', 'firewall-cmd', '--get-default-zone'])
            run.assert_called_once()

    def test_allows_read_commands(self):
        for argv in (['sudo', '-n', 'firewall-cmd', '--permanent', '--list-all-zones'],
                     ['sudo', '-n', 'firewall-cmd', '--ipset=fds-dns-clients', '--get-entries'],
                     ['nmcli', '-t', '-f', 'NAME,DEVICE', 'connection', 'show', '--active'],
                     ['sudo', '-n', 'nft', 'list', 'ruleset'], ['systemctl', 'is-active', 'firewalld']):
            F.check_read_only(argv)


if __name__ == '__main__':
    unittest.main()

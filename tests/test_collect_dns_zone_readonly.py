"""Mock tests for tools/collect_dns_zone_readonly.py (no server, no network, no sudo).

Every external command is replaced by FakeServer. The collector file itself is
not modified: its SHA-256 must stay equal to the executed copy recorded in the
evidence repository (9458d9aa...).
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
COLLECTOR = ROOT / 'tools' / 'collect_dns_zone_readonly.py'
EXECUTED_SHA256 = '9458d9aa60d8589809eadc129cd4186f7084a2eea7fdba8302c5a090ae0e1346'

spec = importlib.util.spec_from_file_location('collector', COLLECTOR)
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

MASKED = {
    'dns01': (ROOT / 'references/console-20260918/dns01/named.expanded.sanitized.reference.conf').read_bytes(),
    'dns02': (ROOT / 'references/console-20260918/dns02/named.expanded.sanitized.reference.conf').read_bytes(),
}
ZONE_TEXT = (ROOT / 'zones/fds.internal.zone').read_bytes()
NORMALIZED = (ROOT / 'references/console-20260918/dns02/fds.internal.normalized.reference.zone').read_bytes()
RAW_ZONE = b'\x00\x00\x00\x01raw-format-placeholder' * 8
SECRET_VALUE = 'c2VjcmV0LXZhbHVlLWZvci10ZXN0LW9ubHk='


class FakeServer:
    """Answers the collector's commands like a healthy dns01/dns02; faults are switched on per test."""

    def __init__(self, host, **faults):
        self.host = host
        self.f = faults
        self.pid_calls = 0
        self.cmdline_calls = 0
        self.stat_calls = 0
        self.status_calls = 0
        self.calls = []

    def source(self):
        return C.EXPECTED[self.host][1]

    def zone_bytes(self):
        if self.f.get('include'):
            return ZONE_TEXT + b'$INCLUDE other.zone\n'
        return RAW_ZONE if self.host == 'dns02' else ZONE_TEXT

    def __call__(self, argv, **kwargs):
        self.calls.append(list(argv))
        out, rc = self.answer(list(argv))
        return subprocess.CompletedProcess(argv, rc, out, b'SENSITIVE-STDERR-MUST-NOT-BE-SAVED')

    def answer(self, a):
        pid = '1266'
        if a[:2] == ['systemctl', 'show']:
            self.pid_calls += 1
            if self.f.get('pid_changes') and self.pid_calls > 1:
                return b'9999\n', 0
            return (pid + '\n').encode(), 0
        if a[:2] == ['sudo', '-n'] and self.f.get('sudo_denied'):
            return b'', 1
        cmd = a[2:] if a[:2] == ['sudo', '-n'] else a
        if cmd[:2] == ['readlink', '-e'] and cmd[2].endswith('/exe'):
            return b'/usr/sbin/named\n', 0
        if cmd[:2] == ['readlink', '-e'] and cmd[2].endswith('/root'):
            return b'/\n', 0
        if cmd[:2] == ['readlink', '-e']:
            target = '/var/named/elsewhere.zone' if self.f.get('symlink') else self.source()
            return (target + '\n').encode(), 0
        if cmd[0] == 'cat' and cmd[1].endswith('/cmdline'):
            self.cmdline_calls += 1
            args = self.f.get('cmdline', [b'/usr/sbin/named', b'-u', b'named', b'-c', b'/etc/named.conf'])
            if self.f.get('args_change') and self.cmdline_calls > 1:
                args = args + [b'-4']
            return b'\0'.join(args) + b'\0', 0
        if cmd[0] == 'named-checkconf':
            cfg = MASKED[self.host]
            if self.f.get('config_changed'):
                cfg += b'# changed\n'
            if self.f.get('secret'):
                cfg = cfg.replace(b'????????????????????????????????????????????', SECRET_VALUE.encode())
            return cfg, 0
        if cmd[:2] == ['rndc', 'zonestatus']:
            self.status_calls += 1
            serial = '2026090101'
            if self.f.get('serial_changes') and self.status_calls > 1:
                serial = '2026090102'
            dynamic = 'yes' if self.f.get('dynamic') else 'no'
            files = self.source()[len('/var/named/'):]
            return (f'name: fds.internal\ntype: primary\nfiles: {files}\nserial: {serial}\n'
                    f'dynamic: {dynamic}\n').encode(), 0
        if cmd[0] == 'sh':
            return (b'present\n' if self.f.get('journal') else b'absent\n'), 0
        if cmd[0] == 'stat':
            self.stat_calls += 1
            mtime = '2026-09-18 12:21:02.894277000 +0900'
            if self.f.get('file_changes') and self.stat_calls > 1:
                mtime = '2026-09-18 12:30:00.000000000 +0900'
            size = len(self.zone_bytes())
            return f'regular file|64768|1343302|{size}|{mtime}|{mtime}\n'.encode(), 0
        if cmd[0] == 'cat':
            return self.zone_bytes(), 0
        if cmd == ['named', '-v']:
            return b'BIND 9.18.33\n', 0
        if cmd == ['named-checkzone', '-v']:
            return b'9.18.33\n', 0
        if cmd[0] == 'named-checkzone':
            fmt = cmd[cmd.index('-f') + 1]
            if self.f.get('checkzone_fail'):
                return b'', 1
            if self.host == 'dns02' and fmt == 'text':
                return b'', 1
            return NORMALIZED, 0
        if cmd[0] == 'firewall-cmd':
            if any(x.startswith('--ipset=') for x in cmd):
                return b'10.1.93.50\n10.1.93.51\n', 0
            return b'public (active)\n  interfaces: ens160\n', 0
        raise AssertionError(f'unexpected command: {a}')


class CollectorTestBase(unittest.TestCase):
    def run_collector(self, host='dns01', euid=1000, **faults):
        home = tempfile.TemporaryDirectory()
        self.addCleanup(home.cleanup)
        fake = FakeServer(host, **faults)
        with mock.patch.object(C.subprocess, 'run', fake), \
                mock.patch.object(C.socket, 'gethostname', return_value=host + '.fds.internal'), \
                mock.patch.object(C.os, 'geteuid', return_value=euid), \
                mock.patch.object(C.os, 'getuid', return_value=euid), \
                mock.patch.object(C.Path, 'home', return_value=Path(home.name)), \
                mock.patch('builtins.print'):
            rc = C.main()
        outs = [p for p in Path(home.name).iterdir() if p.is_dir()]
        return rc, (outs[0] if outs else None), fake

    def status(self, out):
        return json.loads((out / 'STATUS.json').read_text(encoding='utf-8'))

    def assert_stopped(self, rc, out, reason_part):
        self.assertEqual(rc, 1)
        st = self.status(out)
        self.assertEqual(st['status'], 'INCOMPLETE_DO_NOT_SUBMIT_AS_COMPLETE')
        self.assertIn(reason_part, st['reason'])
        self.assert_no_leak(out)

    def assert_no_leak(self, out):
        for p in out.iterdir():
            data = p.read_bytes()
            self.assertNotIn(b'SENSITIVE-STDERR', data, p.name)
            self.assertNotIn(SECRET_VALUE.encode(), data, p.name)
        manifest = (out / 'SHA256SUMS').read_text(encoding='utf-8')
        self.assertNotIn('\r', manifest)
        for line in manifest.splitlines():
            digest, name = line.split('  ', 1)
            self.assertEqual(hashlib.sha256((out / name).read_bytes()).hexdigest(), digest, name)


class CollectorIdentityTest(unittest.TestCase):
    def test_collector_bytes_equal_executed_copy(self):
        self.assertEqual(hashlib.sha256(COLLECTOR.read_bytes()).hexdigest(), EXECUTED_SHA256)

    def test_masked_reference_configs_match_pinned_hashes(self):
        for host, data in MASKED.items():
            self.assertEqual(hashlib.sha256(data).hexdigest(), C.EXPECTED[host][0], host)


class CollectorNormalTest(CollectorTestBase):
    def test_dns01_text_zone_complete(self):
        rc, out, fake = self.run_collector('dns01')
        self.assertEqual(rc, 0)
        self.assertEqual(self.status(out)['status'], 'COMPLETE_COLLECTION_ONLY')
        self.assertEqual((out / 'fds.internal.source').read_bytes(), ZONE_TEXT)
        self.assertEqual((out / 'zone-source-format.txt').read_text(), 'text\n')
        self.assertEqual((out / 'named.expanded.sanitized.conf').read_bytes(), MASKED['dns01'])
        self.assert_no_leak(out)
        commands = json.loads((out / 'COMMANDS.json').read_text(encoding='utf-8'))
        self.assertTrue(all(c['stderr'].startswith('suppressed') for c in commands))

    def test_dns02_raw_zone_falls_back_to_raw(self):
        rc, out, fake = self.run_collector('dns02')
        self.assertEqual(rc, 0)
        self.assertEqual((out / 'zone-source-format.txt').read_text(), 'raw\n')
        commands = json.loads((out / 'COMMANDS.json').read_text(encoding='utf-8'))
        rcs = {c['label']: c['exit_code'] for c in commands}
        self.assertEqual((rcs['checkzone-text'], rcs['checkzone-raw']), (1, 0))
        self.assert_no_leak(out)

    def test_no_write_like_commands_are_issued(self):
        _, _, fake = self.run_collector('dns01')
        forbidden = {'reload', 'restart', 'stop', 'start', 'retransfer', 'freeze', 'thaw', 'sync',
                     '--add-rich-rule', '--reload', '--runtime-to-permanent', 'rm', 'mv', 'cp', 'tee'}
        for argv in fake.calls:
            self.assertFalse(forbidden & set(argv), argv)


class CollectorStopTest(CollectorTestBase):
    def test_refuses_root(self):
        rc, out, _ = self.run_collector('dns01', euid=0)
        self.assertEqual((rc, out), (1, None))

    def test_refuses_unknown_host(self):
        rc, out, _ = self.run_collector('dns03')
        self.assertEqual((rc, out), (1, None))

    def test_chroot_option(self):
        rc, out, _ = self.run_collector(
            'dns01', cmdline=[b'/usr/sbin/named', b'-t', b'/var/named/chroot', b'-c', b'/etc/named.conf'])
        self.assert_stopped(rc, out, 'chroot')

    def test_config_changed(self):
        rc, out, _ = self.run_collector('dns01', config_changed=True)
        self.assert_stopped(rc, out, 'masked disk configuration changed')

    def test_unmasked_secret(self):
        rc, out, _ = self.run_collector('dns01', secret=True)
        self.assert_stopped(rc, out, 'unmasked shared secret')

    def test_symlinked_zone(self):
        rc, out, _ = self.run_collector('dns01', symlink=True)
        self.assert_stopped(rc, out, 'symlink')

    def test_zone_include(self):
        rc, out, _ = self.run_collector('dns01', include=True)
        self.assert_stopped(rc, out, 'INCLUDE')

    def test_dynamic_zone(self):
        rc, out, _ = self.run_collector('dns01', dynamic=True)
        self.assert_stopped(rc, out, 'dynamic zone')

    def test_journal_present(self):
        rc, out, _ = self.run_collector('dns01', journal=True)
        self.assert_stopped(rc, out, 'journal')

    def test_sudo_denied(self):
        rc, out, _ = self.run_collector('dns01', sudo_denied=True)
        self.assert_stopped(rc, out, 'nonzero exit')

    def test_zone_file_changed(self):
        rc, out, _ = self.run_collector('dns01', file_changes=True)
        self.assert_stopped(rc, out, 'zone changed during intake')

    def test_serial_changed(self):
        rc, out, _ = self.run_collector('dns01', serial_changes=True)
        self.assert_stopped(rc, out, 'serial changed')

    def test_pid_changed(self):
        rc, out, _ = self.run_collector('dns01', pid_changes=True)
        self.assert_stopped(rc, out, 'process changed')

    def test_arguments_changed(self):
        rc, out, _ = self.run_collector('dns01', args_change=True)
        self.assert_stopped(rc, out, 'arguments changed')

    def test_zone_check_fails_both_formats(self):
        rc, out, _ = self.run_collector('dns01', checkzone_fail=True)
        self.assert_stopped(rc, out, 'failed both text and raw')


class ProcessConfigTest(unittest.TestCase):
    def check_stop(self, args, message):
        with self.assertRaises(C.Stop) as ctx:
            C.process_config(b'\0'.join(args) + b'\0')
        self.assertIn(message, str(ctx.exception))

    def test_accepts_standard(self):
        self.assertEqual(C.process_config(b'/usr/sbin/named\0-u\0named\0-c\0/etc/named.conf\0'),
                         '/etc/named.conf')

    def test_rejects_other_executable(self):
        self.check_stop([b'/usr/local/sbin/named', b'-c', b'/etc/named.conf'], 'unexpected named executable')

    def test_rejects_missing_config_option(self):
        self.check_stop([b'/usr/sbin/named', b'-u', b'named'], 'explicit -c')

    def test_rejects_duplicate_config_option(self):
        self.check_stop([b'/usr/sbin/named', b'-c', b'/etc/named.conf', b'-c', b'/etc/other.conf'], 'explicit -c')

    def test_rejects_nonstandard_path(self):
        self.check_stop([b'/usr/sbin/named', b'-c', b'/etc/named-alt.conf'], 'nonstandard configuration path')

    def test_rejects_attached_config_option(self):
        self.check_stop([b'/usr/sbin/named', b'-c', b'/etc/named.conf', b'-c/etc/x.conf'], 'ambiguous configuration option')


if __name__ == '__main__':
    unittest.main()

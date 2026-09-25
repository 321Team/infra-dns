"""Mock tests for tools/collect_named_structure_readonly.py (no server, no network, no sudo)."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('structure', ROOT / 'tools' / 'collect_named_structure_readonly.py')
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)

SECRET = 'dGVzdC1vbmx5LXNlY3JldC12YWx1ZS0wMTIzNDU2Nzg5QUI='
RNDC_SECRET = 'cm5kYy10ZXN0LXNlY3JldC0wMTIzNDU2Nzg5YWJjZGVm'

NAMED_CONF = '''// named.conf for tests
// include "/etc/commented-out.conf";
/* include "/etc/also-commented.conf"; */
options {
\tdirectory "/var/named";
\tforwarders { 8.8.8.8; };  # comment with "quote
\tallow-transfer { "none"; };
};
include "/etc/named/fds-transfer.key";
controls { inet 127.0.0.1 port 953 allow { 127.0.0.1; } keys { "rndc-key"; }; };
include "/etc/rndc.key";
zone "fds.internal" IN {
\ttype primary;
\tfile "fds.internal.zone";
\tallow-transfer { key "fds-transfer-key"; };
\talso-notify { 10.1.93.53 key "fds-transfer-key"; };
};
include "/etc/named.rfc1912.zones";
include "/etc/named.root.key";
'''
FILES = {
    '/etc/named.conf': NAMED_CONF,
    '/etc/named/fds-transfer.key': f'key "fds-transfer-key" {{\n\talgorithm hmac-sha256;\n\tsecret "{SECRET}";\n}};\n',
    '/etc/rndc.key': f'key "rndc-key" {{\n\talgorithm hmac-sha256;\n\tsecret "{RNDC_SECRET}";\n}};\n',
    '/etc/named.rfc1912.zones': 'zone "localhost" IN {\n\ttype primary;\n\tfile "named.localhost";\n};\n',
    '/etc/named.root.key': 'trust-anchors {\n\t"." initial-ds 20326 8 2 "E06D44B8";\n};\n',
}
MASKED_EXPANDED = b'options {\n\tdirectory "/var/named";\n};\nkey "fds-transfer-key" {\n\talgorithm "hmac-sha256";\n\tsecret "????????????????????????????????????????????";\n};\n'


class FakeServer:
    def __init__(self, files=None, **faults):
        self.files = dict(FILES if files is None else files)
        self.f = faults
        self.pid_calls = 0
        self.calls = []

    def __call__(self, argv, **kwargs):
        self.calls.append(list(argv))
        out, rc = self.answer(list(argv))
        return subprocess.CompletedProcess(argv, rc, out, b'SENSITIVE-STDERR')

    def answer(self, a):
        if a[:2] == ['systemctl', 'show']:
            self.pid_calls += 1
            return (b'9999\n' if self.f.get('pid_changes') and self.pid_calls > 1 else b'1266\n'), 0
        cmd = a[2:] if a[:2] == ['sudo', '-n'] else a
        if cmd[:2] == ['readlink', '-e']:
            p = cmd[2]
            if p.endswith('/exe'):
                return b'/usr/sbin/named\n', 0
            if p.endswith('/root'):
                return b'/\n', 0
            if p not in self.files:
                return b'', 1
            return ((p + '.real' if p in self.f.get('symlinks', ()) else p) + '\n').encode(), 0
        if cmd[0] == 'cat' and cmd[1].endswith('/cmdline'):
            return b'/usr/sbin/named\0-u\0named\0-c\0/etc/named.conf\0', 0
        if cmd[0] == 'stat':
            data = self.files[cmd[-1]].encode()
            size = self.f.get('size', len(data))
            return f'regular file|root|named|640|system_u:object_r:named_conf_t:s0|{size}\n'.encode(), 0
        if cmd[0] == 'cat':
            return self.files[cmd[1]].encode(), 0
        if cmd[0] == 'named-checkconf':
            return (self.f.get('expanded', MASKED_EXPANDED)), 0
        raise AssertionError(f'unexpected command {a}')


class StructureBase(unittest.TestCase):
    def run_tool(self, host='dns01', euid=1000, **kw):
        home = tempfile.TemporaryDirectory()
        self.addCleanup(home.cleanup)
        fake = FakeServer(**kw)
        with mock.patch.object(S.subprocess, 'run', fake), \
                mock.patch.object(S.socket, 'gethostname', return_value=host), \
                mock.patch.object(S.os, 'geteuid', return_value=euid), \
                mock.patch.object(S.os, 'getuid', return_value=euid), \
                mock.patch.object(S.Path, 'home', return_value=Path(home.name)), \
                mock.patch('builtins.print'):
            rc = S.main()
        dirs = [p for p in Path(home.name).iterdir() if p.is_dir()]
        return rc, (dirs[0] if dirs else None), fake

    def assert_no_secret_output(self, out):
        raw_hashes = {hashlib.sha256(v.encode()).hexdigest() for v in FILES.values()
                      if 'secret' in v}
        for p in out.rglob('*'):
            if not p.is_file():
                continue
            data = p.read_bytes()
            for needle in (SECRET, RNDC_SECRET, 'SENSITIVE-STDERR', *raw_hashes):
                self.assertNotIn(needle.encode(), data, f'{needle[:12]} leaked in {p.name}')
        for line in (out / 'SHA256SUMS').read_text(encoding='utf-8').splitlines():
            digest, name = line.split('  ', 1)
            self.assertEqual(hashlib.sha256((out / name).read_bytes()).hexdigest(), digest, name)

    def assert_stopped(self, rc, out, reason):
        self.assertEqual(rc, 1)
        st = json.loads((out / 'STATUS.json').read_text(encoding='utf-8'))
        self.assertEqual(st['status'], 'INCOMPLETE_DO_NOT_SUBMIT_AS_COMPLETE')
        self.assertIn(reason, st['reason'])
        self.assertEqual(list((out / 'masked').iterdir()), [])
        self.assertFalse((out / 'structure.json').exists())
        self.assert_no_secret_output(out)


class StructureNormalTest(StructureBase):
    def test_complete_structure(self):
        rc, out, fake = self.run_tool()
        self.assertEqual(rc, 0)
        s = json.loads((out / 'structure.json').read_text(encoding='utf-8'))
        paths = [f['path'] for f in s['files']]
        self.assertEqual(paths, ['/etc/named.conf', '/etc/named/fds-transfer.key', '/etc/rndc.key',
                                 '/etc/named.rfc1912.zones', '/etc/named.root.key'])
        self.assertNotIn('/etc/commented-out.conf', json.dumps(s))
        by = {f['path']: f for f in s['files']}
        self.assertEqual(by['/etc/named/fds-transfer.key']['included_from'], '/etc/named.conf:9')
        self.assertTrue(by['/etc/named/fds-transfer.key']['contains_secret_statement'])
        self.assertFalse(by['/etc/named.rfc1912.zones']['contains_secret_statement'])
        self.assertEqual(by['/etc/named/fds-transfer.key']['key_definitions'][0]['algorithm'], 'hmac-sha256')
        self.assertEqual(s['keys_defined'], ['fds-transfer-key', 'rndc-key'])
        self.assertEqual(s['keys_referenced'], ['fds-transfer-key', 'rndc-key'])
        self.assertEqual(s['keys_referenced_but_not_defined'], [])
        self.assertEqual(by['/etc/named.conf']['selinux_context'], 'system_u:object_r:named_conf_t:s0')
        zone = [x for x in by['/etc/named.conf']['statements'] if x['type'] == 'zone']
        self.assertEqual(zone[0]['name'], 'fds.internal')
        masked = (out / by['/etc/named/fds-transfer.key']['masked_copy']).read_text(encoding='utf-8')
        self.assertIn('secret "????????"', masked)
        self.assert_no_secret_output(out)

    def test_undefined_key_reference_is_reported(self):
        files = dict(FILES)
        files['/etc/named.conf'] = NAMED_CONF.replace('include "/etc/named/fds-transfer.key";\n', '')
        del files['/etc/named/fds-transfer.key']
        rc, out, _ = self.run_tool(files=files)
        self.assertEqual(rc, 0)
        s = json.loads((out / 'structure.json').read_text(encoding='utf-8'))
        self.assertEqual(s['keys_referenced_but_not_defined'], ['fds-transfer-key'])

    def test_only_read_commands(self):
        _, _, fake = self.run_tool()
        allowed = {'systemctl', 'readlink', 'cat', 'stat', 'named-checkconf'}
        for argv in fake.calls:
            cmd = argv[2:] if argv[:2] == ['sudo', '-n'] else argv
            self.assertIn(cmd[0], allowed, argv)
            self.assertNotIn('reload', argv)


class StructureStopTest(StructureBase):
    def with_conf(self, extra):
        files = dict(FILES)
        files['/etc/named.conf'] = NAMED_CONF + extra
        return files

    def test_refuses_root_and_unknown_host(self):
        self.assertEqual(self.run_tool(euid=0)[:2], (1, None))
        self.assertEqual(self.run_tool(host='web01')[:2], (1, None))

    def test_relative_include(self):
        files = self.with_conf('include "named.extra";\n')
        files['named.extra'] = 'options { };\n'
        rc, out, _ = self.run_tool(files=files)
        self.assert_stopped(rc, out, 'relative include')

    def test_include_outside_allowed_prefix(self):
        files = self.with_conf('include "/opt/named/extra.conf";\n')
        files['/opt/named/extra.conf'] = 'acl x { 10.0.0.1; };\n'
        rc, out, _ = self.run_tool(files=files)
        self.assert_stopped(rc, out, 'outside /etc or /var/named')

    def test_include_cycle(self):
        files = dict(FILES)
        files['/etc/named.root.key'] = FILES['/etc/named.root.key'] + 'include "/etc/named.conf";\n'
        rc, out, _ = self.run_tool(files=files)
        self.assert_stopped(rc, out, 'include cycle')

    def test_symlinked_file(self):
        rc, out, _ = self.run_tool(symlinks=('/etc/rndc.key',))
        self.assert_stopped(rc, out, 'symlinked')

    def test_oversized_file(self):
        rc, out, _ = self.run_tool(size=S.MAX_BYTES + 1)
        self.assert_stopped(rc, out, 'type or size')

    def test_unmasked_expanded_config(self):
        rc, out, _ = self.run_tool(expanded=MASKED_EXPANDED.replace(b'?' * 44, SECRET.encode()))
        self.assert_stopped(rc, out, 'unmasked shared secret')

    def test_unquoted_secret(self):
        files = dict(FILES)
        files['/etc/rndc.key'] = 'key "rndc-key" {\n\talgorithm hmac-sha256;\n\tsecret ' + RNDC_SECRET + ';\n};\n'
        rc, out, _ = self.run_tool(files=files)
        self.assert_stopped(rc, out, 'unquoted secret')

    def test_private_key_material(self):
        header = '-----BEGIN ' + 'RSA PRIVATE KEY' + '-----'  # assembled so the repo scanner stays clean
        files = self.with_conf('# ' + header + '\n')
        rc, out, _ = self.run_tool(files=files)
        self.assert_stopped(rc, out, 'private key')

    def test_unbalanced_braces(self):
        files = self.with_conf('acl broken { 10.0.0.1;\n')
        rc, out, _ = self.run_tool(files=files)
        self.assert_stopped(rc, out, 'unbalanced braces')

    def test_pid_changed(self):
        rc, out, _ = self.run_tool(pid_changes=True)
        self.assert_stopped(rc, out, 'process changed')


class ParserTest(unittest.TestCase):
    def test_strip_comments_keeps_strings_and_lines(self):
        text = 'a "http://x#y" // c\n/* b\n c */ d # e\n'
        s = S.strip_comments(text)
        self.assertIn('"http://x#y"', s)
        self.assertNotIn('// c', s)
        self.assertEqual(s.count('\n'), text.count('\n'))
        self.assertIn(' d ', s)

    def test_mask_secrets_fixed_length(self):
        self.assertEqual(S.mask_secrets(f'secret "{SECRET}";'), 'secret "????????";')

    def test_zone_collector_unchanged(self):
        data = (ROOT / 'tools' / 'collect_dns_zone_readonly.py').read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         '9458d9aa60d8589809eadc129cd4186f7084a2eea7fdba8302c5a090ae0e1346')


if __name__ == '__main__':
    unittest.main()

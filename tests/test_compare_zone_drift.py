"""Tests for tools/compare_zone_drift.py using synthetic collector output folders."""
import hashlib
import importlib.util
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('drift', ROOT / 'tools' / 'compare_zone_drift.py')
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)

REPO_ZONE = ROOT / 'zones' / 'fds.internal.zone'
NORMALIZED = (ROOT / 'references/console-20260918/dns02/fds.internal.normalized.reference.zone').read_bytes()


def zonestatus(serial, kind):
    files = 'fds.internal.zone' if kind == 'primary' else 'slaves/fds.internal.zone'
    return f'name: fds.internal\ntype: {kind}\nfiles: {files}\nserial: {serial}\ndynamic: no\n'.encode()


class DriftTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)

    def make_host(self, host, source=None, normalized=NORMALIZED, serial='2026090101', after_serial=None,
                  status='COMPLETE_COLLECTION_ONLY', session_host=None):
        folder = self.base / host
        folder.mkdir()
        kind = 'primary' if host == 'dns01' else 'secondary'
        files = {
            'fds.internal.source': source if source is not None else (
                REPO_ZONE.read_bytes() if host == 'dns01' else b'\x00raw-copy'),
            'fds.internal.normalized.zone': normalized,
            'zonestatus-before.txt': zonestatus(serial, kind),
            'zonestatus-after.txt': zonestatus(after_serial or serial, kind),
            'STATUS.json': json.dumps({'status': status, 'finished_at_kst': '2026-09-25T10:00:00+09:00'}).encode(),
            'SESSION.json': json.dumps({'host': session_host or host, 'collector_sha256': 'x' * 64}).encode(),
        }
        for name, data in files.items():
            (folder / name).write_bytes(data)
        lines = [f'{hashlib.sha256(d).hexdigest()}  {n}' for n, d in sorted(files.items())]
        (folder / 'SHA256SUMS').write_text('\n'.join(lines) + '\n', encoding='utf-8')
        return folder

    def run_compare(self, **kw):
        d1 = self.make_host('dns01', **kw.get('dns01', {}))
        d2 = self.make_host('dns02', **kw.get('dns02', {}))
        return D.compare(kw.get('repo', REPO_ZONE), d1, d2)

    def test_no_drift(self):
        r = self.run_compare()
        self.assertEqual(r['result'], 'NO_DRIFT')
        self.assertEqual(r['findings'], [])
        self.assertEqual(set(r['serials'].values()), {'2026090101'})

    def test_dns01_source_differs_from_repository(self):
        r = self.run_compare(dns01={'source': REPO_ZONE.read_bytes() + b'extra IN A 10.1.93.99\n'})
        self.assertEqual(r['result'], 'DRIFT')
        self.assertIn('dns01 disk source differs from repository zone', r['findings'])

    def test_secondary_normalized_differs(self):
        r = self.run_compare(dns02={'normalized': NORMALIZED.replace(b'10.1.93.102', b'10.1.93.199')})
        self.assertIn('dns01 and dns02 normalized zones differ', r['findings'])

    def test_serial_not_transferred(self):
        newer = NORMALIZED.replace(b'2026090101', b'2026092501')
        r = self.run_compare(dns01={'normalized': newer, 'serial': '2026092501'})
        self.assertEqual(r['result'], 'DRIFT')
        self.assertTrue(any(f.startswith('SOA serial differs') for f in r['findings']), r['findings'])

    def test_serial_changed_during_collection(self):
        r = self.run_compare(dns02={'after_serial': '2026090102'})
        self.assertTrue(any('dns02_runtime_after=2026090102' in f for f in r['findings']), r['findings'])

    def test_incomplete_collection_is_invalid(self):
        with self.assertRaisesRegex(D.InputError, 'not complete'):
            self.run_compare(dns01={'status': 'INCOMPLETE_DO_NOT_SUBMIT_AS_COMPLETE'})

    def test_host_mismatch_is_invalid(self):
        with self.assertRaisesRegex(D.InputError, 'SESSION host'):
            self.run_compare(dns02={'session_host': 'dns01'})

    def test_tampered_file_is_invalid(self):
        d1 = self.make_host('dns01')
        d2 = self.make_host('dns02')
        (d1 / 'fds.internal.source').write_bytes(b'tampered')
        with self.assertRaisesRegex(D.InputError, 'does not match SHA256SUMS'):
            D.compare(REPO_ZONE, d1, d2)

    def test_unsafe_manifest_name_is_invalid(self):
        d1 = self.make_host('dns01')
        d2 = self.make_host('dns02')
        with (d1 / 'SHA256SUMS').open('a', encoding='utf-8') as f:
            f.write('0' * 64 + '  ../outside\n')
        with self.assertRaisesRegex(D.InputError, 'unsafe name'):
            D.compare(REPO_ZONE, d1, d2)

    def test_repository_zone_without_soa_is_invalid(self):
        bad = self.base / 'bad.zone'
        bad.write_text('$TTL 300\nwww IN A 10.0.0.1\n', encoding='utf-8')
        with self.assertRaisesRegex(D.InputError, 'no parsable SOA'):
            self.run_compare(repo=bad)

    def test_repository_serial_parses_multiline_soa(self):
        self.assertEqual(D.repo_serial(REPO_ZONE.read_text(encoding='utf-8')), '2026090101')

    def test_main_exit_codes_and_report(self):
        d1 = self.make_host('dns01')
        d2 = self.make_host('dns02')
        report = self.base / 'report.json'
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(D.main(['--dns01', str(d1), '--dns02', str(d2), '--report', str(report)]), 0)
        data = json.loads(report.read_text(encoding='utf-8'))
        self.assertNotIn('source_bytes', json.dumps(data))
        (d1 / 'STATUS.json').write_text('{}', encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(D.main(['--dns01', str(d1), '--dns02', str(d2)]), 1)
        self.assertIn('INVALID_INPUT', out.getvalue())


if __name__ == '__main__':
    unittest.main()

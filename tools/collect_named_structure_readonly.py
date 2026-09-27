#!/usr/bin/env python3
"""Read-only intake of the named.conf include structure and TSIG key references (#6).

Run on dns01 or dns02 as the existing non-root administrator after `sudo -v`.
It reads /etc/named.conf and every file it includes, in memory only, and saves:
  - structure.json: include tree (file, including file:line), file attributes
    (type/owner/group/mode/SELinux context/size), top-level statements, key
    definitions (name, algorithm, file:line, NO secret) and key references
  - masked/NN-<name>: each file with every `secret "..."` value replaced by ????????
  - named.expanded.sanitized.conf: `named-checkconf -p -x` output (informational)
Raw file contents, secret values, raw-file hashes, process argv and command
stderr are never saved or printed. No service, file, firewall or account change;
no reload/restart. Stops (INCOMPLETE) on anything outside the reviewed shape.
"""
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import tempfile

HOSTS = ('dns01', 'dns02')
ROOT_CONFIG = '/etc/named.conf'
ALLOWED_PREFIXES = ('/etc/', '/var/named/')
CRYPTO_POLICY_LINK = '/etc/crypto-policies/back-ends/bind.config'
CRYPTO_POLICY_TARGET_RE = re.compile(r'^/usr/share/crypto-policies/[A-Za-z0-9_.+-]+/bind\\.txt
MAX_DEPTH = 8
MAX_BYTES = 256 * 1024
MASK = '????????'

_spec = importlib.util.spec_from_file_location(
    'zone_collector', Path(__file__).resolve().parent / 'collect_dns_zone_readonly.py')
_zc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_zc)
process_config = _zc.process_config


class Stop(Exception):
    pass


def read_path_for(path, resolved):
    """Return the path to read after a narrowly-scoped symlink check."""
    if resolved == path:
        return path
    if path == CRYPTO_POLICY_LINK and CRYPTO_POLICY_TARGET_RE.fullmatch(resolved):
        return resolved
    raise Stop('symlinked or nonstandard configuration path requires review')


def strip_comments(text):
    """Replace comments with spaces, keeping newlines and quoted strings intact."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == '\\' else 1
            out.append(text[i:j + 1])
            i = j + 1
        elif text.startswith('/*', i):
            j = text.find('*/', i + 2)
            j = n if j < 0 else j + 2
            out.append(''.join('\n' if ch == '\n' else ' ' for ch in text[i:j]))
            i = j
        elif text.startswith('//', i) or c == '#':
            j = text.find('\n', i)
            j = n if j < 0 else j
            out.append(' ' * (j - i))
            i = j
        else:
            out.append(c)
            i += 1
    return ''.join(out)


def line_of(text, pos):
    return text.count('\n', 0, pos) + 1


def mask_secrets(text):
    return re.sub(r'(\bsecret\s+")([^"]*)(")', lambda m: m.group(1) + MASK + m.group(3), text)


def assert_no_secret(text):
    if re.search(r'-----BEGIN (?:\w+ )*PRIVATE KEY-----', text):
        raise Stop('private key material detected; value suppressed')
    for value in re.findall(r'\bsecret\s+"([^"]*)"', text):
        if value != MASK:
            raise Stop('unmasked secret remains; value suppressed')
    if re.search(r'\bsecret\s+[^"\s;]{8,}', text):
        raise Stop('unquoted secret value; value suppressed')


def analyze(text):
    """Structure of one file from comment-stripped text (secrets are not read here)."""
    s = strip_comments(text)
    includes = [(m.group(1), line_of(s, m.start())) for m in re.finditer(r'\binclude\s+"([^"]+)"\s*;', s)]
    key_defs = []
    for m in re.finditer(r'\bkey\s+"?([A-Za-z0-9._-]+)"?\s*\{', s):
        body_end = s.find('}', m.end())
        body = s[m.end():body_end if body_end > 0 else len(s)]
        alg = re.search(r'\balgorithm\s+"?([A-Za-z0-9._-]+)"?\s*;', body)
        key_defs.append({'name': m.group(1), 'line': line_of(s, m.start()),
                         'algorithm': alg.group(1) if alg else None,
                         'has_secret_statement': bool(re.search(r'\bsecret\b', body))})
    key_refs = {m.group(1) for m in re.finditer(r'\bkey\s+"?([A-Za-z0-9._-]+)"?\s*;', s)}
    for m in re.finditer(r'\bkeys\s*\{([^}]*)\}', s):
        key_refs.update(re.findall(r'"?([A-Za-z0-9._-]+)"?\s*;', m.group(1)))
    key_refs = sorted(key_refs)
    statements, depth, start = [], 0, 0
    for i, ch in enumerate(s):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth < 0:
                raise Stop('unbalanced braces')
        elif ch == ';' and depth == 0:
            head = s[start:i].strip()
            if head:
                words = head.split()
                name = words[1].strip('"') if len(words) > 1 and words[0] in ('zone', 'key', 'acl', 'view', 'masters', 'primaries') else None
                statements.append({'type': words[0], 'name': name, 'line': line_of(s, start + len(s[start:i]) - len(s[start:i].lstrip()))})
            start = i + 1
    if depth != 0:
        raise Stop('unbalanced braces')
    return {'includes': includes, 'key_definitions': key_defs, 'key_references': key_refs,
            'statements': statements}


def now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()


def main():
    os.umask(0o077)
    host = socket.gethostname().split('.')[0]
    if host not in HOSTS or os.geteuid() == 0:
        print('STOP: use the existing non-root administrator on dns01 or dns02')
        return 1
    out = Path(tempfile.mkdtemp(prefix='dns-named-structure.' + host + '.', dir=str(Path.home())))
    (out / 'masked').mkdir()
    commands = []

    def run(label, argv, allowed=(0,)):
        item = {'label': label, 'command': argv, 'started_at_kst': now(),
                'stdout': 'not saved unless listed in STATUS', 'stderr': 'suppressed; may contain sensitive diagnostics'}
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
        return result.stdout

    files, order = {}, []
    try:
        session = {'host': host, 'started_at_kst': now(), 'uid': os.getuid(),
                   'collector_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   'scope': 'read-only named.conf include structure and key references; no secrets, no DNS test'}
        (out / 'SESSION.json').write_text(json.dumps(session, indent=2) + '\n', encoding='utf-8')
        pid_cmd = ['systemctl', 'show', 'named', '--property=MainPID', '--value']
        pid = run('named-mainpid-before', pid_cmd).strip().decode('ascii')
        if not pid.isdigit() or int(pid) <= 0:
            raise Stop('named is not running')
        proc = '/proc/' + pid
        if run('named-executable', ['sudo', '-n', 'readlink', '-e', proc + '/exe']).strip() != b'/usr/sbin/named':
            raise Stop('unexpected process executable')
        if run('named-root', ['sudo', '-n', 'readlink', '-e', proc + '/root']).strip() != b'/':
            raise Stop('process root requires separate path review')
        if process_config(run('process-arguments-read-in-memory', ['sudo', '-n', 'cat', proc + '/cmdline'])) != ROOT_CONFIG:
            raise Stop('unexpected configuration path')

        queue = [(ROOT_CONFIG, None, 0)]
        while queue:
            path, parent, depth = queue.pop(0)
            if path in files:
                raise Stop('file included more than once or include cycle; path review required')
            if len(files) >= MAX_FILES or depth > MAX_DEPTH:
                raise Stop('include tree larger than reviewed limits')
            if not path.startswith('/'):
                raise Stop('relative include path requires review')
            if not path.startswith(ALLOWED_PREFIXES) or '/../' in path:
                raise Stop('include outside /etc or /var/named requires review')
            n = len(order)
            resolved = run(f'resolved-path-{n:02}', ['sudo', '-n', 'readlink', '-e', path]).strip().decode()
            read_path = read_path_for(path, resolved)
            st = run(f'stat-{n:02}', ['sudo', '-n', 'stat', '-Lc', '%F|%U|%G|%a|%C|%s', read_path]).decode().strip().split('|')
            if len(st) != 6 or st[0] != 'regular file' or not (0 < int(st[5]) <= MAX_BYTES):
                raise Stop('unexpected configuration file type or size')
            raw = run(f'read-in-memory-{n:02}', ['sudo', '-n', 'cat', read_path])
            if len(raw) != int(st[5]):
                raise Stop('configuration file size changed while reading')
            text = raw.decode('utf-8')
            info = analyze(text)
            masked = mask_secrets(text)
            assert_no_secret(masked)
            safe = re.sub(r'[^A-Za-z0-9._-]', '_', Path(path).name)
            masked_name = f'masked/{n:02}-{safe}'
            (out / masked_name).write_text(masked, encoding='utf-8', newline='')
            files[path] = {
                'path': path, 'resolved_path': resolved, 'included_from': parent, 'depth': depth,
                'type': st[0], 'owner': st[1], 'group': st[2], 'mode': st[3], 'selinux_context': st[4],
                'size_bytes': int(st[5]),
                'contains_secret_statement': any(k['has_secret_statement'] for k in info['key_definitions'])
                or bool(re.search(r'\bsecret\b', strip_comments(text))),
                'masked_copy': masked_name,
                'masked_sha256': hashlib.sha256(masked.encode('utf-8')).hexdigest(),
                'includes': [{'path': p, 'line': ln} for p, ln in info['includes']],
                'key_definitions': info['key_definitions'],
                'key_references': info['key_references'],
                'statements': info['statements'],
            }
            del raw, text
            order.append(path)
            for inc, ln in info['includes']:
                queue.append((inc, f'{path}:{ln}', depth + 1))

        defined = {k['name'] for f in files.values() for k in f['key_definitions']}
        referenced = {r for f in files.values() for r in f['key_references']}
        cfg = run('masked-config', ['sudo', '-n', 'named-checkconf', '-p', '-x', ROOT_CONFIG])
        try:
            _zc.safe_content(cfg)  # -x must have replaced every secret with '?'
        except _zc.Stop as exc:
            raise Stop(str(exc))
        (out / 'named.expanded.sanitized.conf').write_bytes(cfg)
        if run('named-mainpid-after', pid_cmd).strip().decode() != pid:
            raise Stop('named process changed during intake')
        structure = {
            'host': host, 'root_config': ROOT_CONFIG, 'files': [files[p] for p in order],
            'keys_defined': sorted(defined), 'keys_referenced': sorted(referenced),
            'keys_referenced_but_not_defined': sorted(referenced - defined),
            'expanded_masked_config_sha256': hashlib.sha256(cfg).hexdigest(),
            'expanded_matches_20260918_pinned_hash': hashlib.sha256(cfg).hexdigest() == _zc.EXPECTED[host][0],
            'limits': {'allowed_prefixes': list(ALLOWED_PREFIXES),
                       'allowed_crypto_policy_link': CRYPTO_POLICY_LINK,
                       'allowed_crypto_policy_target_pattern': CRYPTO_POLICY_TARGET_RE.pattern,
                       'max_files': MAX_FILES, 'max_depth': MAX_DEPTH, 'max_bytes': MAX_BYTES},
        }
        (out / 'structure.json').write_text(json.dumps(structure, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        status = {'status': 'COMPLETE_COLLECTION_ONLY', 'finished_at_kst': now(), 'files': len(order),
                  'claims_excluded': ['AC PASS', 'deployable configuration', 'secret validity', 'independent review']}
        rc = 0
    except (Stop, ValueError, UnicodeError) as exc:
        status = {'status': 'INCOMPLETE_DO_NOT_SUBMIT_AS_COMPLETE', 'finished_at_kst': now(),
                  'reason': str(exc) if isinstance(exc, Stop) else 'unexpected content or format; value suppressed'}
        rc = 1
        for p in (out / 'masked').iterdir():
            p.unlink()
    finally:
        (out / 'COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n', encoding='utf-8')
    (out / 'STATUS.json').write_text(json.dumps(status, indent=2) + '\n', encoding='utf-8')
    lines = [hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(out).as_posix()
             for p in sorted(out.rglob('*')) if p.is_file()]
    (out / 'SHA256SUMS').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(status['status'])
    print('COLLECTED_DIRECTORY=' + str(out))
    if rc:
        print(status['reason'])
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
)
MAX_FILES = 32
MAX_DEPTH = 8
MAX_BYTES = 256 * 1024
MASK = '????????'

_spec = importlib.util.spec_from_file_location(
    'zone_collector', Path(__file__).resolve().parent / 'collect_dns_zone_readonly.py')
_zc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_zc)
process_config = _zc.process_config


class Stop(Exception):
    pass


def strip_comments(text):
    """Replace comments with spaces, keeping newlines and quoted strings intact."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == '\\' else 1
            out.append(text[i:j + 1])
            i = j + 1
        elif text.startswith('/*', i):
            j = text.find('*/', i + 2)
            j = n if j < 0 else j + 2
            out.append(''.join('\n' if ch == '\n' else ' ' for ch in text[i:j]))
            i = j
        elif text.startswith('//', i) or c == '#':
            j = text.find('\n', i)
            j = n if j < 0 else j
            out.append(' ' * (j - i))
            i = j
        else:
            out.append(c)
            i += 1
    return ''.join(out)


def line_of(text, pos):
    return text.count('\n', 0, pos) + 1


def mask_secrets(text):
    return re.sub(r'(\bsecret\s+")([^"]*)(")', lambda m: m.group(1) + MASK + m.group(3), text)


def assert_no_secret(text):
    if re.search(r'-----BEGIN (?:\w+ )*PRIVATE KEY-----', text):
        raise Stop('private key material detected; value suppressed')
    for value in re.findall(r'\bsecret\s+"([^"]*)"', text):
        if value != MASK:
            raise Stop('unmasked secret remains; value suppressed')
    if re.search(r'\bsecret\s+[^"\s;]{8,}', text):
        raise Stop('unquoted secret value; value suppressed')


def analyze(text):
    """Structure of one file from comment-stripped text (secrets are not read here)."""
    s = strip_comments(text)
    includes = [(m.group(1), line_of(s, m.start())) for m in re.finditer(r'\binclude\s+"([^"]+)"\s*;', s)]
    key_defs = []
    for m in re.finditer(r'\bkey\s+"?([A-Za-z0-9._-]+)"?\s*\{', s):
        body_end = s.find('}', m.end())
        body = s[m.end():body_end if body_end > 0 else len(s)]
        alg = re.search(r'\balgorithm\s+"?([A-Za-z0-9._-]+)"?\s*;', body)
        key_defs.append({'name': m.group(1), 'line': line_of(s, m.start()),
                         'algorithm': alg.group(1) if alg else None,
                         'has_secret_statement': bool(re.search(r'\bsecret\b', body))})
    key_refs = {m.group(1) for m in re.finditer(r'\bkey\s+"?([A-Za-z0-9._-]+)"?\s*;', s)}
    for m in re.finditer(r'\bkeys\s*\{([^}]*)\}', s):
        key_refs.update(re.findall(r'"?([A-Za-z0-9._-]+)"?\s*;', m.group(1)))
    key_refs = sorted(key_refs)
    statements, depth, start = [], 0, 0
    for i, ch in enumerate(s):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth < 0:
                raise Stop('unbalanced braces')
        elif ch == ';' and depth == 0:
            head = s[start:i].strip()
            if head:
                words = head.split()
                name = words[1].strip('"') if len(words) > 1 and words[0] in ('zone', 'key', 'acl', 'view', 'masters', 'primaries') else None
                statements.append({'type': words[0], 'name': name, 'line': line_of(s, start + len(s[start:i]) - len(s[start:i].lstrip()))})
            start = i + 1
    if depth != 0:
        raise Stop('unbalanced braces')
    return {'includes': includes, 'key_definitions': key_defs, 'key_references': key_refs,
            'statements': statements}


def now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()


def main():
    os.umask(0o077)
    host = socket.gethostname().split('.')[0]
    if host not in HOSTS or os.geteuid() == 0:
        print('STOP: use the existing non-root administrator on dns01 or dns02')
        return 1
    out = Path(tempfile.mkdtemp(prefix='dns-named-structure.' + host + '.', dir=str(Path.home())))
    (out / 'masked').mkdir()
    commands = []

    def run(label, argv, allowed=(0,)):
        item = {'label': label, 'command': argv, 'started_at_kst': now(),
                'stdout': 'not saved unless listed in STATUS', 'stderr': 'suppressed; may contain sensitive diagnostics'}
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
        return result.stdout

    files, order = {}, []
    try:
        session = {'host': host, 'started_at_kst': now(), 'uid': os.getuid(),
                   'collector_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   'scope': 'read-only named.conf include structure and key references; no secrets, no DNS test'}
        (out / 'SESSION.json').write_text(json.dumps(session, indent=2) + '\n', encoding='utf-8')
        pid_cmd = ['systemctl', 'show', 'named', '--property=MainPID', '--value']
        pid = run('named-mainpid-before', pid_cmd).strip().decode('ascii')
        if not pid.isdigit() or int(pid) <= 0:
            raise Stop('named is not running')
        proc = '/proc/' + pid
        if run('named-executable', ['sudo', '-n', 'readlink', '-e', proc + '/exe']).strip() != b'/usr/sbin/named':
            raise Stop('unexpected process executable')
        if run('named-root', ['sudo', '-n', 'readlink', '-e', proc + '/root']).strip() != b'/':
            raise Stop('process root requires separate path review')
        if process_config(run('process-arguments-read-in-memory', ['sudo', '-n', 'cat', proc + '/cmdline'])) != ROOT_CONFIG:
            raise Stop('unexpected configuration path')

        queue = [(ROOT_CONFIG, None, 0)]
        while queue:
            path, parent, depth = queue.pop(0)
            if path in files:
                raise Stop('file included more than once or include cycle; path review required')
            if len(files) >= MAX_FILES or depth > MAX_DEPTH:
                raise Stop('include tree larger than reviewed limits')
            if not path.startswith('/'):
                raise Stop('relative include path requires review')
            if not path.startswith(ALLOWED_PREFIXES) or '/../' in path:
                raise Stop('include outside /etc or /var/named requires review')
            n = len(order)
            if run(f'resolved-path-{n:02}', ['sudo', '-n', 'readlink', '-e', path]).strip().decode() != path:
                raise Stop('symlinked or nonstandard configuration path requires review')
            st = run(f'stat-{n:02}', ['sudo', '-n', 'stat', '-Lc', '%F|%U|%G|%a|%C|%s', path]).decode().strip().split('|')
            if len(st) != 6 or st[0] != 'regular file' or not (0 < int(st[5]) <= MAX_BYTES):
                raise Stop('unexpected configuration file type or size')
            raw = run(f'read-in-memory-{n:02}', ['sudo', '-n', 'cat', path])
            if len(raw) != int(st[5]):
                raise Stop('configuration file size changed while reading')
            text = raw.decode('utf-8')
            info = analyze(text)
            masked = mask_secrets(text)
            assert_no_secret(masked)
            safe = re.sub(r'[^A-Za-z0-9._-]', '_', Path(path).name)
            masked_name = f'masked/{n:02}-{safe}'
            (out / masked_name).write_text(masked, encoding='utf-8', newline='')
            files[path] = {
                'path': path, 'included_from': parent, 'depth': depth,
                'type': st[0], 'owner': st[1], 'group': st[2], 'mode': st[3], 'selinux_context': st[4],
                'size_bytes': int(st[5]),
                'contains_secret_statement': any(k['has_secret_statement'] for k in info['key_definitions'])
                or bool(re.search(r'\bsecret\b', strip_comments(text))),
                'masked_copy': masked_name,
                'masked_sha256': hashlib.sha256(masked.encode('utf-8')).hexdigest(),
                'includes': [{'path': p, 'line': ln} for p, ln in info['includes']],
                'key_definitions': info['key_definitions'],
                'key_references': info['key_references'],
                'statements': info['statements'],
            }
            del raw, text
            order.append(path)
            for inc, ln in info['includes']:
                queue.append((inc, f'{path}:{ln}', depth + 1))

        defined = {k['name'] for f in files.values() for k in f['key_definitions']}
        referenced = {r for f in files.values() for r in f['key_references']}
        cfg = run('masked-config', ['sudo', '-n', 'named-checkconf', '-p', '-x', ROOT_CONFIG])
        try:
            _zc.safe_content(cfg)  # -x must have replaced every secret with '?'
        except _zc.Stop as exc:
            raise Stop(str(exc))
        (out / 'named.expanded.sanitized.conf').write_bytes(cfg)
        if run('named-mainpid-after', pid_cmd).strip().decode() != pid:
            raise Stop('named process changed during intake')
        structure = {
            'host': host, 'root_config': ROOT_CONFIG, 'files': [files[p] for p in order],
            'keys_defined': sorted(defined), 'keys_referenced': sorted(referenced),
            'keys_referenced_but_not_defined': sorted(referenced - defined),
            'expanded_masked_config_sha256': hashlib.sha256(cfg).hexdigest(),
            'expanded_matches_20260918_pinned_hash': hashlib.sha256(cfg).hexdigest() == _zc.EXPECTED[host][0],
            'limits': {'allowed_prefixes': list(ALLOWED_PREFIXES), 'max_files': MAX_FILES, 'max_depth': MAX_DEPTH,
                       'max_bytes': MAX_BYTES},
        }
        (out / 'structure.json').write_text(json.dumps(structure, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        status = {'status': 'COMPLETE_COLLECTION_ONLY', 'finished_at_kst': now(), 'files': len(order),
                  'claims_excluded': ['AC PASS', 'deployable configuration', 'secret validity', 'independent review']}
        rc = 0
    except (Stop, ValueError, UnicodeError) as exc:
        status = {'status': 'INCOMPLETE_DO_NOT_SUBMIT_AS_COMPLETE', 'finished_at_kst': now(),
                  'reason': str(exc) if isinstance(exc, Stop) else 'unexpected content or format; value suppressed'}
        rc = 1
        for p in (out / 'masked').iterdir():
            p.unlink()
    finally:
        (out / 'COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n', encoding='utf-8')
    (out / 'STATUS.json').write_text(json.dumps(status, indent=2) + '\n', encoding='utf-8')
    lines = [hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(out).as_posix()
             for p in sorted(out.rglob('*')) if p.is_file()]
    (out / 'SHA256SUMS').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(status['status'])
    print('COLLECTED_DIRECTORY=' + str(out))
    if rc:
        print(status['reason'])
    return rc


if __name__ == '__main__':
    raise SystemExit(main())

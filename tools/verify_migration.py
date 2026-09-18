#!/usr/bin/env python3
"""Verify imported bytes and narrowly scoped credential patterns; no network/runtime."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    errors = []
    manifest = json.loads((ROOT / 'docs/MIGRATION_MANIFEST.json').read_text(encoding='utf-8'))
    seen = set()
    for entry in manifest['files']:
        name = entry['destination']
        rel = PurePosixPath(name)
        if rel.is_absolute() or '..' in rel.parts or '\\' in name or name in seen:
            errors.append(f'Unsafe or duplicate manifest path: {name}')
            continue
        seen.add(name)
        path = ROOT / name
        if path.is_symlink() or not path.is_file():
            errors.append(f'Missing or non-regular imported file: {name}')
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry['destination_sha256']:
            errors.append(f'Imported content changed: {name}')
    actual = {p.relative_to(ROOT).as_posix() for directory in ('runbooks', 'references')
              for p in (ROOT / directory).rglob('*') if p.is_file()}
    if actual != seen:
        errors.append(f'Imported inventory mismatch: {sorted(actual ^ seen)}')

    # Heuristic only: a clean result is not proof that all secrets are absent.
    patterns = [
        re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----'),
        re.compile(r'(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}'),
        re.compile(r'\bsecret\s+"[A-Za-z0-9+/=]{16,}"'),
    ]
    checked = 0
    for p in ROOT.rglob('*'):
        rel = p.relative_to(ROOT)
        if not p.is_file() or '.git' in rel.parts or '__pycache__' in rel.parts:
            continue
        if p.suffix in {'.key', '.p12', '.pfx', '.zip'} or p.name == '.env':
            errors.append(f'Unexpected sensitive/binary artifact: {rel.as_posix()}')
            continue
        try:
            content = p.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            errors.append(f'Unexpected non-UTF-8 file: {rel.as_posix()}')
            continue
        checked += 1
        for number, line in enumerate(content.splitlines(), 1):
            if any(pattern.search(line) for pattern in patterns):
                errors.append(f'Possible credential at {rel.as_posix()}:{number} (value suppressed)')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'PASS: {len(seen)} imported files; {checked} UTF-8 source files; scoped credential patterns absent')
    print('STATIC only. No runtime, independent review, merge, or publication is asserted.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

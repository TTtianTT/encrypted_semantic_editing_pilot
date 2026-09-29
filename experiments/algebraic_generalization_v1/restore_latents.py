"""Restore the two lossless latent tensor files from GitHub-size archive parts."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE / 'latents_archive'


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    if not shutil.which('zstd'):
        raise SystemExit('zstd command is required to restore the latent tensors')
    manifest = json.loads((ARCHIVE / 'manifest.json').read_text())
    for name, entry in manifest['files'].items():
        target = HERE / name
        if target.exists():
            if target.stat().st_size != entry['size'] or sha256(target) != entry['sha256']:
                raise SystemExit(f'{target} exists but fails the manifest; move it aside before restoring')
            print('verified existing', target)
            continue
        parts = [ARCHIVE / p['name'] for p in entry['parts']]
        for path, part in zip(parts, entry['parts']):
            if path.stat().st_size != part['size'] or sha256(path) != part['sha256']:
                raise SystemExit(f'archive part failed checksum: {path}')
        temporary = target.with_suffix(target.suffix + '.tmp')
        try:
            with temporary.open('wb') as output:
                proc = subprocess.Popen(['zstd', '-d', '-q', '-c'], stdin=subprocess.PIPE, stdout=output)
                try:
                    for path in parts:
                        with path.open('rb') as stream:
                            shutil.copyfileobj(stream, proc.stdin, length=8 * 1024 * 1024)
                finally:
                    proc.stdin.close()
                if proc.wait() != 0:
                    raise RuntimeError('zstd decompression failed')
            if temporary.stat().st_size != entry['size'] or sha256(temporary) != entry['sha256']:
                raise RuntimeError(f'restored checksum failed: {name}')
            temporary.replace(target)
            print('restored', target)
        finally:
            temporary.unlink(missing_ok=True)


if __name__ == '__main__':
    main()

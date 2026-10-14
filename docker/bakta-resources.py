#!/opt/conda/bin/python3
"""Explicit, immutable Bakta DB 6.0 + AMRFinder 4.2 snapshot installation."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
from urllib.parse import urljoin

SHARE = Path('/opt/taffish/bakta')
AMR = SHARE / 'amr-inputs.json'
SCHEMA = 'taffish.bakta.database.v1'
IDENTITY = '6.0-amr2026-08-07.1'
DATABASES = {
    'light': dict(filename='db-light.tar.xz', md5='4a6e059ded39e9c5537ef4137d2f5648',
                  size=1344199496, unpack_budget=5*1024**3, top='db-light'),
    'full': dict(filename='db.tar.xz', md5='4c1115e40abfa2b464ae5dd988bdd88e',
                 size=31921769288, unpack_budget=100*1024**3, top='db'),
}
LICENSE = '''Bakta DB 6.0: CC-BY-4.0, Oliver Schwengers (2025).
https://doi.org/10.5281/zenodo.14916843
https://creativecommons.org/licenses/by/4.0/
AMRFinderPlus database: NCBI United States Government Work, public domain notice:
https://github.com/ncbi/amr/blob/amrfinder_v4.2.7/amrfinder_update.cpp
Data files are not scientifically modified. AMRFinder indexes are generated locally.
Retain database attribution and original constituent database notices in downstream work.
'''

def require(ok, message):
    if not ok:
        raise ValueError(message)

def digest(path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(4*1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))+'\n'

def safe_name(value):
    parts = PurePosixPath(value).parts
    require(parts and not PurePosixPath(value).is_absolute() and '..' not in parts
            and all(re.fullmatch(r'[A-Za-z0-9_.+-]+', p) for p in parts), 'unsafe resource path: '+value)
    return parts

def regular(path):
    require(not path.is_symlink() and stat.S_ISREG(path.lstat().st_mode), 'expected regular file: '+str(path))

def selection(kind):
    item = dict(DATABASES[kind], name=DATABASES[kind]['filename'], algorithm='md5', license='CC-BY-4.0')
    item['checksum'] = item['md5']
    item['url'] = 'https://zenodo.org/records/14916843/files/'+item['filename']
    amr = json.loads(AMR.read_text())
    require(amr['version'] == '2026-08-07.1' and amr['software_series'] == '4.2', 'wrong AMR catalog')
    files = [dict(r, checksum=r['sha256'], algorithm='sha256') for r in amr['files']]
    return dict(schema=SCHEMA, identity=IDENTITY, type=kind, database=item, amrfinder=amr, inputs=[item, *files])

def run(stage, args):
    print('bakta-resources: '+stage, file=sys.stderr, flush=True)
    with tempfile.TemporaryFile() as log:
        result = subprocess.run(args, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            log.seek(max(0, log.tell()-32768))
            print('bakta-resources stage='+stage+'\n'+log.read().decode(errors='replace'), file=sys.stderr)
            raise RuntimeError(stage+' failed (exit '+str(result.returncode)+')')

def private_dir(path):
    if not path.exists():
        path.mkdir(mode=0o700)
    require(not path.is_symlink() and path.is_dir() and path.stat().st_uid == os.geteuid()
            and stat.S_IMODE(path.stat().st_mode) == 0o700, 'cache must be owned/private 0700: '+str(path))

def obtain(item, cache, source_dir):
    print('bakta-resources: prepare '+item['name'], file=sys.stderr, flush=True)
    blob = cache/item['checksum']
    part = cache/(item['checksum']+'.part')
    for p in (blob, part):
        if os.path.lexists(p):
            regular(p)
    if blob.exists():
        require(blob.stat().st_size == item['size'] and digest(blob, item['algorithm']) == item['checksum'],
                'corrupt completed cache; no automatic replacement: '+str(blob))
        return blob
    if source_dir:
        source = source_dir/item['name']
        regular(source)
        require(not part.exists(), 'partial cache exists; use network resume or inspect/remove this exact partial: '+str(part))
        with source.open('rb') as inp, part.open('xb') as out:
            shutil.copyfileobj(inp, out)
    else:
        # 固定 HTTPS 输入仍可能下架；Range 不可用时保留 partial 并明确失败，不静默换源。
        import requests
        for attempt in range(3):
            offset = part.stat().st_size if part.exists() else 0
            if offset == item['size']:
                break
            require(offset < item['size'], 'oversized partial cache: '+str(part))
            try:
                url = item['url']
                response = None
                for redirect in range(6):
                    require(url.startswith('https://'), 'HTTPS downgrade rejected')
                    response = requests.get(url, headers={'Range': f'bytes={offset}-'} if offset else {},
                                            stream=True, timeout=(30, 120), allow_redirects=False)
                    if response.status_code not in (301,302,303,307,308):
                        break
                    url = urljoin(url, response.headers.get('Location', ''))
                    response.close()
                else:
                    raise ValueError('too many redirects')
                with response:
                    response.raise_for_status()
                    require(response.url.startswith('https://'), 'HTTPS downgrade rejected')
                    if offset:
                        require(response.status_code == 206 and response.headers.get('Content-Range', '').startswith(f'bytes {offset}-'),
                                'server did not honor resume; partial retained: '+str(part))
                    else:
                        require(response.status_code == 200, 'unexpected initial download response')
                    with part.open('ab' if part.exists() else 'xb') as out:
                        received = offset
                        last_report = offset
                        for block in response.iter_content(4*1024*1024):
                            out.write(block)
                            received += len(block)
                            if received-last_report >= 64*1024*1024:
                                print(f"bakta-resources: {item['name']} {received}/{item['size']} bytes", file=sys.stderr, flush=True)
                                last_report = received
                break
            except requests.RequestException:
                if attempt == 2:
                    raise
    require(part.stat().st_size == item['size'] and digest(part, item['algorithm']) == item['checksum'],
            'input size/checksum mismatch; fail closed; inspect/remove exact partial: '+str(part))
    part.chmod(0o600)
    part.rename(blob)
    return blob

def unpack(blob, stage, expected_top, reserve):
    print('bakta-resources: inspect and extract verified database archive', file=sys.stderr, flush=True)
    with tarfile.open(blob, 'r:xz') as archive:
        members = archive.getmembers()
        require(shutil.disk_usage(stage).free > sum(m.size for m in members)+reserve, 'insufficient extraction space')
        seen = set()
        for member in members:
            parts = PurePosixPath(member.name).parts
            require(parts and parts[0] == expected_top, 'unexpected archive root')
            if len(parts) == 1:
                require(member.isdir(), 'archive root must be directory')
                continue
            parts = safe_name('/'.join(parts[1:]))
            name = '/'.join(parts)
            require(name not in seen, 'duplicate archive member: '+name)
            seen.add(name)
            # 官方 DB 6.0 归档带旧 AMR 2024-12-18.1 和 latest 相对链接。
            # 本资源明确组合固定 4.2/2026-08-07.1；旧 expert 子树不安装，
            # 随后按独立 SHA256 输入重建，不跟随归档链接，也不改 Bakta DB。
            if parts[0] == 'amrfinderplus-db':
                require(member.isfile() or member.isdir() or
                        (name == 'amrfinderplus-db/latest' and member.issym() and
                         re.fullmatch(r'\d{4}-\d{2}-\d{2}\.\d+', member.linkname)),
                        'unsafe legacy AMR archive entry: '+name)
                continue
            require(member.isfile() or member.isdir(), 'archive links/devices forbidden: '+name)
            out = stage.joinpath(*parts)
            if member.isdir():
                out.mkdir(parents=True, exist_ok=True)
            else:
                out.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as inp, out.open('xb') as stream:
                    shutil.copyfileobj(inp, stream)

def inventory(root):
    files = {}
    for p in sorted(root.rglob('*')):
        require(not p.is_symlink(), 'resource symlink forbidden: '+str(p))
        require(not p.stat().st_mode & 0o022, 'group/world writable resource: '+str(p))
        if p.is_dir():
            continue
        regular(p)
        name = p.relative_to(root).as_posix()
        safe_name(name)
        if name not in ('manifest.json', 'READY', 'FILES'):
            files[name] = dict(size=p.stat().st_size, sha256=digest(p))
    return files

def verify(root, full=True):
    root = Path(root)
    require(root.is_dir() and not root.is_symlink() and not root.stat().st_mode & 0o022, 'invalid physical database root')
    for name in ('READY','manifest.json','FILES'):
        regular(root/name)
    expected = digest(root/'manifest.json')+' '+digest(root/'FILES')
    require((root/'READY').read_text().strip() == expected, 'READY/manifest/inventory mismatch')
    record = json.loads((root/'manifest.json').read_text())
    require(record['schema'] == SCHEMA and record['identity'] == IDENTITY and record['type'] in DATABASES, 'wrong database identity')
    require(record['selection'] == selection(record['type']), 'database selection differs from this release')
    require((root/'FILES').read_text() == ''.join(f"{r['size']} {name}\n" for name, r in sorted(record['files'].items())), 'inventory mismatch')
    for name, entry in record['files'].items():
        p = root.joinpath(*safe_name(name))
        regular(p)
        require(p.stat().st_size == entry['size'], 'size mismatch: '+name)
    if full:
        require(inventory(root) == record['files'], 'database integrity mismatch')
    return record

def install(root, selected, source_dir=None, reserve=1024**3):
    root = Path(root).absolute()
    require(root.parent.is_dir() and root.parent.resolve() == root.parent, 'create a physical parent directory first')
    require(not root.parent.stat().st_mode & 0o022, 'parent must not be group/world writable')
    require(not root.is_symlink(), 'destination must not be a symlink')
    lock = root.parent/('.'+root.name+'.lock')
    fd = os.open(lock, os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW, 0o600)
    require(os.fstat(fd).st_uid == os.geteuid() and stat.S_IMODE(os.fstat(fd).st_mode) == 0o600, 'unsafe install lock')
    stage = None
    with os.fdopen(fd, 'w') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX|fcntl.LOCK_NB)
        if root.exists():
            record = verify(root)
            require(record['selection'] == selected, 'immutable root has another selection; choose a new --db-root')
            print('already verified: '+str(root))
            return
        cache = root.parent/('.'+root.name+'.cache')
        private_dir(cache)
        needed = sum(i['size'] for i in selected['inputs'] if not (cache/i['checksum']).exists())
        require(shutil.disk_usage(root.parent).free > needed+selected['database']['unpack_budget']+1024**3+reserve,
                'insufficient disk space for download, extraction, AMR indexes and reserve')
        try:
            stage = Path(tempfile.mkdtemp(prefix='.'+root.name+'.stage-', dir=root.parent))
            blob = obtain(selected['database'], cache, source_dir)
            unpack(blob, stage, selected['database']['top'], reserve)
            info = json.loads((stage/'version.json').read_text())
            require((info['major'],info['minor'],info['type']) == (6,0,selected['type']), 'wrong extracted database identity')
            amr = stage/'amrfinderplus-db'/'latest'
            amr.mkdir(parents=True)
            for item in selected['inputs'][1:]:
                shutil.copyfile(obtain(item, cache, source_dir), amr/item['name'])
            require((amr/'version.txt').read_text().strip() == '2026-08-07.1', 'wrong AMR version')
            run('amrfinder-index', ['amrfinder_index', str(amr)])
            run('amrfinder-verify', ['amrfinder', '--database', str(amr), '--database_version'])
            (stage/'RESOURCE_LICENSE.txt').write_text(LICENSE)
            for p in stage.rglob('*'):
                p.chmod(0o755 if p.is_dir() else 0o644)
            files = inventory(stage)
            record = dict(schema=SCHEMA, identity=IDENTITY, type=selected['type'], selection=selected,
                          files=files, archive_sha256=digest(blob))
            (stage/'manifest.json').write_text(canonical(record))
            (stage/'FILES').write_text(''.join(f"{r['size']} {name}\n" for name,r in sorted(files.items())))
            (stage/'READY').write_text(digest(stage/'manifest.json')+' '+digest(stage/'FILES')+'\n')
            for name in ('manifest.json','FILES','READY'):
                (stage/name).chmod(0o644)
            stage.chmod(0o755)
            verify(stage)
            require(not os.path.lexists(root), 'destination appeared during installation')
            stage.rename(root)
            stage = None
            print('installed, indexed and verified: '+str(root))
        finally:
            if stage is not None:
                shutil.rmtree(stage)

def main():
    parser = argparse.ArgumentParser(description='Install immutable Bakta DB 6.0 with pinned AMRFinder 2026-08-07.1. No latest lookup, no overwrite.')
    parser.add_argument('--db-root', type=Path, required=True)
    parser.add_argument('--type', choices=['light','full'], help='explicit scientific selection; required for installation')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--verify', action='store_true', help='full checksum audit; does not need write access or network')
    parser.add_argument('--source-dir', type=Path, help='import exact official inputs by filename from this directory')
    parser.add_argument('--reserve-gib', type=float, default=1)
    args = parser.parse_args()
    try:
        require(args.reserve_gib >= 1, 'reserve must be at least 1 GiB')
        if args.verify:
            record = verify(args.db_root)
            print('verified '+record['identity']+' '+record['type'])
        else:
            require(args.type is not None, 'select --type light or full explicitly')
            selected = selection(args.type)
            if args.dry_run:
                print(json.dumps(dict(db_root=str(args.db_root), selection=selected, license=LICENSE,
                    overwrite='refused; use a new versioned root for repair; retain old root until verified',
                    recovery='retry reuses verified cache and HTTPS partials; corrupt cache fails closed'), indent=2))
            else:
                os.umask(0o022)
                install(args.db_root, selected, args.source_dir, int(args.reserve_gib*1024**3))
    except Exception as error:
        print('bakta-resources: '+str(error), file=sys.stderr)
        return 2
    return 0

if __name__ == '__main__':
    sys.exit(main())

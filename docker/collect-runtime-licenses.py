"""瘦身前保留官方基底携带的许可原文；不以 license 名称替代原文。"""
import importlib.metadata
import json
from pathlib import Path
import shutil

prefix=Path('/opt/conda')
dest=Path('/usr/local/share/licenses/bakta-runtime')
dest.mkdir(parents=True,exist_ok=True)
records=[]
for package in sorted((prefix/'pkgs').iterdir()):
    if not package.is_dir():
        continue
    info=package/'info'
    licenses=info/'licenses'
    if licenses.is_dir():
        shutil.copytree(licenses,dest/'conda'/package.name/'licenses',dirs_exist_ok=True)
        for name in ('index.json','about.json'):
            if (info/name).is_file():shutil.copyfile(info/name,dest/'conda'/package.name/name)
        records.append(dict(package=package.name,kind='conda-cache',files=[str(p.relative_to(dest)) for p in (dest/'conda'/package.name).rglob('*') if p.is_file()]))
for package in importlib.metadata.distributions():
    files=[]
    for item in package.files or ():
        if item.parts and '.dist-info' in item.parts[0] and any(x in str(item).lower() for x in ('license','copying','notice')):
            src=Path(package.locate_file(item))
            if src.is_file():
                target=dest/'python'/str(item)
                target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
                files.append(str(target.relative_to(dest)))
    records.append(dict(package=package.metadata['Name'],version=package.version,kind='python',files=files))
shutil.copytree(prefix/'conda-meta',dest/'conda-installed-metadata',dirs_exist_ok=True)
(dest/'inventory.json').write_text(json.dumps(records,indent=2)+'\n')
assert any(r['kind']=='conda-cache' and r['files'] for r in records)
print('retained license records:',len(records))

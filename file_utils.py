#!/usr/bin/env python3

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED
import os
from datetime import datetime
from dataclasses import dataclass, asdict
import json


# There is a lot of root and path here. I guess I'm trying to keep the
# file operations sandboxed somehow, only using absolute paths internally,
# whereas the web interface only uses relative paths (to CFD_HOME e.g.).

tfmt = '%Y-%m-%d %H:%M:%S'


@dataclass
class file_info:
    name: str
    path: Path
    file_size: int
    mtime: int
    last_modified: datetime
    file_type: str

    def asdict(self):
        return asdict(self)

    def asjson(self):
        return json.dumps(self.asdict(), indent=4, default=str)

    def mtime_str(self):
        return self.last_modified.strftime(tfmt)

    def __repr__(self):
        return self.asjson()


def get_dir_size(path: Path, scale: int = 1024**2):
    total = 0
    for entry in path.iterdir():
        if entry.is_file():
            total += entry.stat().st_size/scale
        elif entry.is_dir():
            total += get_dir_size(entry)
    return total


def list_directory(root: Path, path: Path) -> dict:
    content = {'dirs': [], 'files': []}
    for item in Path(root, path).iterdir():
        f_info = f_stat(root, item.relative_to(root))
        if f_info:
            if item.is_dir():
                content['dirs'].append(f_info)
            else:
                content['files'].append(f_info)
    return content


def list_directory_as_dicts(root: Path, path: Path) -> dict:
    content = list_directory(root, path)
    dictified = [v.asdict() for v in content['dirs']]
    dictified+= [v.asdict() for v in content['files']]
    asjson = json.dumps(dictified, default=str)
    dictified = json.loads(asjson)
    return dictified


def f_stat(root: Path, path: Path) -> dict:
    abs_path = Path(root, path)
    mtime = abs_path.stat().st_mtime
    if abs_path.is_dir():
        size = get_dir_size(abs_path)
        file_type = 'directory'
    elif abs_path.is_file():
        size = abs_path.stat().st_size
        file_type = path.suffix
    else:
        return None
    f_info = file_info(path=path,
                       name=abs_path.name,
                       mtime=mtime,
                       last_modified=datetime.fromtimestamp(mtime),
                       file_size=int(size),
                       file_type=file_type)
    return f_info


def find_openfoam_cases(root: Path):
    root = Path(root)
    if not os.access(root, os.R_OK):
        return f'{root} is not readable.'
    for item in root.rglob('*'):
        if item.is_file() and item.name == 'controlDict':
            case_path = item.parent.parent
            try:
                relative_root = case_path.relative_to(root)
            except ValueError:
                continue
            yield f_stat(root, relative_root)


def zip_directory(case_path: Path, target_file: Path):
    files = [f for f in case_path.rglob('*') if f.is_file()]
    if files and generate_zip(files, target_file, compress=False):
        return target_file
    return None


def generate_zip(files: list, zip_file: str, compress=False):
    comp = ZIP_DEFLATED if compress else ZIP_STORED
    try:
        with ZipFile(zip_file, mode="w", compression=comp) as zf:
            for f in files:
                if Path(f).exists():
                    zf.write(f)
    except Exception:
        return False
    return True


if __name__ == '__main__':
    import sys
    root = sys.argv[1]
    cases = find_openfoam_cases(root)
    for cas in cases:
        print(cas)
        print(cas.path)

    contents = list_directory_as_dicts(root,'')
    print(json.dumps(contents, default=str, indent=2))

#!/usr/bin/env python3

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED
import os
import sys
from datetime import datetime


tfmt = '%Y-%m-%d %H:%M:%S'


def get_dir_size(path='.'):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total/1024**2


def list_directory(root: Path) -> dict:
    content = {'dirs': [], 'files': []}
    for item in root.iterdir():
        if item.is_dir():
            content['dirs'].append(item.name)
        else:
            content['files'].append(item.name)
    return content


def find_openfoam_cases(root: Path):
    try:
        root = Path(root)
    except TypeError:
        return "Failed to assign root"
    if not os.access(root, os.R_OK):
        return f'{root} is not readable.'
    for item in root.rglob('*'):
        if item.is_file() and item.name == 'controlDict':
            case_root = item.parent.parent
            mtime = item.stat().st_mtime
            dir_size = get_dir_size(item.parent.parent)
            yield {'path': case_root,
                   'name': case_root.name,
                   'mtime': mtime,
                   'time_str': datetime.fromtimestamp(mtime).strftime(tfmt),
                   'size': int(dir_size)}


def zip_directory(case_root: Path):
    files = [f for f in case_root.rglob('*') if f.is_file()]
    zip_file_name = Path('/tmp', case_root.with_suffix('.zip').name)
    if files and generate_zip(files, zip_file_name, compress = False):
        return zip_file_name
    return None


def generate_zip(files: list, zip_file: str, compress=False):
    comp = ZIP_DEFLATED if compress else ZIP_STORED
    try:
        with ZipFile(zip_file, mode="w", compression=comp) as zf:
            for f in files:
                if Path(f).exists():
                    zf.write(f)
    except Exception as e:
        return False
    return True

if __name__ == '__main__':
    import sys
    # for cfd_case in find_openfoam_cases('/home/cfd/cfd_run'):
    #     cdir = Path(cfd_case['path'])
    #     zip_directory(cdir)
    cases = find_openfoam_cases('/home/cfd/cfd_run')


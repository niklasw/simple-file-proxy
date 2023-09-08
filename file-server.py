#!/usr/bin/env python3

from file_utils import find_openfoam_cases, list_directory, zip_directory

from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, render_template, request,\
    send_from_directory, abort
from werkzeug.utils import secure_filename
from pathlib import Path
import json
import os
import sys
import getpass


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = Path(f'/tmp/{getpass.getuser()}/uploads')
app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)
app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1, x_prefix=1)

@app.route('/')
def test():
    return "Hello world!"

@app.route('/cfd-vm-0')
def tests():
    return "Hello WORLD!"

@app.route('/upload/<path:file_name>')
def upload(file_name):
    return render_template('upload.html', file_name=secure_filename(file_name))


@app.route('/explore/')
def explore():
    root_path = Path(os.getenv('CFD_HOME'))
    all_cases = list(find_openfoam_cases(root_path))
    all_cases.sort(key=lambda t: t.mtime, reverse=True)
    response_str = 'Case directories on the CFD server'
    return render_template('explore.html',
                           header=response_str,
                           dir_info_list=all_cases)


def safe_path(root: Path, path: Path):
    try:  # Protect against access outside of root
        (root/path).resolve().relative_to(root)
        return True
    except Exception:
        return False


@app.route('/explore/<path:case_path>')
def explorer(case_path):
    root_path = Path(os.getenv('CFD_HOME'))
    case_path = Path(case_path)
    if not safe_path(root_path, case_path):
        abort(404)
    if Path(root_path, case_path).is_file():
        try:
            content = Path(root_path, case_path).open('rb').read().decode()
        except ValueError:
            content = 'Binary data file'
        return render_template('file.html',
                               header=case_path.name,
                               file_name=case_path.name,
                               message=content)
    content = list_directory(root_path, case_path)
    return render_template('explore.html',
                           header=case_path,
                           parent=case_path.parent,
                           dir_info_list=content.get('dirs'),
                           file_info_list=content.get('files'))


@app.route('/download/<path:case_path>')
def download(case_path):
    root_path = Path(os.getenv('CFD_HOME'))
    case_path = Path(case_path)
    file_path = Path(root_path, case_path)
    dl_name = request.args.get('dl') or 'download.zip'
    if file_path.is_file():
        return send_from_directory(root_path, case_path)
    elif file_path.is_dir():
        target_file = app.config['UPLOAD_FOLDER']/dl_name
        if zip_directory(file_path, target_file):
            return send_from_directory(app.config['UPLOAD_FOLDER'], dl_name)
    return abort(404)


@app.route('/transfer/<path:file_name>', methods=['GET', 'POST'])
def file_transfer(file_name):
    """Post or get file using Flask methods"""
    target_folder = app.config['UPLOAD_FOLDER']
    if request.method == 'POST':
        if 'file' in request.files:
            f = request.files['file']
            f.save(Path(target_folder, secure_filename(file_name)))
    elif request.method == 'GET':
        if Path(target_folder, file_name).exists():
            return send_from_directory(target_folder, file_name)
        else:
            return json.dumps({'exit': 404,
                               'message': 'File not found on server.'})
    return request.headers.__repr__()


@app.route('/rw/<path:file_name>', methods=['GET', 'POST'])
def file_transfer_test(file_name):
    """Post or get file avoiding Flask methods"""
    target_folder = app.config['UPLOAD_FOLDER']
    target_file = Path(target_folder, secure_filename(file_name))
    if request.method == 'POST':
        if request.data:
            with target_file.open('wb') as f:
                f.write(request.data)
    elif request.method == 'GET':
        if target_file.exists():
            with target_file.open('rb') as f:
                return f.read()
        else:
            return json.dumps({'exit': 404,
                               'message': 'File not found on server.'})
    return request.headers.__repr__()


def log():
    log_dir = Path(Path.cwd(), 'logs')
    if not log_dir.exists():
        log_dir.mkdir()
    with Path(log_dir, 'PID').open('w') as f:
        f.write(str(os.getpid()))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except TypeError as e:
            print('Argument must be a port number')
            print(e)
            sys.exit(1)
    else:
        port = 5000
    log()
    app.run(debug=True, host='0.0.0.0', port=port)

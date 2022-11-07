#!/usr/bin/env python3

from flask import Flask, render_template, request,\
    send_file, send_from_directory, abort
from werkzeug.utils import secure_filename
from pathlib import Path
import json
import os
import sys


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/flask-blob/uploads'
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)


@app.route('/upload/<path:file_name>')
def upload(file_name):
    return render_template('upload.html', file_name=secure_filename(file_name))


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
            abort(404)
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
            port=int(sys.argv[1])
        except TypeError as e:
            print('Argument must be a port number')
            print(e)
            sys.exit(1)
    else:
        port = 5000
    log()
    app.run(debug=True, port=port)

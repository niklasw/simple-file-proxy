#!/usr/bin/env python3

from flask import Flask, render_template, request,\
    send_file, send_from_directory, abort
from werkzeug.utils import secure_filename
from pathlib import Path
import sys

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/flask-blob/uploads'


Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)


@app.route('/upload/<path:file_name>')
def upload(file_name):
    return render_template('upload.html', file_name=secure_filename(file_name))


@app.route('/transfer/<path:file_name>', methods = ['GET', 'POST'])
def file_transfer(file_name):
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



@app.route('/data/<path:file_name>', methods = ['GET', 'POST'])
def file_transfer_test(file_name):
    target_folder = app.config['UPLOAD_FOLDER']
    target_file = Path(target_folder, secure_filename(file_name))
    if request.method == 'POST':
        if request.data:
            with target_file.open('wb') as f:
                f.write(data)
    elif request.method == 'GET':
        if target_file.exists():
            with target_file.open('rb') as f:
                send_file(f)
        else:
            abort(404)
    return request.headers.__repr__()


if __name__ == '__main__':
    app.run(debug = True)

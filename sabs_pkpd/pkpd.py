"""Main page for running analysis.
"""

import os
from flask import Blueprint, render_template, request, current_app, flash, redirect
from werkzeug.utils import secure_filename

bp = Blueprint('pkpd', __name__)

user_config_settings = {}

@bp.route('/')
def index():
    return render_template('pkpd/index.html', settings=user_config_settings)

@bp.route('/', methods=['GET', 'POST'])
def get_user_settings():
    if request.method == 'POST':
        if 'options' in request.form:
            option = request.form['options']
            user_config_settings['model_version'] = option
            return render_template('pkpd/index.html', settings=user_config_settings)

    if request.method == 'POST':

        if 'file' in request.files:

            file = request.files['file']

            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            #return redirect(url_for('uploaded_file', filename=filename))

            user_config_settings['data_file'] = filename
            print(user_config_settings)

            return render_template('pkpd/index.html', settings=user_config_settings)

    return render_template('pkpd/index.html', settings=user_config_settings)

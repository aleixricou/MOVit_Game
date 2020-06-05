from flask import Blueprint, current_app, request, render_template, send_file
from jinja2 import TemplateNotFound
from flask_babelex import Babel, _, lazy_gettext
from flask_security import current_user

babel=Babel()
idi=None
babel_blueprint = Blueprint('babel', __name__, template_folder='templates')

@babel.localeselector
def get_locale():
    if idi == None:
        return request.accept_languages.best_match(['es','en','ca'])
    elif idi == 'en':
        return 'en'
    elif idi == 'es':
        return 'es'
    else:
        return 'ca'

@babel_blueprint.route('/home', methods=['POST'])
def idioma():
    global idi
    idi=request.form['idioma']
    return render_template('dashboard.html')

@babel_blueprint.route('/home_terap', methods=['POST'])
def idioma2():
    global idi
    idi=request.form['idioma']
    return render_template('dashboard_terap.html')

@babel_blueprint.route('/home_admin', methods=['POST'])
def idioma3():
    global idi
    idi=request.form['idioma']
    return render_template('admin.html')  



"""
Blueprint de management
"""
import io
import os

from flask import Blueprint, current_app, request, render_template, send_file
from jinja2 import TemplateNotFound
from .models import User, Partida
from .basedades import BASEDADES as db
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from io import BytesIO
import pandas as pd
from sqlalchemy import desc


management_blueprint = Blueprint('management', __name__, template_folder='templates')
    

@management_blueprint.route('/info')
def mostrar_template ():
    return render_template('info.html')

@management_blueprint.route('/ranking')
def mostrar_template_ranking ():
    users=Partida.query.order_by(desc(Partida.total_points)).filter_by(current=False).all()
    s=1
    for i in users:
        i.rank=s
        s=s+1
    db.session.commit()
    return render_template('ranking.html',users=users)

@management_blueprint.route('/fites')
def mostrar_template_milestones():
    return render_template('milestones.html')

@management_blueprint.route('/contact')
def mostrar_info_contact():
    return render_template('contact.html')


@management_blueprint.route('/idioma')
def canvi_idioma():
    return render_template('idioma.html')


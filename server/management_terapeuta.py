import jsonify
import io
import json

from flask import Blueprint, current_app, request, render_template, send_file
from jinja2 import TemplateNotFound
from .models import User, Cientific, Role, Partida
from .basedades import BASEDADES as db
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, login_required, roles_accepted
from flask_babelex import Babel
from io import BytesIO
import pandas as pd
from flask_login import current_user
from sqlalchemy import desc
from flask_mail import Mail, Message
from .babel import babel, babel_blueprint, get_locale


cientific_datastore = SQLAlchemyUserDatastore(db, Cientific, Role)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)


management_t_blueprint = Blueprint('management_terapeuta', __name__, template_folder='templates')

#Llistat d'usuaris
@management_t_blueprint.route('/all_users')
@login_required
@roles_accepted('therapist')
def show_users_results():
    users = current_user.posts
    return render_template('users.html',users=users)

@management_t_blueprint.route('/download_users')
@login_required
@roles_accepted('therapist')
def download_users():
    users=current_user.posts
    idi=get_locale()
    if idi == 'es':
        d={'Nombre':[],'E-Mail':[],'Número de partidas jugadas':[],'Dificultad':[],'Última partida':[],'Registrado':[]}
        for user in users:
            d['Nombre'].append(user.nom)
            d['E-Mail'].append(user.email)
            d['Número de partidas jugadas'].append(user.num_partides)
            d['Dificultad'].append(user.dificulty)
            d['Última partida'].append(user.last_partida)
            d['Registrado'].append(user.registrat)
    elif idi == 'ca':
        d={'Nom':[],'E-Mail':[],'Nombre de partides jugades':[],'Dificultat':[],'Última partida':[],'Registrat':[]}
        for user in users:
            d['Nom'].append(user.nom)
            d['E-Mail'].append(user.email)
            d['Nombre de partides jugades'].append(user.num_partides)
            d['Dificultat'].append(user.dificulty)
            d['Última partida'].append(user.last_partida)
            d['Registrat'].append(user.registrat)
    else:
        d={'Name':[],'E-Mail':[],'Number of player\'s matches':[],'Difficulty':[],'Last match':[],'Registered':[]}
        for user in users:
            d['Name'].append(user.nom)
            d['E-Mail'].append(user.email)
            d['Number of player\'s matches'].append(user.num_partides)
            d['Difficulty'].append(user.dificulty)
            d['Last match'].append(user.last_partida)
            d['Registered'].append(user.registrat)
        
    df = pd.DataFrame(data=d)  
    strIO = io.BytesIO()
    writer = pd.ExcelWriter(strIO, engine="xlsxwriter")
    df.to_excel(writer, sheet_name='Jugadores', index=False)
    workbook = writer.book
    worksheet = writer.sheets['Jugadores']        
    for i, col in enumerate(df.columns):
        column_len = df[col].astype(str).str.len().max()
        column_len = max(column_len, len(col)) + 2
        worksheet.set_column(i, i, column_len)
    writer.save()
    excel_data = strIO.getvalue()
    strIO.seek(0)
    return send_file(strIO,
                     attachment_filename='jugadores.xlsx',
                     as_attachment=True)

@management_t_blueprint.route('/download_partides', methods=['POST'])
@login_required
@roles_accepted('therapist')
def download_partides_admin():
    try:
        player = request.form['usuari']
        partides = Partida.query.filter_by(player=player, current=False).all()
    except:
        partides=[]
    idi=get_locale()
    if idi=='es':
        d={'Dificultad':[],'Hitos':[],'Puntos':[],'Pausas':[],'Fecha':[],'Orden seguido':[],'Picos':[],'Cansancio después de jugar':[],'Facilidad en cansarse':[],'Forma física después de jugar':[],'Agotamiento después de jugar':[]}
        for user in partides:
            d['Dificultad'].append(user.difficulty_partida)
            d['Hitos'].append(user.num_milestones)
            d['Puntos'].append(user.total_points)
            d['Pausas'].append(user.nparades)
            d['Fecha'].append(user.dia_partida)
            d['Orden seguido'].append(user.order)
            d['Picos'].append(user.pics)
            d['Cansancio después de jugar'].append(user.answer1)
            d['Facilidad en cansarse'].append(user.answer2)
            d['Forma física después de jugar'].append(user.answer3)
            d['Agotamiento después de jugar'].append(user.answer4)
    elif idi=='ca':
        d={'Dificultat':[],'Fites':[],'Punts':[],'Pauses':[],'Data':[],'Ordre seguit':[],'Pics':[],'Cansament després de jugar':[],'Facilitat en cansar-se':[],'Forma física després de jugar':[],'Esgotament després de jugar':[]}
        for user in partides:
            d['Dificultat'].append(user.difficulty_partida)
            d['Fites'].append(user.num_milestones)
            d['Punts'].append(user.total_points)
            d['Pauses'].append(user.nparades)
            d['Data'].append(user.dia_partida)
            d['Ordre seguit'].append(user.order)
            d['Pics'].append(user.pics)
            d['Cansament després de jugar'].append(user.answer1)
            d['Facilitat en cansar-se'].append(user.answer2)
            d['Forma física després de jugar'].append(user.answer3)
            d['Esgotament després de jugar'].append(user.answer4)
    else:
        d={'Difficulty':[],'Milestones':[],'Points':[],'Pauses':[],'Date':[],'Followed order':[],'Spikes':[],'Tiredness after playing':[],'Ease in getting tired':[],'Fitness level after playing':[],'Exhaustion after playing':[]}
        for user in partides:
            d['Difficulty'].append(user.difficulty_partida)
            d['Milestones'].append(user.num_milestones)
            d['Points'].append(user.total_points)
            d['Pauses'].append(user.nparades)
            d['Date'].append(user.dia_partida)
            d['Followed order'].append(user.order)
            d['Spikes'].append(user.pics)
            d['Tiredness after playing'].append(user.answer1)
            d['Ease in getting tired'].append(user.answer2)
            d['Fitness level after playing'].append(user.answer3)
            d['Exhaustion after playing'].append(user.answer4)    
    df = pd.DataFrame(data=d)  
    strIO = io.BytesIO()
    writer = pd.ExcelWriter(strIO, engine="xlsxwriter")
    df.to_excel(writer, sheet_name='Partidas', index=False)
    workbook = writer.book
    worksheet = writer.sheets['Partidas']        
    for i, col in enumerate(df.columns):
        column_len = df[col].astype(str).str.len().max()
        column_len = max(column_len, len(col)) + 2
        worksheet.set_column(i, i, column_len)
    writer.save()
    excel_data = strIO.getvalue()
    strIO.seek(0)
    return send_file(strIO,
                     attachment_filename='partidas.xlsx',
                     as_attachment=True)

#Registre i donar d'alta usuaris
@management_t_blueprint.route('/', methods=['POST']) 
@login_required
@roles_accepted('therapist','admin')
def registrar_usuari():
    email_cientific = current_user.email
    if request.form['psw'] == request.form['psw-repeat']:
        try:
            db.create_all()
            mail = request.form['email']
            user_datastore.create_user(usuari= request.form['usuari'], email= mail, password=request.form['psw'], codi= request.form['code'], email_cientific = email_cientific, registrat=True, nom= 'nom de prova')
            user_datastore.add_role_to_user(mail,'patient')
            db.session.commit()
            return render_template('registre_success.html')
        except:
            return render_template('registre_no_success_usuari.html')
    else:
        return render_template('registre_no_success_psw.html')
    
@management_t_blueprint.route('/registre')
@login_required
@roles_accepted('therapist','admin')
def registrar():
    return render_template('registre.html')

@management_t_blueprint.route('/alta')
@login_required
@roles_accepted('therapist','admin')
def alta():
    return render_template('alta.html')

@management_t_blueprint.route('/eliminar', methods=['POST'])
@login_required
@roles_accepted('therapist','admin')
def eliminar():
    mail = request.form['email']
    email_cientific = current_user.email
    if Role.query.filter_by(name='admin').first() in current_user.roles:
        user = User.query.filter_by(email=mail).first()
        if not user:
            return render_template('alta_error_admin.html')
        else:
            for partida in user.partides:
                db.session.delete(partida)
            db.session.delete(user)
            db.session.commit()
            return render_template('admin.html')
    else:   
        user = User.query.filter_by(email=mail, email_cientific = email_cientific).first()
        if not user:
            return render_template('alta_error.html')
        else:
            for partida in user.partides:
                db.session.delete(partida)
            db.session.delete(user)
            db.session.commit()
            return render_template('dashboard_terap.html')
    
@management_t_blueprint.route('/menu_registre')
@login_required
@roles_accepted('therapist','admin')
def menu_registrar():
    return render_template('menu_registre.html')

#mail
@management_t_blueprint.route('/registre_codi')
@login_required
@roles_accepted('therapist','admin')
def registrar_codi():
    return render_template('registre_codi.html')   

#Busqueda d'usuari
@management_t_blueprint.route('/busqueda')
@login_required
@roles_accepted('therapist','admin')
def show_busqueda():
    return render_template('busqueda.html') 

@management_t_blueprint.route('/search', methods=['POST'])
@login_required
@roles_accepted('therapist','admin')
def search():
    mail = request.form['email']
    email_cientific = current_user.email
    if Role.query.filter_by(name='admin').first() in current_user.roles:
        users = User.query.filter_by(email=mail).first()
        if users == None:
            return render_template('busqueda_error_admin.html')
        else:
            partides = Partida.query.filter_by(player=users.usuari, current=False).all()
            return render_template('partides_admin.html',partides=partides)
    else:
        users = User.query.filter_by(email=mail, email_cientific = email_cientific).first()
        if users == None:
            return render_template('busqueda_error.html')
        else:
            partides = Partida.query.filter_by(player=users.usuari, current=False).all()
            return render_template('partides.html',partides=partides)
        
#dasboard
@management_t_blueprint.route('/dashboard_terap')
@login_required
@roles_accepted('therapist','admin')
def show_terap_dashboard():
    if Role.query.filter_by(name='admin').first() in current_user.roles:
        return render_template('admin.html')
    else:
        return render_template('dashboard_terap.html')

#idioma
@management_t_blueprint.route('/idioma_terap')
@login_required
@roles_accepted('therapist','admin')
def idioma_terap():
    return render_template('idioma_terap.html') 
###############


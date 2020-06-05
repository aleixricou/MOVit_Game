"""
Blueprint de management
"""
import jsonify
import io
import json

from flask import Blueprint, current_app, request, render_template, send_file
from jinja2 import TemplateNotFound
from .models import User, Cientific, Role, Partida
from .basedades import BASEDADES as db
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, login_required, roles_required, roles_accepted
from flask_babelex import Babel
from io import BytesIO
import pandas as pd
from flask_login import current_user
from sqlalchemy import desc
from flask_security.utils import hash_password
from .babel import babel, babel_blueprint, get_locale

cientific_datastore = SQLAlchemyUserDatastore(db, Cientific, Role)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

management_a_blueprint = Blueprint('management_admin', __name__, template_folder='templates')

#Menu administrador

#Registre de científics i usuaris  
@management_a_blueprint.route('/regis_terap', methods=['POST'])   
@login_required
@roles_accepted('admin')
def registrar_terap():
    if request.form['psw'] == request.form['psw-repeat']:
        try:
            db.create_all()
            mail = request.form['email']
            cientific_datastore.create_user(usuari= request.form['usuari'], email= mail, password=hash_password(request.form['psw']), num_usuaris= 0)
            cientific_datastore.add_role_to_user(mail,'therapist')
            db.session.commit()
            return render_template('admin.html')
        except:
            return render_template('registre_no_success_usuari.html')
    else:
        return render_template('registre_no_success_psw.html')

@management_a_blueprint.route('/registre_no_success_psw')
@login_required
@roles_accepted('admin')  
def registrar_no_success_psw():
    return render_template('registre_no_success_psw.html')

@management_a_blueprint.route('/registre_no_success_usuari')
@login_required
@roles_accepted('admin')  
def registrar_no_success_usuari():
    return render_template('registre_no_success_usuari.html')
        
@management_a_blueprint.route('/registre_terapeuta')   
@login_required
@roles_accepted('admin')    
def registrar_terapeuta():
    return render_template('registre_terapeuta.html')

@management_a_blueprint.route('/menu_registre_admin')   
@login_required
@roles_accepted('admin')    
def menu_registrar_terapeuta():
    return render_template('menu_registre_admin.html')

@management_a_blueprint.route('/alta_admin')
@login_required
@roles_accepted('admin')
def alta_admin():
    return render_template('alta_admin.html')

@management_a_blueprint.route('/alta_u_admin')
@login_required
@roles_accepted('admin')
def alta_u_admin():
    return render_template('alta_u_admin.html')

@management_a_blueprint.route('/eliminar_admin', methods=['POST'])
@login_required
@roles_accepted('admin')
def eliminar_admin():
    mail = request.form['email']
    user = Cientific.query.filter_by(email=mail).first()
    if not user:
        return render_template('alta_admin_error.html')
    else:
        for jugador in user.posts:
            for partida in jugador.partides:
                db.session.delete(partida)
            db.session.delete(jugador)
        db.session.delete(user)
        db.session.commit()
        return render_template('admin.html')

@management_a_blueprint.route('/registre_codi_admin')
@login_required
@roles_accepted('admin')
def enviem_codi_admin():
    return render_template('registre_codi_admin.html')
       
#Dashboard administradors
@management_a_blueprint.route('/admin')   
@login_required
@roles_accepted('admin')    
def dashboard_admin():
    return render_template('admin.html')

#Llistat de terapeutes
@management_a_blueprint.route('/cientifics')
@login_required
@roles_accepted('admin')
def show_all_cientifics_results():
    users=Cientific.query.all()
    for terap in users:
        num=0
        for jugador in terap.posts:
            num+=1
        terap.num_usuaris=num
    db.session.commit()
    return render_template('cientifics.html',users=users)

@management_a_blueprint.route('/download_terap')
@login_required
@roles_accepted('admin')
def download_terap():
    users=Cientific.query.all()
    idi=get_locale()
    if idi=='es':
        d={'Nombre':[],'E-Mail':[],'Número de jugadores asignados':[]}
        for cientific in users:
            if cientific.usuari != None:
                d['Nombre'].append(cientific.usuari)
                d['E-Mail'].append(cientific.email)
                d['Número de jugadores asignados'].append(cientific.num_usuaris)
    elif idi=='ca':
        d={'Nom':[],'E-Mail':[],'Nombre de jugadors assignats':[]}
        for cientific in users:
            if cientific.usuari != None:
                d['Nom'].append(cientific.usuari)
                d['E-Mail'].append(cientific.email)
                d['Nombre de jugadors assignats'].append(cientific.num_usuaris)
    else:
        d={'Name':[],'E-Mail':[],'Number of assigned players':[]}
        for cientific in users:
            if cientific.usuari != None:
                d['Name'].append(cientific.usuari)
                d['E-Mail'].append(cientific.email)
                d['Number of assigned players'].append(cientific.num_usuaris)
    
    df = pd.DataFrame(data=d)  
    strIO = io.BytesIO()
    writer = pd.ExcelWriter(strIO, engine="xlsxwriter")
    df.to_excel(writer, sheet_name='Terapeutas', index=False)
    workbook = writer.book
    worksheet = writer.sheets['Terapeutas']        
        #Iterate through each column and set the width == the max length in that column. A padding length of 2 is also added.
    for i, col in enumerate(df.columns):
        # find length of column i
        column_len = df[col].astype(str).str.len().max()
        # Setting the length if the column header is larger
        # than the max column value length
        column_len = max(column_len, len(col)) + 2
        # set the column length
        worksheet.set_column(i, i, column_len)
    writer.save()
    excel_data = strIO.getvalue()
    strIO.seek(0)
    return send_file(strIO,
                     attachment_filename='terapeutas.xlsx',
                     as_attachment=True)


@management_a_blueprint.route('/download_partides_a', methods=['POST'])
@login_required
@roles_accepted('admin')
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

@management_a_blueprint.route('/download_users_a')
@login_required
@roles_accepted('admin')
def download_users_admin():
    users=User.query.all()
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
    
#reset
@management_a_blueprint.route('/reset_usu')
@login_required
@roles_accepted('admin')
def reset_usuarios():
    users=User.query.all()
    for user in users:
        for partida in user.partides:
                db.session.delete(partida)
        db.session.delete(user)
    db.session.commit()
    return render_template('admin.html')

@management_a_blueprint.route('/reset')
@login_required
@roles_accepted('admin')
def reset():
    cientifics=Cientific.query.all()
    for cientific in cientifics:
#        if Role.query.filter_by(name='admin').first() not in cientific.roles:
        if current_user != cientific:
            for jugador in cientific.posts:
                for partida in jugador.partides:
                    db.session.delete(partida)
                db.session.delete(jugador)
            db.session.delete(cientific)
        db.session.commit()
    return render_template('admin.html') 

@management_a_blueprint.route('/menu_reset')
@login_required
@roles_accepted('admin')
def menu_reset():
    return render_template('menu_reset.html')
#idioma
@management_a_blueprint.route('/idioma_admin')
@login_required
@roles_accepted('admin')
def idioma_admin():
    return render_template('idioma_admin.html') 
#Búsqueda
@management_a_blueprint.route('/busqueda_admin')
@login_required
@roles_accepted('admin')
def show_busqueda():
    return render_template('busqueda_admin.html')

#LListat d'usuaris
@management_a_blueprint.route('/all_users_admin')
@login_required
@roles_accepted('admin')
def show_all_users_results():
    users=User.query.all()
    return render_template('users_admin.html',users=users)

###################
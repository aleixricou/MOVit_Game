from flask import Flask, render_template, request, current_app, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, login_required, roles_accepted
from flask_babelex import Babel, gettext
from flask_mail import Mail, Message
from flask_login import current_user, logout_user
from flask_security.utils import verify_password
from .basedades import BASEDADES as db
from .models import Role, User, Cientific
from .management import management_blueprint
from .management_terapeuta import management_t_blueprint
from .management_admin import management_a_blueprint
from .appmanagement import appmanagement_blueprint
from .babel import babel, babel_blueprint, get_locale
from .config import Config
import click
import random
import os
from .create_database import create_database
#Log out
from flask import session, escape, redirect, url_for

def create_app():
    # Create app
    app = Flask(__name__)
    
    #registre blueprints
    app.register_blueprint(appmanagement_blueprint)
    app.register_blueprint(management_blueprint)
    app.register_blueprint(management_t_blueprint)
    app.register_blueprint(management_a_blueprint)
    app.register_blueprint(babel_blueprint)
    
    babel.init_app(app)
    

    #afegeix la configuració desitjada (també l'idioma)
    settings = Config(app)
    app.config.from_object(settings)

    db.init_app(app)

    # Setup Database Principal (On està l'administrador)
    cientific_datastore = SQLAlchemyUserDatastore(db, Cientific, Role)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)

    # Setup Flask-Security
    security = Security(app, cientific_datastore)
    
    #Mail
    mail= Mail(app)
    
    @app.route("/")
    def dashboard():
        return render_template("dashboard.html")
    
    #Mail
    @app.route('/send_mail', methods=['POST']) 
    @login_required
    @roles_accepted('therapist')
    def send_mail():
        code=str(random.randrange(10000000, 99999999 ,1))
        while User.query.filter_by(codi=code).first() is not None:
            code=str(random.randrange(10000000, 99999999 ,1))
        comail = request.form['email']
        name = request.form['name']
        email_cientific = current_user.email
        idi=get_locale()
        try:
            if idi=='es':
                msg = Message(gettext('Envío de código de registro'), recipients=[comail])
                msg.html = gettext('<em>Por favor, no responda a este mensaje</em> <p>Bienvenido a MOVit Game,</p> <p>El código para registrarse en la aplicación es el siguiente: <b>'+code+'</b>.</p> <br> <p>¡El equipo de MOVit GAME le desea que tenga una buena experiencia!</p>')
            elif idi=='ca':
                msg = Message('Enviament de codi de registre', recipients=[comail])
                msg.html = '<em>Si us plau, no respongui a aquest missatge</em> <p>Benvingut a MOVit Game,</p> <p>El codi per registrar-se a l\'aplicació és el següent: <b>'+code+'</b>.</p> <br> <p>L\'equip de MOVit GAME desitja que tingui una bona experiència!</p>'    
            elif idi=='en':
                msg = Message('Sending registration code', recipients=[comail])
                msg.html = '<em>Please do not reply to this message</em> <p>Welcome to MOVit Game,</p> <p>The code to register in the application is as follows: <b>'+code+'</b>.</p> <br> <p>The MOVit GAME team wishes you have a good experience!</p>'
                
            db.create_all()
            user_datastore.create_user(email= comail, codi=code, email_cientific = email_cientific, nom=name)
            user_datastore.add_role_to_user(comail,'patient')
            db.session.commit()
            mail.send(msg)
            return render_template('dashboard_terap.html')
        except:
            return render_template("registre_codi_error.html")
        
    @app.route('/send_mail_admin', methods=['POST']) 
    @login_required
    @roles_accepted('admin')
    def send_mail_admin():
        code=str(random.randrange(10000000, 99999999 ,1))
        while User.query.filter_by(codi=code).first() is not None:
            code=str(random.randrange(10000000, 99999999 ,1))
        comail = request.form['email']
        name = request.form['name']
        email_cientific = request.form['email_t']
        cientific = Cientific.query.filter_by(email=email_cientific).first()
        idi=get_locale()
        if cientific == None:
            return render_template("registre_codi_error_admin.html")
        else:
            try:
                if idi=='es':
                    msg = Message(gettext('Envío de código de registro'), recipients=[comail])
                    msg.html = gettext('<em>Por favor, no responda a este mensaje</em> <p>Bienvenido a MOVit Game,</p> <p>El código para registrarse en la aplicación es el siguiente: <b>'+code+'</b>.</p> <br> <p>¡El equipo de MOVit GAME le desea que tenga una buena experiencia!</p>')
                elif idi=='ca':
                    msg = Message('Enviament de codi de registre', recipients=[comail])
                    msg.html = '<em>Si us plau, no respongui a aquest missatge</em> <p>Benvingut a MOVit Game,</p> <p>El codi per registrar-se a l\'aplicació és el següent: <b>'+code+'</b>.</p> <br> <p>L\'equip de MOVit GAME desitja que tingui una bona experiència!</p>'    
                elif idi=='en':
                    msg = Message('Sending registration code', recipients=[comail])
                    msg.html = '<em>Please do not reply to this message</em> <p>Welcome to MOVit Game,</p> <p>The code to register in the application is as follows: <b>'+code+'</b>.</p> <br> <p>The MOVit GAME team wishes you have a good experience!</p>'
                db.create_all()
                user_datastore.create_user(email= comail, codi=code, email_cientific = email_cientific, nom=name)
                user_datastore.add_role_to_user(comail,'patient')
                db.session.commit()
                mail.send(msg)
                return render_template('admin.html')
            except:
                return render_template("registre_codi_error_admin.html")
    
    @app.route('/send_mess', methods=['POST'])
    def consulta():
        comail = request.form['email']
        name = request.form['usuari']
        descripcio = request.form['desc']
        text = request.form['cons']
        msg = Message(descripcio, recipients=['movitgameserver@gmail.com'])
        msg.html = '<p>'+name+' amb email <b>'+comail+'</b> ha escrit:</p> <p>'+text+'</p>'
        mail.send(msg)
        return render_template('dashboard.html')
    
    @app.route('/QR_download', methods=['POST'])
    def descarrega_qr():
        usuari = request.form['usuari']
        password = request.form['password']
        user = User.query.filter_by(usuari=usuari).first()
        uploads = app.config['UPLOAD_FOLDER']
        if user == None:
            return render_template('milestones_u.html')
        else:
            if not verify_password(password,user.password):
                return render_template('milestones_p.html')
            else:
                level=user.level
                if level==1:
                    return send_from_directory(directory=uploads, filename='fites1.pdf', as_attachment=True)
                elif level==2:
                    return send_from_directory(directory=uploads, filename='fites2.pdf', as_attachment=True)
                elif level==3:
                    return send_from_directory(directory=uploads, filename='fites3.pdf', as_attachment=True)
                else:
                    return send_from_directory(directory=uploads, filename='fites4.pdf', as_attachment=True)
    
    @app.cli.command('createdb')
    @click.argument('email')
    @click.password_option()
    def initdb_command(email = None, password = None):
        create_database(db, email, password)

    #Tanca sessió
    @app.route('/logout')
    @login_required
    def logout():
        user = current_user
        user.authenticated = False
        db.session.add(user)
        db.session.commit()
        logout_user()
        return render_template('logout_done.html')

    return app

if __name__ == ('__main__'):
    app = create_app()


    #run the flask app
#    app.run()

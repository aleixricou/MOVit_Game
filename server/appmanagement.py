import json

from flask import Blueprint, current_app, request, render_template
from jinja2 import TemplateNotFound
from flask_security import Security, SQLAlchemyUserDatastore, login_required
from .models import User, Role, Cientific, Partida
from .basedades import BASEDADES as db
import datetime as dt
from flask_security.utils import hash_password, verify_password
import random

appmanagement_blueprint = Blueprint('appmanagement', __name__, template_folder='templates')
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
partida_datastore = SQLAlchemyUserDatastore(db, Partida, Role)

servidor='http://localhost:5000'
        
      
### sendlogin() receives the user (nickname) and password from the app
@appmanagement_blueprint.route('/sendlogin', methods=['POST','GET'])
def sendlogin():
    usuari = request.form['usuari']
    password = request.form['password']
    d={}
    user = User.query.filter_by(usuari=usuari).first()
    if user != None:
        if not verify_password(password,user.password):
            d['login'] = 'False'
            d['response']= 'Contrasenya incorrecta'
        else:
            d['login'] = 'True'
            d['response']= 'Usuari i contrasenya correctes'        
        user.login=d
        db.session.commit()
    return json.dumps({"success": True, "message": "user registered", "code": 200}), {'Content-Type': "application/json"}
        
### getlogin() sends a True value if login was correct and False if login is incorrect
@appmanagement_blueprint.route('/getlogin', methods=['GET'])
def getlogin():
    users=User.query.all()
    for user in users:
        if user.login != {}:
            d=user.login
            user.login={}
            db.session.commit()        
            return json.dumps(d),200,{'Contact-Type': "application/json"}
    return json.dumps({'login':'False','response':'L\'usuari no es troba en la base de dades'}),200,{'Contact-Type': "application/json"}

### sendregister() gets code, username, nickname and password from the app
@appmanagement_blueprint.route('/sendregister', methods=['POST'])
def sendregister():
    code = request.form['code']
    username = request.form['username']
    nickname = request.form['nickname']
    password = request.form['password']
    user = User.query.filter_by(codi=code, email = username).first()
    d={}
    userlist=User.query.all()
    t=[]
    for u in userlist:
        t.append(u.usuari)       
    if user != None:
        if user.registrat == True:
            d['register'] = 'False'
            d['response'] = 'Codi registrat amb anterioritat'
            
        elif nickname in t:
            d['register'] = 'False'
            d['response'] = 'L\'usuari introduït ja es troba la base de dades'

        else:
            d['register'] = 'True'
            d['response'] = 'Registre correcte'
            user.usuari = nickname
            user.password = hash_password(password)
            user.registrat = True
        user.registre= d   
        db.session.commit()
    return json.dumps({"success": True, "message": "user registered", "code": 200}), {'Content-Type': "application/json"}


### getregister() sends a True value if register can be proceeded or False if something is incorrect
@appmanagement_blueprint.route('/getregister', methods=['GET'])
def getregister():
    users=User.query.all()
    for user in users:
        if user.registre != {}:
            d=user.registre
            user.registre={}
            db.session.commit()        
            return json.dumps(d),200,{'Contact-Type': "application/json"}
    return json.dumps({'register':'False','response':'Codi incorrecte, revisa que el codi sigui el mateix que el rebut al correu electrònic introduït'}),200,{'Contact-Type': "application/json"}


### startgame() gets the user
@appmanagement_blueprint.route('/start_game', methods=['POST'])
def startgame():
    username = request.form['usuari']
    fatiga = request.form['fatigue']
    user = User.query.filter_by(usuari=username).first()  
    user.dificulty=fatiga
    db.session.commit()     
    d=typegame(username)
    user.inici=d
    partida_datastore.create_user(player=user.usuari, current = True, level_partida=d['level'], num_milestones = d['milestones'], difficulty_partida=d['difficulty'])
    db.session.commit()
    return  json.dumps({"success": True, "message": "user started game", "code": 200}), {'Content-Type': "application/json"}


### newgame() sends the difficulty, level, number of milestones, distance to reach between milestones, hints and guilty character
@appmanagement_blueprint.route('/new_game', methods=['GET'])
def newgame():
    users=User.query.all()
    for user in users:
        if user.inici != {}:
            d=user.inici
            user.inici={}
            db.session.commit()        
            return json.dumps(d),200,{'Contact-Type': "application/json"}
    return json.dumps({"success": False, "message": "user error", "code": 400}),{'Contact-Type': "application/json"}

def typegame(username):
    d={}
    user = User.query.filter_by(usuari=username).first()
    dificultat=user.dificulty
    level=user.level
    text,guilty=narrativa(level)
    milestones = 4
    distancia = [10,10,10,10]
    if level>1:
        distancia.append(10)
        milestones=5
        if level>2:
            distancia.append(10)
            distancia.append(10)
            milestones=7
            if level>3:
                distancia.append(10)
                distancia.append(10)
                milestones=9
    if dificultat == 1:
        s=[]
        for i in distancia:
            s.append(0*i)
        distancia = s
    elif dificultat == 2:
        s=[]
        for i in distancia:
            s.append(0.5*i)
        distancia = s
    elif dificultat == 4:
        s=[]
        for i in distancia:
            s.append(1.5*i)
        distancia = s        
    elif dificultat == 5:
        s=[]
        for i in distancia:
            s.append(2*i)
        distancia = s
    elif dificultat == 6:
        s=[]
        for i in distancia:
            s.append(2.5*i)
        distancia = s
    d['difficulty']= dificultat
    d['level']= level
    d['milestones'] = milestones
    d['distance'] = distancia
    d['hints'] = text
    d['guilty'] = guilty           
    return d

def narrativa(level):
    t=[]
    extra=['Crec que li agradava molt la natura','Recordo que tenia la mirada perduda','Crec recordar que no havia dormit bé','Només recordo que li agradava molt ballar','Recordo que tenia molt bon gust musical']
    num=random.randrange(0,len(extra),1)
    if level>1:
        t.append(extra[num])
    guilty=random.randrange(1,12,1)
    if guilty==1:
        t.append('Només recordo que tenia ulls parells')
        t.append('Recordo que portava algun accessori')
        t.append('Recordo que tenia antenes')
        t.append('Només recordo que tenia dents')
        if level>2:
            t.append('Només recordo que tenia ulls senars')
            t.append('Recordo llegir al diari que tenia ulls parells i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            if level>3:
                t.append('Només recordo que no tenia antenes')
                t.append('Recordo veure a les notícies que tenia antenes i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
                            
        
    elif guilty==2:
        t.append('Només recordo que tenia ulls senars')
        t.append('Recordo que portava algun accessori')
        t.append('Recordo que tenia antenes')
        t.append('Només recordo que tenia dents')
        if level>2:
            t.append('Només recordo que tenia ulls parells')
            t.append('Recordo llegir al diari que tenia ulls senars i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            if level>3:
                t.append('Només recordo que no tenia antenes')
                t.append('Recordo veure a les notícies que tenia antenes i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            
    elif guilty==3:
        t.append('Només recordo que tenia ulls parells')
        t.append('Recordo que no portava cap accessori')
        t.append('Recordo que tenia antenes')
        t.append('Només recordo que tenia dents')
        if level>2:
            t.append('Només recordo que tenia ulls senars')
            t.append('Recordo llegir al diari que tenia ulls parells i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            if level>3:
                t.append('Només recordo que no tenia antenes')
                t.append('Recordo veure a les notícies que tenia antenes i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            
    elif guilty==4:
        t.append('Només recordo que tenia ulls senars')
        t.append('Recordo que no portava cap accessori')
        t.append('Recordo que tenia antenes')
        t.append('Només recordo que tenia dents')
        if level>2:
            t.append('Només recordo que tenia ulls parells')
            t.append('Recordo llegir al diari que tenia ulls senars i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            if level>3:
                t.append('Només recordo que no tenia antenes')
                t.append('Recordo veure a les notícies que tenia antenes i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            
    elif guilty==5:
        t.append('Només recordo que tenia ulls parells')
        t.append('Recordo que no portava cap accessori')
        t.append('Recordo que tenia antenes')
        t.append('Només recordo que no tenia dents')
        if level>2:
            t.append('Només recordo que tenia ulls senars')
            t.append('Recordo llegir al diari que tenia ulls parells i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            if level>3:
                t.append('Només recordo que no tenia antenes')
                t.append('Recordo veure a les notícies que tenia antenes i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            
    elif guilty==6:
        t.append('Només recordo que tenia ulls senars')
        t.append('Recordo que no portava cap accessori')
        t.append('Recordo que tenia antenes')
        t.append('Només recordo que no tenia dents')
        if level>2:
            t.append('Només recordo que tenia ulls parells')
            t.append('Recordo llegir al diari que tenia ulls senars i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            if level>3:
                t.append('Només recordo que no tenia antenes')
                t.append('Recordo veure a les notícies que tenia antenes i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            
    elif guilty==7:
        t.append('Només recordo que tenia ulls parells')
        t.append('Recordo que no portava cap accessori')
        t.append('Recordo que tenia antenes')
        t.append('Només recordo que no tenia dents')
        if level>2:
            t.append('Només recordo que tenia ulls senars')
            t.append('Recordo llegir al diari que tenia ulls parells i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            if level>3:
                t.append('Només recordo que no tenia antenes')
                t.append('Recordo veure a les notícies que tenia antenes i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            
    elif guilty==8:
        t.append('Només recordo que tenia ulls senars')
        t.append('Recordo que no portava cap accessori')
        t.append('Recordo que no tenia antenes')
        t.append('Només recordo que no tenia dents')
        if level>2:
            t.append('Només recordo que tenia ulls parells')
            t.append('Recordo llegir al diari que tenia ulls senars i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            if level>3:
                t.append('Només recordo que tenia antenes')
                t.append('Recordo veure a les notícies que no tenia antenes i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            
    elif guilty==9:
        t.append('Només recordo que tenia ulls parells')
        t.append('Recordo que portava algun accessori')
        t.append('Recordo que tenia antenes')
        t.append('Només recordo que no tenia dents')
        if level>2:
            t.append('Només recordo que tenia ulls senars')
            t.append('Recordo llegir al diari que tenia ulls parells i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            if level>3:
                t.append('Només recordo que no tenia antenes')
                t.append('Recordo veure a les notícies que tenia antenes i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            
    elif guilty==10:
        t.append('Només recordo que tenia ulls senars')
        t.append('Recordo que portava algun accessori')
        t.append('Recordo que no tenia antenes')
        t.append('Només recordo que no tenia dents')
        if level>2:
            t.append('Només recordo que tenia ulls parells')
            t.append('Recordo llegir al diari que tenia ulls senars i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            if level>3:
                t.append('Només recordo que tenia antenes')
                t.append('Recordo veure a les notícies que no tenia antenes i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            
    elif guilty==11:
        t.append('Només recordo que tenia ulls parells')
        t.append('Recordo que no portava cap accessori')
        t.append('Recordo que no tenia antenes')
        t.append('Només recordo que tenia dents')
        if level>2:
            t.append('Només recordo que tenia ulls senars')
            t.append('Recordo llegir al diari que tenia ulls parells i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            if level>3:
                t.append('Només recordo que tenia antenes')
                t.append('Recordo veure a les notícies que no tenia antenes i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
              
    elif guilty==12:
        t.append('Només recordo que tenia ulls senars')
        t.append('Recordo que portava algun accessori')
        t.append('Recordo que no tenia antenes')
        t.append('Només recordo que tenia dents')
        if level>2:
            t.append('Només recordo que tenia ulls parells')
            t.append('Recordo llegir al diari que tenia ulls senars i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            if level>3:
                t.append('Només recordo que tenia antenes')
                t.append('Recordo veure a les notícies que no tenia antenes i un còmplice. Vigila amb el que et diuen que pot no ser cert!')
            
    return t,guilty


### milestones() gets the user and the number of the milestone it has reached
@appmanagement_blueprint.route('/milestone', methods=['POST'])
def milestones():
    username = request.form['usuari']
    milestone = int(request.form['milestone'])
    npics = int(request.form['pics'])
#    temps = float(request.form['temps'])
    partida = Partida.query.filter_by(player=username, current = True).first()
#ordre de les partides. S'ha de reiniciar el atribut order Because SQLAlchemy keeps track of references. As long as the references are the same, it does not see any change hence it does not commit the difference.
    #link: https://stackoverflow.com/questions/47998500/flask-sqlalchemy-append-to-pickletype-doesnt-update
    a=partida.order
    b=partida.pics
    if a != []:
        if a[-1] == milestone:
            partida.nparades +=1
    partida.order=[]
    partida.pics=[]
    db.session.commit()
    a.append(milestone)
    b.append(npics)
    partida.order=a
    partida.pics=b
    
    db.session.commit()   
    return  json.dumps({"success": True, "message": "user new milestone", "code": 200}), {'Content-Type': "application/json"}
 
### final() gets user, final score and win/lose boolean
@appmanagement_blueprint.route('/end', methods=['POST'])
def final():
    username = request.form['usuari']
    punts = float(request.form['punts'])
    win = request.form['win']
    date = dt.datetime.now()
    datestr = date.strftime("%d/%m/%Y (%I:%M %p)")
    user = User.query.filter_by(usuari=username).first()
    user.last_partida = datestr
    user.num_partides= user.num_partides+1
    if win:
        user.partides_win = user.partides_win+1
    #defineix el seguent level
        if user.partides_win >= 10:
            user.level=4
        elif 9 >= user.partides_win > 6:
            user.level=3
        elif 6 >= user.partides_win > 2:
            user.level=2
        else:
            user.level=1

    if user.punt_max < punts:
        user.punt_max=punts
    partida = Partida.query.filter_by(player=username, current = True).first()
    partida.dia_partida = datestr
    partida.total_points = punts
    db.session.commit()
    return  json.dumps({"success": True, "message": "success", "code": 200}), {'Content-Type': "application/json"}
    

### questionari() gets user and answers to the questionnaire
@appmanagement_blueprint.route('/endQuestAnswers', methods=['POST'])
def questionari():
    username = request.form['usuari']
    respostes = request.form['answers'] #array en format string amb les respostes dels usuaris
    respostes=eval(respostes)
    partida = Partida.query.filter_by(player=username, current = True).first()
    partida.current = False
    partida.answer1= int(respostes[0])
    partida.answer2= int(respostes[1])
    partida.answer3= int(respostes[2])
    partida.answer4= int(respostes[3])
    db.session.commit()
    return  json.dumps({"success": True, "message": "success", "code": 200}), {'Content-Type': "application/json"}
    
    
    
    
    

    

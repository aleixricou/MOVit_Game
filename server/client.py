import requests
import json

server='http://127.0.0.1:5000'

def send_user(usuari,password):
    json_data = {'usuari': usuari, 'password':password}
    r = requests.post(server+'/sendlogin', data= json_data)
    return r

def get_user():
    r = requests.get(server+'/getlogin')
    d=r.json()
    return d

def send_registre(code,username,nickname,password):
    json_data = {'code': code, 'username': username, 'nickname': nickname, 'password':password}
    r = requests.post(server+'/sendregister', data= json_data)
    return r

def get_registre():
    r = requests.get(server+'/getregister')
    d=r.json()
    return d

def give_calibration(username,cali):
    json_data = {'usuari': username,'start': cali }
    r = requests.post(server+'/manualcalibration', data= json_data)
    return r

def send_start(usuari,fatiga):
    json_data = {'usuari': usuari, 'fatigue':fatiga}
    r = requests.post(server+'/start_game', data= json_data)
    return r

def get_start():
    r = requests.get(server+'/new_game')
    d=r.json()
    return d

def send_milestone(usuari,milestone,pics):
    json_data = {'usuari': usuari, 'milestone': milestone, 'pics': pics}
    r = requests.post(server+'/milestone', data= json_data)
    return r

def send_end(usuari,punts,win):
    json_data = {'usuari': usuari, 'punts': punts, 'win': win}
    r = requests.post(server+'/end', data= json_data)
    return r

def send_answers(usuari,answers):
    json_data = {'usuari': usuari, 'answers': answers}
    r = requests.post(server+'/endQuestAnswers', data= json_data)
    return r

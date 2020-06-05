_DO_NOT_USE = "[override]"
import os.path

class Config(object):
    DEBUG = False
    APPLICATION_ROOT = "/"
    TESTING = False
    DATABASE_URI = 'sqlite:///'
    SECURITY_PASSWORD_SALT = _DO_NOT_USE
    SECRET_KEY = _DO_NOT_USE
    LANGUAGES = ['es','ca','en']
    SUPPORTED_LANGUAGES = {'en':'English','ca':'Català','es':'Español'}
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    #Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    #same as DEBUG
    #MAIL_DEBUG = False
    MAIL_USERNAME = 'movitgameserver@gmail.com'
    MAIL_PASSWORD = '1709.MGS'
    MAIL_DEFAULT_SENDER = ('Automatic server from MOVit Game','movitgameserver@gmail.com')
    MAIL_MAX_EMAILS = None
    #same as TESTING
    #MAIL_SUPPRESS_SEND = False
    MAIL_ASCII_ATTACHMENTS = False
    UPLOAD_FOLDER = 'static/pdf'
    
    def __init__(self, app):
        self.SQLALCHEMY_DATABASE_URI = "sqlite:///%s" %(os.path.join(app.instance_path, 'base_de_dades.db'))

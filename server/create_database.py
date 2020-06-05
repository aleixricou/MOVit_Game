from flask import current_app

def create_database(db, email=None, password = None):
    db.create_all()
    user_datastore = current_app.extensions["security"].datastore
    admin_role = user_datastore.create_role(name='admin', description='administrator of the data')
    therapist_role = user_datastore.create_role(name='therapist', description='therapist that analyzes the data')
    patient_role = user_datastore.create_role(name='patient', description='person that answers the quest')
    admin_user = user_datastore.create_user(email = email, password = password)
    user_datastore.add_role_to_user(admin_user, admin_role)
    db.session.commit()

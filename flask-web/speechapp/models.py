# When ever is required to be used along with a database

from . import db
from sqlalchemy.orm import relationship

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self,patient_name,email):
        self.patient_name = patient_name
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.patient_name

class AudioFiles(db.Model):
    __tablename__ = 'audiofiles'
    id = db.Column(db.Integer, primary_key=True)
    blob = db.Column(db.LargeBinary,nullable=False)
    patient_id = db.Column(db.Integer,db.ForeignKey('patients.id'))
    patient = db.relationship('Patient',backref=db.backref('audiofile', lazy=True))
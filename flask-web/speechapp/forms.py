from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length

class UploadForm(FlaskForm):
    patient_name = StringField('Patient name',validators=[DataRequired(), Length(min=2, max=35)])
    session_number = IntegerField("Session number",validators=[DataRequired()])
    uploadedfile = FileField('MP4 File or MP3 File',validators=[FileRequired(),FileAllowed(['mp4','mp3'], 'File must be in MP4 or MP3 format.')])
    submit = SubmitField('Submit')

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')

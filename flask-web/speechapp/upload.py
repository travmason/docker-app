import os
import functools
import time

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
from werkzeug.utils import secure_filename
from . import forms

import shutil

from utilities import audio_video_processing as avp
from utilities.helper_functions import get_name,strip_hidden,convert_name,write_status

bp = Blueprint('upload', __name__)
patients_path = os.path.join("instance","patients")
buffer_path = os.path.join("instance",".temp")

@bp.route("/", methods=["POST","GET"])
def fileupload():
    form = forms.UploadForm()
    if form.validate_on_submit() and request.method == "POST":

        # register patient into the list
        os.makedirs(patients_path) if not os.path.exists(patients_path) else print("Path exists")
        patient_name = get_name(form.patient_name.data)
        session = str(form.session_number.data)

        # make the buffer
        try:
            os.makedirs(os.path.join(buffer_path,patient_name,session))
        except FileExistsError:
            flash(f'A session is bring uploaded', category="alert")
            return render_template("upload/form.html", form=form, loadable = True)
        
        # get audio name
        audio_video_filename = secure_filename(form.uploadedfile.data.filename)

        # save video into buffer
        save_path = os.path.join(buffer_path,patient_name,session,audio_video_filename)
        form.uploadedfile.data.save(save_path)
        old_name, ext = os.path.splitext(save_path)
        if ext == ".mp3":
            old_file_path = os.path.join(buffer_path,patient_name,session,audio_video_filename)
        else:
            ext = ".mp3"
            old_file_path = avp.extract_audio_pydub(save_path,audio_video_filename,patient_name,session)
        # create dir ready for moving mp3 near instant
        try:
            os.makedirs(os.path.join(patients_path,patient_name,session))
        except FileExistsError:
            flash(f'Session {session} already exists. Delete the session before uploading the session again.', category="alert")
            return render_template("upload/form.html", form=form, loadable = True)
        os.rename(old_file_path,os.path.join(patients_path,patient_name,session,patient_name + "_source_" + session + ext))
        try:
            os.remove(save_path)
        except FileNotFoundError:
            pass
        shutil.rmtree(os.path.join(buffer_path,patient_name))

        # write a hidden status file here
        write_status(patient_name,session,0)
    
        return render_template("upload/success.html")
    return render_template("upload/form.html", form=form, loadable = True)

@bp.route("/processing")
def process():
    return render_template("upload/process.html", loadable = True)

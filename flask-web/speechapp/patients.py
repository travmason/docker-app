import os
import time
from . import forms

from flask import Blueprint, flash, redirect, render_template, request, session, url_for, abort, send_from_directory, Response, Markup
from plotly.offline import plot

import shutil
import pandas as pd
import tensorflow as tf
import plotly.express as px

from utilities.helper_functions import get_name,strip_hidden,convert_name,write_status,read_status
from utilities.audio_video_processing import split_audio_to_segments
from utilities.model_prediction import process_dataframe, get_labels

bp = Blueprint('patients', __name__,url_prefix="/patients/")
patients_path = os.path.join("instance","patients")
model_path = os.path.join('speechapp','model','active_model.h5')
labels_path = os.path.join('speechapp','model','labels')

# Load model
loaded_model = tf.keras.models.load_model(model_path)
label = get_labels(labels_path)

def download_file(name,session,filename):
    path = os.path.join(os.path.abspath(patients_path),name,session)
    return send_from_directory(path,filename = filename, as_attachment = True)

def make_archive(source, destination):
    base = os.path.basename(destination)
    name = base.split('.')[0]
    format = base.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move('%s.%s'%(name,format), destination)
                   
@bp.route("/")
def show_patients():
    try:
        patients_list = sorted(strip_hidden(os.listdir(patients_path)))
        if len(patients_list) == 0:
            raise FileNotFoundError
        patients_names = [convert_name(name) for name in patients_list]
    except FileNotFoundError:
        patients_names = None
        patients_list = []
    return render_template("patients/table.html", length = len(patients_list), patients = patients_names, patient_folder = patients_list)

@bp.route("/<name>/")
def patient_details(name):
    patients_list = strip_hidden(os.listdir(patients_path))
    if name not in patients_list:
        flash(f"Patient \"{convert_name(name)}\" does not exist.",category="alert")
        return redirect(url_for("patients.show_patients",_external=True))
    else:
        session_list = strip_hidden(os.listdir(os.path.join(patients_path,name)))
        session_list.sort()

        # gets status for each of the sessions
        status_list = [read_status(name,session) for session in session_list]
    return render_template("patients/details.html", titlename = convert_name(name), name = name, sessions = len(session_list), session_list = session_list, statuses = status_list, loadable = True)

@bp.route("/<name>/delete/" ,methods=["POST","GET"])
def delete_patient(name):
    patients_list = strip_hidden(os.listdir(patients_path))
    form = forms.DeleteForm()
    if request.method == "POST":
        try:
            shutil.rmtree(os.path.join(patients_path,name))
            flash(f"Patient \"{convert_name(name)}\" has been removed.")
            return redirect(url_for("patients.show_patients",_external=True))
        except FileNotFoundError:
            flash(f"Patient \"{convert_name(name)}\" does not exist.",category="alert")
            return redirect(url_for("patients.show_patients",_external=True))
    if name not in patients_list:
        flash(f"Patient \"{convert_name(name)}\" does not exist.",category="alert")
        return redirect(url_for("patients.show_patients",_external=True))
    return render_template("patients/delete.html", form = form, titlename = convert_name(name), name = name, patient = True)

@bp.route("/<name>/<session>/")
def display_session(name,session):
    # checks if patient exists
    patients_list = strip_hidden(os.listdir(patients_path))
    if name not in patients_list:
        flash(f"Patient \"{convert_name(name)}\" does not exist.",category="alert")
        return redirect(url_for("patients.show_patients",_external=True))

    # checks if patient session exists
    session_list = os.listdir(os.path.join(patients_path,name))
    if session not in session_list:
        flash(f"Patient \"{convert_name(name)}\" session {session} does not exist.",category="alert")
        return redirect(url_for("patients.patient_details",name = name,_external=True))

    status = read_status(name,session)
    if status == "0" or status == "1":
        flash(f"Session {session} is not ready.", category="alert")
        return redirect(url_for('patients.patient_details',name = name))
    else:
        # check if source file exsists
        audio_source_name = "_".join([name,"source",session]) + ".mp3"
        csv_source_name = "_".join([name,session]) + ".csv"

        source_path = os.path.join(patients_path,name,session)
        if os.path.exists(os.path.join(source_path,"chunks")):
            pass

        if os.path.exists(os.path.join(source_path,csv_source_name)) and os.path.exists(os.path.join(source_path,audio_source_name)):
            flag_csv = True
            final_df = pd.read_csv(os.path.join(source_path,csv_source_name))
            final_df = final_df.rename(columns={
                "filename" : "Filename",
                "intervals" : "Intervals",
                "predictions" : "Predicted Emotion",
                "confidence" : "Model Confidence"
            })
        else:
            flash("CSV is not available or has been corrupted. Please delete the session and re-upload the session.",category="alert")
            flag_csv = False

            # create empty dataframe
            final_df = pd.DataFrame()

        return render_template("patients/session.html",
            titlename = convert_name(name),
            name = name, session = session, 
            flag = flag_csv,
            tables = [final_df.to_html(classes=("responsive-table","highlight"), na_rep="N/A" ,header=True, index = False)], loadable = True)

@bp.route("/<name>/<session>/delete", methods=["POST","GET"])
def delete_patient_session(name,session):
    session_list = strip_hidden(os.listdir(os.path.join(patients_path,name)))
    form = forms.DeleteForm()
    if request.method == "POST":
        try:
            shutil.rmtree(os.path.join(patients_path,name,session))
            flash(f"Patient \"{convert_name(name)}\" - Session {session} has been removed.")
            return redirect(url_for("patients.patient_details",name = name,_external=True))
        except FileNotFoundError:
            flash(f"Patient \"{convert_name(name)}\" does not exist.",category="alert")
            return redirect(url_for("patients.patient_details",name = name,_external=True))
    if session not in session_list:
        flash(f"Patient \"{convert_name(name)}\" does not exist.",category="alert")
        return redirect(url_for("patients.patient_details",name = name,_external=True))
    return render_template("patients/delete.html", form = form, titlename = convert_name(name), name = name, session_number = session, session = True)

@bp.route("/<name>/<session>/csv/")
def download_csv(name,session):
    csv_source_name = "_".join([name,session]) + ".csv"
    return download_file(name,session,csv_source_name)

@bp.route("/<name>/<session>/source/")
def download_source(name,session):
    source_path = os.path.join(patients_path,name,session)
    mp3_source_name = "_".join([name,"source",session]) + ".mp3"
    if os.path.exists(os.path.join(source_path,mp3_source_name)):
        return download_file(name,session,mp3_source_name)
    else:
        flash(f"Session {session} does not exist for {convert_name(name)}.", category="alert")
        return redirect(url_for("patients.patient_details", name = name))

@bp.route("/<name>/<session>/chunks/")
def download_chunks(name,session):
    try:
        path = os.path.join(patients_path,name,session)
        zipname = "_".join([name,session]) + ".zip"
        make_archive(os.path.join(path,"chunks"), os.path.join(path,zipname))
        with open(os.path.join(path, zipname), 'rb') as f:
            data = f.readlines()
        os.remove(os.path.join(path, zipname))
        return Response(data, headers={
            'Content-Type': 'application/zip',
            'Content-Disposition': 'attachment; filename=%s;' % zipname
        })
    except FileNotFoundError:
        flash(f"Session {session} does not exist for {convert_name(name)}.", category="alert")
        return redirect(url_for("patients.patient_details", name = name))

@bp.route("/<name>/<session>/chart/")
def display_chart(name,session):
    source_path = os.path.join(patients_path,name,session)
    csv_source_name = "_".join([name,session]) + ".csv"
    if os.path.exists(os.path.join(source_path,csv_source_name)):
        flag_csv = True
        final_df = pd.read_csv(os.path.join(source_path,csv_source_name))
        # emotion = {'predictions':['surprise','happy_positive','neutral','angry_negative','disgust_negative','sad_negative','fear_negative','not_applicable']}
        emotion = {'predictions':['not_applicable','fear_negative','sad_negative','disgust_negative','angry_negative','neutral','happy_positive','surprise']}
        a = px.histogram(final_df, x=final_df.predictions, title="Histogram", category_orders=emotion)
        b = px.line(final_df,y=final_df.intervals,x=final_df.predictions,category_orders=emotion, title="Line Graph",width=800, height=1000)
        histogram = plot(a,output_type="div")
        scatter_line = plot(b,output_type="div")
    else:
        flash(f"Session {session} does not exist for {convert_name(name)}.", category="alert")
        return redirect(url_for("patients.patient_details", name = name))
    return render_template(     
        "patients/charts.html",
        name = name,
        session = session, 
        titlename = convert_name(name),
        chart_histogram = Markup(histogram), 
        chart_scatter = Markup(scatter_line),
        flag = flag_csv)

@bp.route("process/<name>/<session>")
def process(name,session):
    try:
        status = read_status(name,session)
        if status == "0":
            write_status(name,session,1)
        elif status == "2":
            flash("Exsisting data is available.")
            return redirect(url_for("patients.display_session",name = name, session = session))
        else:
            flash(f"Patient \"{convert_name(name)}\" session {session} is still being converted.",category="alert")
            return redirect(url_for("patients.patient_details",name = name))
    except FileNotFoundError:
        flash(f"Patient \"{convert_name(name)}\" session {session} does not exist.",category="alert")
        return redirect(url_for("patients.patient_details",name = name))

    # check if source file exsists
    audio_source_name = "_".join([name,"source",session]) + ".mp3"
    csv_source_name = "_".join([name,session]) + ".csv"
    try:
        source_path = os.path.join(patients_path,name,session)
        initial_df = split_audio_to_segments(source_path,name,session,audio_source_name)

        # Inferencing code goes here
        final_df = process_dataframe(loaded_model,initial_df,label)

        # Finalize dataframe for export and display
        final_df = pd.concat([initial_df,final_df],axis=1)
        final_df = final_df.drop(labels = ['path'],axis=1)
        final_df.to_csv(os.path.join(source_path,csv_source_name),index=False)

        # updates the session status after completing inferencing and saving to csv
        write_status(name,session,2)
        return redirect(url_for("patients.display_session",name = name, session = session))

    except FileNotFoundError:
        abort(404, "Audio source file not found. Please upload one.")
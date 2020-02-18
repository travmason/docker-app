from flask import Flask, render_template

def handle_not_found(error):
    return render_template("errors/error.html", error = error)

def request_entity_too_large(error):
    return render_template("errors/error.html", error = error, additional_details = "Maximum file upload size is 100MB."), 413
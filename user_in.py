from flask import Blueprint, Flask, redirect, url_for, render_template, request, session, send_file
from flask_login import login_required, current_user
import datetime
import os
import pdfkit
import base64

from app import db
from models import CV

user_in = Blueprint('user_in', __name__, url_prefix="/user")


def convert_to_binary_data(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binary_data = file.read()
    return binary_data


@user_in.route("/")
@login_required
def home():
    return render_template("index.html")


@user_in.route("/new_cv", methods=["POST", "GET"])
@login_required
def new_cv():
    if request.method == "POST":
        image = request.files["image"]
        if image.filename != "":
            image.save(image.filename)
            image_binary = convert_to_binary_data(image.filename)
            os.remove(image.filename)
        else:
            image_binary = None
        if request.form["action"] == "save draft":
            cv = CV(name=request.form["name"],
                    surname=request.form["surname"],
                    birth_date=datetime.datetime.strptime(request.form["birth_date"], "%Y-%m-%d").date(),
                    user_id=current_user.id,
                    occupation=request.form["occupation"],
                    education=request.form["education"],
                    image=image_binary)
            db.session.add(cv)
            db.session.commit()
            session["cv_id"] = cv.id
            return render_template("new_cv.html", cv=cv)

        html_sample = f""" <h1>{request.form["name"]} {request.form["surname"]}</h3>"""
        if image_binary is not None:
            html_sample += f'<div style="display:inline-block;vertical-align:top;">' \
                           f'<img src="data:image/png;base64,{base64.b64encode(image_binary).decode()}" width=300px height=auto>' \
                           f'</div> ' \
                           f'<div style="display:inline-block;width:10px;"> </div>'
        html_sample += f"""<div style="display:inline-block;">
                           <h4>Birth Date:</h4>
                           <p>{request.form["birth_date"]}</p>
                           <h4>Work experience: </h4>
                           <p> <div style="white-space: pre-line">{request.form["occupation"]}</div> </p>
                          
                           <h4>Education: </h4>
                           <p> <div style="white-space: pre-line">{request.form["education"]}</div> </p>
                           </div>"""
        filename = f"cv_{current_user.id}.pdf"
        pdfkit.from_string(html_sample, output_path=filename)
        response = send_file(filename, as_attachment=True)
        os.remove(filename)
        return response
    get_all_cvs = CV.query.filter_by(user_id=current_user.id)
    unpacked = [item for item in get_all_cvs]
    if len(unpacked) == 0:
        return render_template("new_cv.html",
                               cv=CV(name="",
                                     surname="",
                                     birth_date=datetime.datetime.strptime("1900-01-01", "%Y-%m-%d").date(),
                                     user_id=current_user.id,
                                     occupation="",
                                     education="",
                                     image=None))
    last = unpacked[-1]
    return render_template("new_cv.html", cv=last)

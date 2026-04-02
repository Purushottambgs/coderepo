from flask import Flask, request

app= Flask(__name__)
@app.route("/")
def ff():
    return "it is my first program in flask"

@app.route("/about")
def about():
    return "it is a about page, here all information in this applications"

@app.route("/contect")
def contect():
    return ("my contect number is:- 9570303776")

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        return "send the data "
    else:
        return "pls only view in this data "
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

appp= Flask(__name__)

@appp.route("/", methods=["GET"])
def name():
    return "<h1> MY NAME IS PURUSHOTTAM KUMAR </h1>"

@appp.route("/course", methods=["GET"])
def course():
    return "<h2> my course name is MCA </h2>"

@appp.route("/success/<int:marks>")
def success(marks):
    return "you are pass because your marks is :-"+ str(marks)

@appp.route("/fail/<int:marks>")
def fail(marks):
    return "you are fail because your marks is :-"+str(marks)

@appp.route("/formm", methods=["GET", "POST"])
def formm():
    if request.method=="GET":
        return render_template('formm.html')
    else:
        maths= float(request.form['maths'])
        science= float(request.form['science'])
        history= float(request.form['history'])
        
        average_marks=(maths+science+history)/3
        res=""
        if average_marks>=50:
            res="success"
        else:
            res="not success"
        
        return redirect(url_for(res, marks=average_marks))

       # return render_template('formm.html', marks=average_marks)



if (__name__)== "__main__":
    appp.run(debug=True)
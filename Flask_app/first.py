from flask import Flask, render_template, request 

app= Flask(__name__)
@app.route("/")
def login():
    return render_template("login.html")

@app.route("/submit", methods=["POST"])
def submit():
    username= request.form.get("username")
    password= request.form.get("password")

    # if username== "Purushottam123" and password == "Puru123":
    #     return render_template("welcome.html", name = username)

    valid_users={
        'admin':'123',
        'Purushottam123':'Puru123',
        'puru':'123'
    }

    if username in valid_users and password == valid_users[username]:
        return render_template("welcome.html", name=username)
    
    else: 
        return "Invalid username or password"

if(__name__) == "__main__":
    app.run(debug=True)

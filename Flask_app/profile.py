from flask import Flask, render_template

app= Flask(__name__)

@app.route("/")
def student_profile():
    return render_template(
        "profile.html",
        name="puru",
        is_toper=True,
        subjects=["Maths", "Science", "History"]
    )

if (__name__) == "__main__":
    app.run(debug=True) 
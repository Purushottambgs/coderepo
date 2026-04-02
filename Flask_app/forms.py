from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class RegistrationForm(FlaskForm):
    name= StringField("Full Name", validators=[DataRequired(message="we need your name, it cannot be empty")])
    email= StringField("Email", validators=[DataRequired(message="Email message is required"), Email()])
    password= PasswordField("Password", validators=[DataRequired(),Length(min=8)])
    submit=SubmitField("Register")
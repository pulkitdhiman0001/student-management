from flask_wtf import FlaskForm

from wtforms import SelectField

class Form(FlaskForm):
    country = SelectField('country', choices=[])
    state = SelectField('state', choices=[])
    city = SelectField('city', choices=[])
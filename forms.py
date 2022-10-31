from flask_wtf import FlaskForm

from wtforms import SelectField


class Form(FlaskForm):
    country = SelectField('country', choices=[('', 'Select Country')])
    state = SelectField('state', choices=[('', 'Select State')])
    city = SelectField('city', choices=[('', 'Select City')])
    standard = SelectField('standard', choices=[''])
    section = SelectField('section', choices=[''])

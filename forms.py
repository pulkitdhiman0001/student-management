from flask_wtf import FlaskForm

from wtforms import SelectField

from wtforms.validators import data_required


class Form(FlaskForm):
    country = SelectField('country', choices=[('', 'Select Country')], validators=[data_required()], default="Select Country")
    state = SelectField('state', choices=[('', 'Select State')], validators=[data_required()], default="Select State")
    city = SelectField('city', choices=[('', 'Select City')], validators=[data_required()], default="Select City")
    standard = SelectField('standard', choices=[''], validators=[data_required()])
    section = SelectField('section', choices=[''], validators=[data_required()])

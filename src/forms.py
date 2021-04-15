from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, \
                                                 ValidationError

class LoginForm(FlaskForm):
    id_field = StringField('ID',
                        validators=[DataRequired()])
    password_field = PasswordField('Password', validators=[DataRequired()])
    submit_iam = SubmitField('Login with IAM')
    submit_driver = SubmitField('Login as driver')

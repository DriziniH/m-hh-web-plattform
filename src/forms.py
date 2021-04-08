from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, \
                                                 ValidationError

class LoginForm(FlaskForm):
    aws_access_key_id = StringField('Access Key ID',
                        validators=[DataRequired()])
    aws_secret_access_key = PasswordField('Secret Access Key', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
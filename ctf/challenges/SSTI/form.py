from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo
from wtforms import StringField, PasswordField


class LoginForm(FlaskForm):
    # Username field
    username = StringField('username',
                           validators=[DataRequired()],
                           render_kw={"placeholder": "username"})
    # Password field
    password = PasswordField('password',
                             validators=[DataRequired()],
                             render_kw={"placeholder": "password"})

class RegistrationForm(FlaskForm):
    # Username field
    username = StringField('username',
                           validators=[DataRequired()],
                           render_kw={"placeholder": "username"})
    # Password field
    password = PasswordField('password', [
        DataRequired(),
        EqualTo('confirm', message='passwords must match')
    ], render_kw={"placeholder": "password"})
    # Confirm password
    confirm = PasswordField('repeat_password', render_kw={"placeholder": "confirm password"})
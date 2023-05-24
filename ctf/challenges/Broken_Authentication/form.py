from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
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

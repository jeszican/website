from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, TextAreaField


class SecretForm(FlaskForm):
    # Username field
    name = StringField('name',
                           validators=[DataRequired()],
                           render_kw={"placeholder": "name"})
    # Password field
    secret = TextAreaField('secret',
                             validators=[DataRequired()],
                             render_kw={"placeholder": "type your secret"})

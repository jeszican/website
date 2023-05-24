from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField


class SearchForm(FlaskForm):
    search_term = StringField('search_term',
                           validators=[DataRequired()],
                           render_kw={"placeholder": "Search.."})

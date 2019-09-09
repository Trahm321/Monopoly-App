from wtforms import Form, StringField, validators


class user_name(Form):
    player_name = StringField("",validators=[validators.DataRequired(), validators.Length(min=1, max=10)])

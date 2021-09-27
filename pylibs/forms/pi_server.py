from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    BooleanField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired, )

class RelayForm(FlaskForm):
    relay_channel = IntegerField(
        label='relay_channel',
        validators=[
            DataRequired()
        ]
    )
    normally_open = BooleanField(
        label="normally_open",
        default=True,
        )
    gpio_port = IntegerField(
        label='gpio_port',
        validators=[DataRequired()])
    board_port = IntegerField(
        label='board_port',
        validators=[DataRequired()])
    description = StringField(label='description:',
                              validators=[DataRequired()])
    submit = SubmitField('submit')

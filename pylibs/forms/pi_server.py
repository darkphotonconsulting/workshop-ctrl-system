from email.policy import default
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
    model = StringField(
        label='relay_model',
        default='Songle',
    )
    state = BooleanField(
        label='Relay state (true: connected, fale: disconnected)',
        default=False)
    description = StringField(label='description:',
                              validators=[DataRequired()])
    manufacturer = StringField(label='manufacturer:',
                               validators=[DataRequired()],
                               default="Songle")
    relay_channel = IntegerField(label='relay_channel',
                                 validators=[DataRequired()])
    normally_open = BooleanField(
        label="normally_open",
        default=True,
    )

    ac_voltage_max = IntegerField(label='ac_voltage_max',
                                  validators=[DataRequired()],
                                  default=250)

    ac_voltage_min = IntegerField(label='ac_voltage_min',
                                  validators=[DataRequired()],
                                  default=125)

    dc_voltage_max = IntegerField(label='dc_voltage_max',
                                  validators=[DataRequired()],
                                  default=30)

    dc_voltage_min = IntegerField(label='dc_voltage_min',
                                  validators=[DataRequired()],
                                  default=28)

    ac_amperage_max = IntegerField(label='ac_amperage_max',
                                   validators=[DataRequired()],
                                   default=10)

    ac_amperage_min = IntegerField(label='ac_amperage_min',
                                   validators=[DataRequired()],
                                   default=10)

    dc_amperage_max = IntegerField(label='dc_amperage_max',
                                   validators=[DataRequired()],
                                   default=10)

    dc_amperage_min = IntegerField(label='dc_amperage_min',
                                   validators=[DataRequired()],
                                   default=10)

    activation_type = StringField(label='activation_type',
                                  validators=[DataRequired()],
                                  default="direct")

    activation_voltage = IntegerField(label='activation_voltage',
                                      validators=[DataRequired()],
                                      default=5)

    submit = SubmitField('submit')

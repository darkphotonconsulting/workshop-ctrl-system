""" Flask WTF Forms
"""
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
    """RelayForm - Provides a flask form used in the /api/relays resource

    allows the headunit system administrator to add/update/manage available relay channels

    \U0001F449 [Assumption] is there is a file "./data/relays.json" present under the repository root.
    
    File Format Example
    -------------------

    [
        {
            'model': 'SRD-05VDC-SL-C',
            'state': False,
            'description': 'relay channel 6',
            'manufacturer': 'Songle',
            'relay_channel': 6,
            'normally_open': True,
            'ac_voltage_max': 250,
            'ac_voltage_min': 125,
            'dc_voltage_min': 28,
            'dc_voltage_max': 30,
            'ac_amperage_max': 10,
            'ac_amperage_min': 10,
            'dc_amperage_max': 10,
            'dc_amperage_min': 10,
            'activation_type': 'direct',
            'activation_voltage': 5
        },
        ...
    ]

    Example:


    from pylibs.relay import RelayInfo
    relay = RelayInfo()    
    # the data is available here:
    relay.data

    Attributes:
    
        model (StringField) - The model number of the multi channel relay board
        state (BooleanField) - The state of the multi-channel relay board, set state to true if there is a device connected at the relay terminals
        description (StringField) - describe channel if relay, e.g. "Living Room Lights"
        manufacturer (StringField) - the relay boards manufacturer
        relay_channel (IntegerField) - the relay channel number
        normally_open (BooleanField) - if the channel is normally_open or not when the coils are energized
        ac_voltage_min (IntegerField) - the minimum AC voltage the relay can control
        ac_amperage_min (IntegerField) - the maximum AC amperage the relay can control
        ac_voltage_max (IntegerField) - the minimum AC voltage the relay can control
        ac_amperage_max (IntegerField) - the maximum AC amperage the relay can control
        dc_voltage_min (IntegerField) - the minimum DC voltage the relay can control
        dc_amperage_min (IntegerField) - the maximum DC amperage the relay can control
        dc_voltage_max (IntegerField) - the minimum DC voltage the relay can control
        dc_amperage_max (IntegerField) - the maximum DC amperage the relay can control
        submit = (SubmitField) - the form submit button
    """
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

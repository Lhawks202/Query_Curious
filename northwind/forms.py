from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from wtforms.widgets import HiddenInput

class UpdateItemQuantity(FlaskForm):
    item_id = HiddenField('Item ID', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)], widget=HiddenInput())
    increment = SubmitField('+')
    decrement = SubmitField('-')

class RemoveItem(FlaskForm):
    item_id = HiddenField('Item ID', validators=[DataRequired()])
    remove = SubmitField('remove')
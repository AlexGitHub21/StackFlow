from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange


class AddProductForm(FlaskForm):
    name = StringField("Наименование товара:", validators=[DataRequired()])
    description = StringField("Описание товара:", validators=[DataRequired()])
    price = DecimalField("Цена товара", validators=[DataRequired()], default=0.00)
    submit = SubmitField("Добавить товар")


class AddLocationForm(FlaskForm):
    name = StringField("Локация склада", validators=[DataRequired()])
    submit = SubmitField("Добавить локацию в БД")


class AddInventoryForm(FlaskForm):
    location = StringField("Локация", validators=[DataRequired()])
    quantity = IntegerField("Количество товара", validators=[DataRequired()])
    submit = SubmitField("Добавить на склад")


class ReduceQuantityForm(FlaskForm):
    quantity = IntegerField("Количество товара", validators=[DataRequired()])
    submit = SubmitField("Удалить")
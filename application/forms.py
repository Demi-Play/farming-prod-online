from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(4, 36)])
    surname = StringField('Фамилия', validators=[DataRequired(), Length(4, 36)])
    email = StringField('Почта', validators=[DataRequired(), Length(4, 36)])
    password = PasswordField('Пароль', validators=[
        DataRequired(), 
        Length(4, 36), 
        EqualTo('confirm_password', message='Пароли не совпадают')])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), Length(4, 36)])
    submit = SubmitField('Зарегистрироваться')
    
class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    
    submit = SubmitField('Войти')

class ProductForm(FlaskForm):
    name = StringField('Наименование продуктции', validators=[DataRequired(), Length(4, 36)])
    description = StringField('Описание', validators=[DataRequired(), Length(4, 255)])
    price = IntegerField('Стоимость', validators=[DataRequired()])
    count = IntegerField('Количество продукции на складе', validators=[DataRequired()])
    image = FileField('Изображение', validators=[DataRequired(), Email()])
    
    submit = SubmitField('Сохранить')
    
    
class Orders(FlaskForm):
    # Orders table
    quantity = IntegerField('Стоимость', validators=[DataRequired()])
    status = StringField('Статус заказа', validators=[DataRequired(), Length(4, 36)])
    
    submit = SubmitField('Сохранить')

class Reviews(FlaskForm):
    # Reviews table
    rating = IntegerField('Рейтинг', validators=[DataRequired()])
    comment = StringField('Комментарий', validators=[DataRequired(), Length(4, 255)])
    
    submit = SubmitField('Сохранить')

class Category(FlaskForm):
    # Category table
    name = StringField('Наименование категории', validators=[DataRequired(), Length(4, 36)])
    description = StringField('Описание категории', validators=[DataRequired(), Length(4, 255)])
    
    submit = SubmitField('Сохранить')

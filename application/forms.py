from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, IntegerField, SelectField, TextAreaField, SearchField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange

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
    name = StringField('Наименование продукции', validators=[DataRequired(), Length(4, 36)])
    description = StringField('Описание', validators=[DataRequired(), Length(4, 255)])
    price = IntegerField('Стоимость', validators=[DataRequired()])
    count = IntegerField('Количество продукции на складе', validators=[DataRequired()])
    category_id = SelectField('Категория', coerce=int, validators=[DataRequired()])
    image = FileField('Изображение')
    
    submit = SubmitField('Сохранить')
    
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        from application.db import Category
        self.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

class Orders(FlaskForm):
    product_id = SelectField('Продукт', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Количество', validators=[
        DataRequired(),
        NumberRange(min=1, message='Количество должно быть больше 0')
    ])
    submit = SubmitField('Создать заказ')

    def __init__(self, *args, **kwargs):
        super(Orders, self).__init__(*args, **kwargs)
        from application.db import Product
        self.product_id.choices = [
            (p.id, f"{p.name} - {p.price}₽") 
            for p in Product.query.filter(Product.count > 0).all()
        ]

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

class OrderForm(FlaskForm):
    category = SelectField('Категория', coerce=int, choices=[], default=0)
    search = StringField('Поиск')
    product_id = SelectField('Продукт', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Количество', validators=[
        DataRequired(),
        NumberRange(min=1, message='Количество должно быть больше 0')
    ])
    submit = SubmitField('Создать заказ')

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        from application.db import Category, Product
        # Добавляем пустой выбор для категории
        self.category.choices = [(0, 'Все категории')] + [
            (c.id, c.name) for c in Category.query.all()
        ]
        # Изначальные варианты для продуктов
        self.product_id.choices = [
            (p.id, f"{p.name} - {p.price}₽") 
            for p in Product.query.filter(Product.count > 0).all()
        ]

class ReviewForm(FlaskForm):
    rating = SelectField('Оценка', 
                        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
                        coerce=int,
                        validators=[DataRequired()])
    comment = StringField('Комментарий', validators=[DataRequired(), Length(4, 255)])
    
    submit = SubmitField('Отправить отзыв')

class CategoryForm(FlaskForm):
    name = StringField('Название категории', validators=[
        DataRequired(),
        Length(min=2, max=50, message='Название должно быть от 2 до 50 символов')
    ])
    description = TextAreaField('Описание', validators=[
        DataRequired(),
        Length(min=10, max=500, message='Описание должно быть от 10 до 500 символов')
    ])
    submit = SubmitField('Сохранить')

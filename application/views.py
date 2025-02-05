

        # Система лояльности (junior*):
            # Внедрить программу лояльности для постоянных 
            # клиентов с накопительными скидками и бонусами.

        # Функция поиска (junior):
            # Функция поиска: Разработать расширенный поиск по 
            # продуктам с фильтрами по цене, категории и наличию.

        # Интеграция с логистикой (middle):
            # Интеграция с логистикой: Включить систему отслеживания 
            # доставки для пользователей, чтобы они могли видеть статус своих заказов.

# Эти идеи мне понравились.

from flask import flash, redirect, render_template, url_for
from flask_login import login_user, logout_user
from application.app import app, db
from application.db import User
from application.forms import LoginForm, RegisterForm

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
            # The `register` function in the Flask application 
            # is responsible for handling the registration
            # process for new users. Here's a breakdown of 
            # what it does:
    form = RegisterForm()
    if form.validate_on_submit():
        # check user existing
        user = User.query.filter_by(name=form.name.data).first()
        if user:
            return 'User already exists'
        # create new user
        new_user = User(
                name=form.name.data, 
                surname=form.surname.data, 
                email=form.email.data
            )
        new_user.password = form.password.data
        
        db.session.add(new_user)
        db.session.commit()
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
            # The `login` function in the Flask application is 
            # responsible for handling the user login
            # process. Here's a breakdown of what it does:
    form = LoginForm()
    if form.validate_on_submit():
        # check user existing
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            # login user
            login_user(user=user)
            return redirect(url_for('index'))
        flash('Неверный логин или пароль!', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
            # The `logout` function in the Flask application 
            # is redirecting the user to the `'index'` route
            # when they access the `/logout` URL. This means 
            # that when a user clicks on a logout link or
            # button, they will be redirected back to the 
            # homepage or index page of the application.
    logout_user()
    return redirect(url_for('index'))



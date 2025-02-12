from flask import flash, redirect, render_template, url_for, request, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from application.app import app, db
from application.db import User, Product, Category, Orders, Reviews, ActivityLog, Orders as Order
from application.forms import (
    LoginForm, RegisterForm, ProductForm, 
    OrderForm,  # Используем OrderForm вместо Orders
    ReviewForm,
    CategoryForm
)
from functools import wraps
from flask import Blueprint
from sqlalchemy import func
from application.utils import role_required
from datetime import datetime, timedelta
import plotly.express as px
import pandas as pd

# Декоратор для проверки роли продавца или админа
def seller_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or \
           current_user.role not in ['seller', 'admin']:
            flash('У вас нет доступа к этой странице!', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Изменим имя blueprint'а с 'admin' на 'admin_panel'
admin_panel = Blueprint('admin_panel', __name__, url_prefix='/admin')

# Перенесем админские маршруты в Blueprint
@admin_panel.route('/')
@role_required('admin')
def index():
    """Главная страница админки"""
    try:
        # Получаем статистику
        stats = {
            'users_count': User.query.count(),
            'orders_count': Orders.query.count(),
            'products_count': Product.query.count(),
            'categories_count': Category.query.count()
        }
        
        # Получаем последние действия
        recent_activities = ActivityLog.query\
            .order_by(ActivityLog.created_at.desc())\
            .limit(10)\
            .all()
        
        # Добавляем дополнительные данные для активности
        for activity in recent_activities:
            if not hasattr(activity, 'type'):
                activity.type = activity.action_type.capitalize()
        
        return render_template('admin/index.html',
                             stats=stats,
                             recent_activities=recent_activities)
    except Exception as e:
        print(f"Error in admin index: {e}")  # For debugging
        flash('Произошла ошибка при загрузке данных', 'error')
        return render_template('admin/index.html', 
                             stats={'users_count': 0, 'orders_count': 0, 
                                   'products_count': 0, 'categories_count': 0},
                             recent_activities=[])

@admin_panel.route('/stats')
@role_required('admin')
def stats():
    """Страница статистики"""
    period = request.args.get('period', 'month')
    
    # Базовая статистика
    stats = {
        'total_sales': Order.query.filter(Order.status == 'completed').count(),
        'average_order': db.session.query(func.avg(Order.total_price))\
            .filter(Order.status == 'completed')\
            .scalar() or 0
    }
    
    # Здесь должна быть логика для построения графиков
    # Пример заглушки для графиков
    charts = {
        'sales_chart': "<div>График продаж</div>",
        'categories_chart': "<div>График категорий</div>",
        'users_activity_chart': "<div>График активности</div>",
        'orders_status_chart': "<div>График статусов</div>"
    }
    
    return render_template('admin/stats.html',
                         stats=stats,
                         period=period,
                         **charts)

@admin_panel.route('/activity-log')
@role_required('admin')
def activity_log():
    """Журнал действий"""
    page = request.args.get('page', 1, type=int)
    action_type = request.args.get('action_type', '')
    user = request.args.get('user', '')
    
    query = ActivityLog.query
    if action_type:
        query = query.filter_by(action_type=action_type)
    if user:
        query = query.join(User).filter(User.name.ilike(f'%{user}%'))
    
    pagination = query.order_by(ActivityLog.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('admin/activity_log.html',
                         logs=pagination.items,
                         pagination=pagination,
                         action_type=action_type,
                         user=user)

# --------- Аутентификация пользователей ---------

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация пользователя"""
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Пользователь с такой почтой уже существует!', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data
        )
        new_user.password = form.password.data
        
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация успешна!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Вход пользователя"""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверный логин или пароль!', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """Выход пользователя"""
    logout_user()
    return redirect(url_for('index'))

# --------- Управление продуктами ---------

@app.route('/products')
def products_list():
    """Список продуктов с фильтрацией"""
    # Получаем параметры фильтрации
    category_id = request.args.get('category', type=int)
    search_query = request.args.get('search', '').lower()  # Приводим запрос к нижнему регистру

    # Базовый запрос
    query = Product.query

    # Применяем фильтры
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if search_query:
        # Используем func.lower() для приведения имени продукта к нижнему регистру
        query = query.filter(func.lower(Product.name).like(f'%{search_query}%'))

    # Получаем отфильтрованные продукты
    products = query.all()
    
    # Получаем все категории для фильтра
    categories = Category.query.all()

    return render_template('products/list.html',
                         products=products,
                         categories=categories,
                         selected_category=category_id,
                         search_query=search_query)

@app.route('/products/add', methods=['GET', 'POST'])
@seller_or_admin_required
def product_add():
    """Добавление нового продукта"""
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            count=form.count.data,
            seller_id=current_user.id,
            category_id=form.category_id.data
        )
        if form.image.data:
            # Здесь должна быть логика сохранения изображения
            pass
        db.session.add(product)
        db.session.commit()
        flash('Продукт добавлен!', 'success')
        return redirect(url_for('products_list'))
    return render_template('products/add.html', form=form)

@app.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def product_edit(id):
    """Редактирование продукта"""
    product = Product.query.get_or_404(id)
    if current_user.id != product.seller_id and current_user.role != 'admin':
        flash('Доступ запрещен!', 'danger')
        return redirect(url_for('products_list'))
    
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.count = form.count.data
        product.category_id = form.category_id.data
        if form.image.data:
            product.image = form.image.data
        db.session.commit()
        flash('Продукт обновлен!', 'success')
        return redirect(url_for('products_list'))
    return render_template('products/edit.html', form=form, product=product)

@app.route('/products/<int:id>/delete')
@login_required
def product_delete(id):
    """Удаление продукта"""
    product = Product.query.get_or_404(id)
    if current_user.id != product.seller_id and current_user.role != 'admin':
        flash('Доступ запрещен!', 'danger')
        return redirect(url_for('products_list'))
    
    db.session.delete(product)
    db.session.commit()
    flash('Продукт удален!', 'success')
    return redirect(url_for('products_list'))

# --------- Управление заказами ---------

@app.route('/orders')
@login_required
def orders_list():
    """Список заказов"""
    if current_user.role == 'admin':
        # Админ видит все заказы
        orders = Orders.query.all()
    elif current_user.role == 'seller':
        # Продавец видит заказы своих товаров
        orders = Orders.query.join(Product).filter(Product.seller_id == current_user.id).all()
    else:
        # Обычный пользователь видит только свои заказы
        orders = Orders.query.filter_by(user_id=current_user.id).all()
    return render_template('orders/list.html', orders=orders)

@app.route('/order/add', methods=['GET', 'POST'])
@login_required
def order_add():
    """Создание нового заказа"""
    form = OrderForm()
    if form.validate_on_submit():
        product = Product.query.get(form.product_id.data)
        if product and product.count >= form.quantity.data:
            order = Orders(
                user_id=current_user.id,
                product_id=form.product_id.data,
                quantity=form.quantity.data,
                status='pending'
            )
            # Вычисляем total_price при создании заказа
            order.total_price = product.price * form.quantity.data
            
            # Уменьшаем количество доступного товара
            product.count -= form.quantity.data
            
            db.session.add(order)
            db.session.commit()
            
            flash('Заказ создан!', 'success')
            return redirect(url_for('orders_list'))
        else:
            flash('Недостаточно товара на складе!', 'danger')
    return render_template('orders/add.html', form=form)

@app.route('/orders/<int:id>/status', methods=['POST'])
@seller_or_admin_required
def update_order_status(id):
    """Обновление статуса заказа"""
    order = Orders.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status in ['new', 'processing', 'completed', 'cancelled']:
        order.status = new_status
        db.session.commit()
        flash('Статус заказа обновлен!', 'success')
    return redirect(url_for('orders_list'))

# --------- Управление отзывами ---------

@app.route('/reviews')
def reviews_list():
    """Список всех отзывов"""
    reviews = Reviews.query.all()
    return render_template('reviews/list.html', reviews=reviews)

@app.route('/reviews/add/<int:product_id>', methods=['GET', 'POST'])
@login_required
def review_add(product_id):
    """Добавление отзыва к продукту"""
    form = ReviewForm()
    if form.validate_on_submit():
        review = Reviews(
            product_id=product_id,
            user_id=current_user.id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        flash('Отзыв добавлен!', 'success')
        return redirect(url_for('products_list'))
    return render_template('reviews/add.html', form=form)

# --------- Управление категориями ---------

@app.route('/categories')
def categories_list():
    """Список всех категорий"""
    categories = Category.query.all()
    return render_template('categories/list.html', categories=categories)

@app.route('/categories/add', methods=['GET', 'POST'])
@login_required
def category_add():
    """Добавление новой категории"""
    if current_user.role not in ['admin', 'seller']:  # Разрешаем доступ и продавцам
        flash('Доступ запрещен!', 'danger')
        return redirect(url_for('index'))
    
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(category)
        db.session.commit()
        flash('Категория добавлена!', 'success')
        return redirect(url_for('categories_list'))
    return render_template('categories/add.html', form=form)

@app.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def category_edit(id):
    """Редактирование категории"""
    if current_user.role not in ['admin', 'seller']:  # Разрешаем доступ и продавцам
        flash('Доступ запрещен!', 'danger')
        return redirect(url_for('categories_list'))
    
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash('Категория обновлена!', 'success')
        return redirect(url_for('categories_list'))
    return render_template('categories/edit.html', form=form, category=category)

@app.route('/categories/<int:id>/delete')
@login_required
def category_delete(id):
    """Удаление категории"""
    if current_user.role not in ['admin', 'seller']:  # Разрешаем доступ и продавцам
        flash('Доступ запрещен!', 'danger')
        return redirect(url_for('categories_list'))
    
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('Категория удалена!', 'success')
    return redirect(url_for('categories_list'))

# Маршруты для управления пользователями (только для админа)
@app.route('/users')
@role_required('admin')
def users_list():
    """Список всех пользователей"""
    users = User.query.all()
    return render_template('admin/users_list.html', users=users)

@app.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@role_required('admin')
def user_edit(id):
    """Редактирование пользователя"""
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.surname = request.form.get('surname')
        user.email = request.form.get('email')
        user.role = request.form.get('role')
        db.session.commit()
        flash('Пользователь обновлен!', 'success')
        return redirect(url_for('users_list'))
    return render_template('admin/user_edit.html', user=user)

# В конце файла изменим регистрацию blueprint
app.register_blueprint(admin_panel)

@app.route('/api/products/search')
def search_products():
    category_id = request.args.get('category', type=int)
    query = request.args.get('query', '').lower()  # Приводим запрос к нижнему регистру
    
    products_query = Product.query.filter(Product.count > 0)
    
    if category_id and category_id > 0:
        products_query = products_query.filter(Product.category_id == category_id)
    
    if query:
        # Используем func.lower() для нечувствительного к регистру поиска
        search_filter = func.lower(Product.name).like(f'%{query}%')
        products_query = products_query.filter(search_filter)
    
    products = products_query.all()
    
    return jsonify({
        'products': [
            {
                'id': p.id,
                'name': p.name,
                'price': p.price,
                'count': p.count
            } for p in products
        ]
    })

@app.route('/seller/stats')
@role_required('seller')
def seller_stats():
    period = request.args.get('period', 'week')
    
    # Определяем временной интервал
    now = datetime.now()
    if period == 'day':
        start_date = now - timedelta(days=1)
    elif period == 'week':
        start_date = now - timedelta(weeks=1)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    else:  # year
        start_date = now - timedelta(days=365)

    # Получаем заказы продавца
    orders = Order.query.join(Product).filter(
        Product.seller_id == current_user.id,
        Order.created_at >= start_date
    ).all()

    # Статистика продаж
    sales_data = []
    for order in orders:
        sales_data.append({
            'date': order.created_at.strftime('%Y-%m-%d'),
            'amount': float(order.total_price) if order.total_price else 0
        })
    
    df_sales = pd.DataFrame(sales_data)
    sales_chart = None
    if not df_sales.empty:
        df_sales = df_sales.groupby('date')['amount'].sum().reset_index()
        sales_chart = px.line(df_sales, x='date', y='amount', 
                            title='Динамика продаж',
                            labels={'date': 'Дата', 'amount': 'Сумма продаж (₽)'})
        sales_chart.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)',
                tickformat='%Y-%m-%d'
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)',
                tickformat=',.0f'
            ),
            showlegend=False,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        sales_chart.update_traces(
            line=dict(color='#4CAF50', width=2),
            mode='lines+markers',
            marker=dict(size=8, color='#4CAF50')
        )

    # Общая статистика
    stats = {
        'total_sales': sum(float(order.total_price) if order.total_price else 0 for order in orders),
        'orders_count': len(orders),
        'average_order': sum(float(order.total_price) if order.total_price else 0 for order in orders) / len(orders) if orders else 0
    }

    return render_template('seller/stats.html',
                         period=period,
                         stats=stats,
                         sales_chart=sales_chart.to_html(full_html=False, include_plotlyjs=True) if sales_chart else '',
                         products_chart='',  # Добавим позже
                         orders_status_chart='')  # Добавим позже



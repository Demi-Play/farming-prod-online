from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask_login import current_user
from flask import redirect, url_for
from application.db import User, Product, Category, Orders

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class UserAdminView(ModelView):
    column_list = ['id', 'name', 'surname', 'email', 'role', 'created_at']
    column_searchable_list = ['name', 'email']
    column_filters = ['role']
    form_columns = ['name', 'surname', 'email', 'role']
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

class OrderAdminView(ModelView):
    column_list = ['id', 'user_id', 'product_id', 'quantity', 'status', 'created_at']
    column_filters = ['status']
    form_columns = ['user_id', 'product_id', 'quantity', 'status']
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

class ProductAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

class CategoryAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

def init_admin(admin, db):
    """Инициализация админ-панели"""
    admin.index_view = MyAdminIndexView()
    admin.add_view(UserAdminView(User, db.session))
    admin.add_view(OrderAdminView(Orders, db.session))
    admin.add_view(ProductAdminView(Product, db.session))
    admin.add_view(CategoryAdminView(Category, db.session)) 
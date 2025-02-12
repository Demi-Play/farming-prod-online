from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model, UserMixin):
    # User's table
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=True)
    surname = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(150), nullable=True, unique=True)
    password_hash = db.Column(db.String(150), nullable=True)
    role = db.Column(db.String(100), default='user') # roles: user, seller, admin
    # logs:
    created_at = db.Column(db.DateTime, default=datetime.now())
    
    # password setter logic
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Product(db.Model):
    # Product's table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    category = db.relationship('Category', backref=db.backref('products', lazy=True))

class Orders(db.Model):
    # Orders table
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    product = db.relationship('Product', backref=db.backref('orders', lazy=True))
    total_price = db.Column(db.Float, nullable=False)

    def __init__(self, *args, **kwargs):
        super(Orders, self).__init__(*args, **kwargs)
        if self.product and self.quantity:
            self.total_price = self.product.price * self.quantity

class Reviews(db.Model):
    # Reviews table
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now())

class Category(db.Model):
    # Category table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

class ActivityLog(db.Model):
    """Модель для журнала действий"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # user, order, product
    description = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(45))  # IPv6 может быть длиннее IPv4
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи
    user = db.relationship('User', backref=db.backref('activities', lazy=True))

    def __repr__(self):
        return f'<ActivityLog {self.action_type}: {self.description}>'

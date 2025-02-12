from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from flask_admin import Admin
from application.db import bcrypt, db
from flask_migrate import Migrate


app = Flask(__name__, static_folder='../static', template_folder='../templates')
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farming.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация расширений
db.init_app(app)
bcrypt.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
admin = Admin(app, name='FarmMarket Admin', template_mode='bootstrap3')
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    from application.db import User
    return User.query.get(int(user_id))

# Команда для создания базы данных
@app.cli.command("create-db")
def create_db():
    with app.app_context():
        db.create_all()
    print("База данных создана!")

# Импорт views после инициализации всех объектов
from application.admin_views import init_admin
init_admin(admin, db)
from application.views import *

if __name__ == "__main__":
    app.run(debug=True)
    
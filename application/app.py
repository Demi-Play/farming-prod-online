from flask import Flask
from flask_login import LoginManager
from config import Config
from application.db import bcrypt, db
from flask_admin import Admin


app = Flask(__name__, static_folder='../static', template_folder='../templates')

app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from application.db import User
    return User.query.get(int(user_id))

# Команда для создания базы данных
@app.cli.command("create-db")
def create_db():
    db.create_all()
    print("База данных создана!")

from application.views import *
admin = Admin(app, name='Панель администратора', template_mode='bootstrap3')

if __name__ == "__main__":
    app.run(debug=True)
    
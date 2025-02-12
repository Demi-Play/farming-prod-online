from flask_migrate import Migrate
from application.app import app, db

migrate = Migrate(app, db) 
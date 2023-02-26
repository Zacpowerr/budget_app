from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# app configs
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app_db.db"
app.config["SECRET_KEY"] = "00b30e871be6cfe8103e10e21b4e649a"
db = SQLAlchemy(app)
bcrypt = Bcrypt()
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
default_category_id = 1
# END app configs

# app routes
from budget_app import routes

# END app routes

# resets db
with app.app_context():
    db.create_all()
# call migrations
from budget_app import migrations
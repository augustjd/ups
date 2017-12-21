# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from ups.storage import Storage


bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()
marshmallow = Marshmallow()
storage = Storage()

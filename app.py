from flask import Flask
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config, TestingConfig

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_name=None):
    app = Flask(__name__)

    if config_name =='testing':
        app.config.from_object('config.TestingConfig')
    else:
        app.config.from_object('config.Config')

    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
    app.config['JWT_TIMEZONE'] = 'UTC'

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from models import user, organisation
    from routes import auth, organisation

    app.register_blueprint(auth.app, url_prefix='/auth')
    app.register_blueprint(organisation.app, url_prefix='/api')

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

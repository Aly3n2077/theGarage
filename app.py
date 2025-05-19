import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the Base class
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///garagehub.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Handle database session errors gracefully
@app.teardown_request
def session_cleanup(exception=None):
    if exception:
        db.session.rollback()  # Rollback the session in case of an exception
    db.session.close()  # Close the session after each request

# Initialize database
with app.app_context():
    # Import models to ensure they are registered with SQLAlchemy
    from models import User, Vehicle, Booking, Service, VehicleMake, VehicleModel
    from models import WorkshopJob, JobNote, Part, PartUsed
    
    # Drop and recreate all tables (development only)
    # db.drop_all()
    db.create_all()
    
    # Create initial service types if they don't exist
    from utils import create_initial_data
    create_initial_data()

# Import and register routes
from routes import *

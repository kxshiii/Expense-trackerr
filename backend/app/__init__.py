from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .models import db

def create_app(config_name='default'):
    app = Flask(__name__)
    CORS(app)
    
    # Configuration
    if config_name == 'default':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense_tracker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change in production
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.transactions import transaction_bp
    from .routes.budget_goals import budget_bp
    from .routes.exports import export_bp
    from .routes.analytics import analytics_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(transaction_bp, url_prefix='/api/transactions')
    app.register_blueprint(budget_bp, url_prefix='/api/budget-goals')
    app.register_blueprint(export_bp, url_prefix='/api/exports')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
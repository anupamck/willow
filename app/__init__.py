from flask import Flask
from .routes.home import home_bp
from .routes.contacts import contacts_bp
from .routes.interactions import interactions_bp
from .routes.auth import auth_bp, User
from flask_cors import CORS
import os
from flask_login import LoginManager

# Create Flask app
app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=os.getenv('SECRET_KEY_TEST'),
)
app.register_blueprint(home_bp)
app.register_blueprint(contacts_bp)
app.register_blueprint(interactions_bp)
app.register_blueprint(auth_bp)
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user):
    return User.get(user)


# Start server
if __name__ == '__main__':
    app.run(debug=True)

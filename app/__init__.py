from flask import Flask
from .routes.home import home_bp
from .routes.contacts import contacts_bp
from .routes.interactions import interactions_bp
from .routes.login import login_bp
from flask_cors import CORS
import os

# Create Flask app
app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=os.getenv('SECRET_KEY_TEST'),
)
app.register_blueprint(home_bp)
app.register_blueprint(contacts_bp)
app.register_blueprint(interactions_bp)
app.register_blueprint(login_bp)
CORS(app)

# Start server
if __name__ == '__main__':
    app.run(debug=True)

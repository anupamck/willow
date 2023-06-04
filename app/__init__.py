from flask import Flask
from .routes.home import home_bp
from .routes.contacts import contacts_bp
from .routes.interactions import interactions_bp
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY='dev'
)
app.register_blueprint(home_bp)
app.register_blueprint(contacts_bp)
app.register_blueprint(interactions_bp)
CORS(app)

# Start server
if __name__ == '__main__':
    app.run(debug=True)

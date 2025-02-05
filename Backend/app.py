from flask import Flask
from flask_cors import CORS
from Auth.routes import auth_bp
from config import Config

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api')

@app.route('/')
def home():
    return "Flask app is running with Neo4j!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
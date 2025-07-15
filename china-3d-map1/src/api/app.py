from flask import Flask
from flask_cors import CORS
from .route_planning import route_bp

app = Flask(__name__)
CORS(app)

# 注册路线规划Blueprint
app.register_blueprint(route_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5173) 
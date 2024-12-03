from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect  # 추가
import os

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()  # 추가

def create_app():
    app = Flask(__name__)
    
    # 절대 경로 설정
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    dbpath = os.path.join(basedir, 'instance', 'app.db')
    
    # 설정
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{dbpath}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 데이터베이스 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)  # 추가
    
    # Blueprint 등록
    from app.routes import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/app2')
    
    # /app2 URL에 대한 리다이렉션 추가
    @app.route('/app2')
    @app.route('/app2/')
    def index():
        return redirect('/app2/experiments')

    return app
from flask import Flask, redirect
import os
from .extensions import db, migrate, csrf

def create_app():
    app = Flask(__name__)
    
    # 절대 경로 설정
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    dbpath = os.path.join(basedir, 'instance', 'app.db')
    
    # 기본 설정
    app.config['SECRET_KEY'] = 'your-secret-key'  # CSRF 보호를 위해 필요
    
    # 데이터베이스 설정
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{dbpath}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True  # SQL 쿼리 로깅 활성화
    
    # 확장 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Blueprint 등록
    from app.routes import bp
    app.register_blueprint(bp, url_prefix='/app2')
    
    # 전역 라우트 추가
    @app.route('/')
    def index():
        return redirect('/app2/experiments')
    
    return app
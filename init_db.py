from app import create_app, db

app = create_app()

with app.app_context():
    # 데이터베이스 테이블 생성
    db.create_all()
    print("Database tables created successfully!")
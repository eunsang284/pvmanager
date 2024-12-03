from app import db
from datetime import datetime
import pytz

def get_korea_time():
    korea_tz = pytz.timezone('Asia/Seoul')
    return datetime.now(korea_tz)

class PVDataset(db.Model):
    __tablename__ = 'pv_datasets'
    
    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, nullable=False)
    set_pv_name = db.Column(db.String(255), nullable=False)
    set_value = db.Column(db.Float)
    readback_pv_name = db.Column(db.String(255))
    state = db.Column(db.String(20), default='Pending')
    last_updated = db.Column(db.DateTime, default=get_korea_time)  # 한국 시간 사용
    HH = db.Column(db.Float)
    High = db.Column(db.Float)
    Low = db.Column(db.Float)
    LL = db.Column(db.Float)
    error_rate = db.Column(db.Float)
    mode = db.Column(db.Integer)
    distance = db.Column(db.Float)  # 거리 정보를 저장할 필드 추가

    def __repr__(self):
        return f'<PVDataset {self.set_pv_name}>'
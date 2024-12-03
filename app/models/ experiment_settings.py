from app import db
from datetime import datetime
import pytz

def get_korea_time():
    korea_tz = pytz.timezone('Asia/Seoul')
    return datetime.now(korea_tz)

class ExperimentSettings(db.Model):
    __tablename__ = 'experiment_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    
    # 새로운 속성들 추가
    source_mode = db.Column(db.String(2))  # S0-S9
    beam_mode = db.Column(db.String(2))    # B0-B9
    machine_mode = db.Column(db.String(2))  # M0-M9
    ion_type = db.Column(db.String(50))
    charge_state = db.Column(db.Integer)
    beam_energy = db.Column(db.Float)
    note = db.Column(db.Text)
    
    # 생성/수정 시간 추적
    created_at = db.Column(db.DateTime, default=get_korea_time)
    updated_at = db.Column(db.DateTime, default=get_korea_time, onupdate=get_korea_time)

    def __repr__(self):
        return f'<ExperimentSettings {self.id}>'
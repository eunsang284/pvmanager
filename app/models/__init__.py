from app import db
from datetime import datetime
import pytz

def get_korea_time():
    korea_tz = pytz.timezone('Asia/Seoul')
    return datetime.now(korea_tz)

class Experiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    
    # 새로운 속성들 추가
    source_mode = db.Column(db.String(2))  # S0-S9
    beam_mode = db.Column(db.String(2))    # B0-B9
    machine_mode = db.Column(db.String(2))  # M0-M9
    ion_type = db.Column(db.String(50))
    charge_state = db.Column(db.Integer)
    beam_energy = db.Column(db.Float)
    note = db.Column(db.Text)
    
    # 시간 필드 추가
    created_at = db.Column(db.DateTime, default=get_korea_time)
    updated_at = db.Column(db.DateTime, default=get_korea_time, onupdate=get_korea_time)
    
    # 기존 관계 유지
    pvs = db.relationship('PVDataset', backref='experiment', lazy=True)

    def __repr__(self):
        return f'<Experiment {self.id}: {self.description}>'


class PVDataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id'), nullable=False)
    set_pv_name = db.Column(db.String(100), nullable=False)
    set_value = db.Column(db.Float, nullable=False)
    readback_pv_name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    last_updated = db.Column(db.DateTime, nullable=True)
    HH = db.Column(db.Float)
    High = db.Column(db.Float)
    Low = db.Column(db.Float)
    LL = db.Column(db.Float)
    error_rate = db.Column(db.Float)
    mode = db.Column(db.Integer)

    def __repr__(self):
        return f'<PVDataset {self.set_pv_name}>'
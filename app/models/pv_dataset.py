from app.extensions import db
from datetime import datetime
import pytz

class PVDataset(db.Model):
    __tablename__ = 'pv_dataset'
    
    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id'), nullable=False)
    set_pv_name = db.Column(db.String(200), nullable=False)
    distance = db.Column(db.Float())
    set_value = db.Column(db.Float())
    readback_pv_name = db.Column(db.String(200))
    state = db.Column(db.String(50), default='Pending')
    last_updated = db.Column(db.DateTime)
    HH = db.Column(db.Float())
    High = db.Column(db.Float())
    Low = db.Column(db.Float())
    LL = db.Column(db.Float())
    error_rate = db.Column(db.Float())
    mode = db.Column(db.Integer())

    def __init__(self, **kwargs):
        super().__init__()
        
        self.state = 'Pending'
        self.last_updated = datetime.now(pytz.timezone('Asia/Seoul'))
        
        if 'experiment_id' in kwargs:
            self.experiment_id = kwargs['experiment_id']
        if 'set_pv_name' in kwargs:
            self.set_pv_name = kwargs['set_pv_name']
        if 'distance' in kwargs:
            self.distance = kwargs['distance']
        if 'set_value' in kwargs:
            self.set_value = kwargs['set_value']
        if 'readback_pv_name' in kwargs:
            self.readback_pv_name = kwargs['readback_pv_name']
        if 'HH' in kwargs:
            self.HH = kwargs['HH']
        if 'High' in kwargs:
            self.High = kwargs['High']
        if 'Low' in kwargs:
            self.Low = kwargs['Low']
        if 'LL' in kwargs:
            self.LL = kwargs['LL']
        if 'error_rate' in kwargs:
            self.error_rate = kwargs['error_rate']
        if 'mode' in kwargs:
            self.mode = kwargs['mode']

    def __repr__(self):
        return f'<PVDataset {self.set_pv_name}>'
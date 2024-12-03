from app import db

class Experiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    pvs = db.relationship('PVDataset', backref='experiment', lazy=True)

    def __repr__(self):
        return f'<Experiment {self.id}: {self.description}>'

class PVDataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id'), nullable=False)
    set_pv_name = db.Column(db.String(100), nullable=False)
    set_value = db.Column(db.Float)
    readback_pv_name = db.Column(db.String(100))
    error_rate = db.Column(db.Float)
    HH = db.Column(db.Float)
    High = db.Column(db.Float)
    Low = db.Column(db.Float)
    LL = db.Column(db.Float)
    mode = db.Column(db.Integer)
    state = db.Column(db.String(50))
    distance = db.Column(db.Float)  # distance 필드 추가
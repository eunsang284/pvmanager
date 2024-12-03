from app.extensions import db

class Experiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    source_mode = db.Column(db.String(50))
    beam_mode = db.Column(db.String(50))
    machine_mode = db.Column(db.String(50))
    ion_type = db.Column(db.String(50))
    charge_state = db.Column(db.Float)
    beam_energy = db.Column(db.Float)
    note = db.Column(db.Text)
    pass 
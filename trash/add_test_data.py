from app import create_app, db
from app.models import PVDataset, Experiment

app = create_app()
with app.app_context():
    # 실험 데이터 추가
    exp1 = Experiment(id=1, description="First experiment - Testing basic PV controls")
    exp2 = Experiment(id=2, description="Second experiment - Advanced PV settings")
    db.session.add(exp1)
    db.session.add(exp2)
    db.session.commit()

    # 기존 PV 데이터에 experiment_id 추가
    pv1 = PVDataset(
        experiment_id=1,  # 실험 1에 연결
        set_pv_name="TEST:PV1",
        set_value=1.0,
        readback_pv_name="TEST:PV1:RB",
        state="Active",
        HH=10.0,
        High=8.0,
        Low=0.0,
        LL=-1.0,
        mode=1
    )
    
    pv2 = PVDataset(
        experiment_id=2,  # 실험 2에 연결
        set_pv_name="TEST:PV2",
        set_value=2.0,
        readback_pv_name="TEST:PV2:RB",
        state="Active",
        HH=20.0,
        High=15.0,
        Low=0.0,
        LL=-2.0,
        mode=1
    )
    
    db.session.add(pv1)
    db.session.add(pv2)
    db.session.commit()
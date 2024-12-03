from flask import render_template, redirect, url_for, request, flash, jsonify,current_app
from app.routes import bp
from app.models import PVDataset, Experiment
from app import db
from datetime import datetime
import pytz
from epics import caget, caput
import redis
from sqlalchemy import text


# 전역 변수로 실험 상태 관리
running_experiment = None

# Redis 연결 설정
redis_client = redis.Redis(host='localhost', port=6379, db=0)

@bp.route('/')
@bp.route('/app2')
@bp.route('/app2/')
def index():
    return redirect(url_for('api.experiment_list'))

@bp.route('/experiments')
def experiment_list():
    experiments = Experiment.query.all()
    return render_template('experiment_list.html', experiments=experiments)

@bp.route('/experiment/<int:exp_id>')
def experiment_detail(exp_id):
    experiment = Experiment.query.get_or_404(exp_id)
    pv_data = PVDataset.query.filter_by(experiment_id=exp_id).all()
    
    # 모델의 모든 속성 출력
    print("\n=== Model Attributes ===")
    print(PVDataset.__table__.columns.keys())
    
    # 실제 데이터의 모든 속성 출력
    print("\n=== Data Attributes ===")
    for pv in pv_data:
        print(vars(pv))
        break
    
    return render_template('experiment_detail.html', 
                         experiment=experiment, 
                         pv_data=pv_data)


@bp.route('/experiments/<int:exp_id>/start', methods=['POST'])
def start_experiment(exp_id):
    try:
        # Redis에서 현재 실행 중인 실험 확인
        running_exp = redis_client.get('running_experiment')
        if running_exp is not None:
            running_exp = int(running_exp)
            if running_exp == exp_id:
                return jsonify({
                    'status': 'error',
                    'message': 'This experiment is already running'
                }), 400
            else:
                return jsonify({
                    'status': 'error',
                    'message': f'Experiment #{running_exp} is already running'
                }), 400

        experiment = Experiment.query.get_or_404(exp_id)
        
        # Redis에 실행 중인 실험 ID 저장
        redis_client.set('running_experiment', exp_id)
        
        # 실험 상태 업데이트
        experiment.state = 'Running'
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Experiment #{exp_id} started successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@bp.route('/experiments/<int:exp_id>/stop', methods=['POST'])
def stop_experiment(exp_id):
    try:
        # Redis에서 현재 실행 중인 실험 확인
        running_exp = redis_client.get('running_experiment')
        if running_exp is None or int(running_exp) != exp_id:
            return jsonify({
                'status': 'error',
                'message': 'This experiment is not currently running'
            }), 400

        experiment = Experiment.query.get_or_404(exp_id)
        
        # Redis에서 실험 상태 제거
        redis_client.delete('running_experiment')
        
        # 실험 상태 업데이트
        experiment.state = 'Stopped'
        
        # 해당 실험의 모든 PV 상태를 'Stopped'로 업데이트
        pvs = PVDataset.query.filter_by(experiment_id=exp_id).all()
        for pv in pvs:
            pv.state = 'Stopped'
            
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Experiment #{exp_id} stopped successfully'
        })
    except Exception as e:
        db.session.rollback()  # 오류 발생 시 롤백 추가
        return jsonify({'status': 'error', 'message': str(e)}), 400

@bp.route('/experiments/status', methods=['GET'])
def get_experiment_status():
    """현재 실행 중인 실험 상태 확인"""
    running_exp = redis_client.get('running_experiment')
    return jsonify({
        'running_experiment': int(running_exp) if running_exp is not None else None
    })
@bp.route('/experiments/<int:exp_id>/edit', methods=['GET', 'POST'])
def edit_experiment(exp_id):
    experiment = Experiment.query.get_or_404(exp_id)
    
    if request.method == 'POST':
        if request.is_json:
            # AJAX 요청 처리
            data = request.json
            field = data.get('field')
            value = data.get('value')
            
            if field and hasattr(experiment, field):
                if field in ['charge_state']:
                    value = int(value) if value else None
                elif field in ['beam_energy']:
                    value = float(value) if value else None
                
                setattr(experiment, field, value)
                db.session.commit()
                return jsonify({'status': 'success'})
            
            return jsonify({'status': 'error', 'message': 'Invalid field'}), 400
        else:
            # 기존 폼 제출 처리
            experiment.description = request.form.get('description')
            experiment.source_mode = request.form.get('source_mode')
            experiment.beam_mode = request.form.get('beam_mode')
            experiment.machine_mode = request.form.get('machine_mode')
            experiment.ion_type = request.form.get('ion_type')
            experiment.charge_state = request.form.get('charge_state')
            experiment.beam_energy = request.form.get('beam_energy')
            experiment.note = request.form.get('note')
            
            db.session.commit()
            return redirect(url_for('api.experiment_list'))
            
    return render_template('edit_experiment.html', experiment=experiment)

@bp.route('/add-experiment', methods=['GET', 'POST'])
def add_experiment():
    if request.method == 'POST':
        try:
            print("\n=== Adding New Experiment ===")
            print("Form data:", request.form)
            
            # description은 필수 필드
            description = request.form.get('description')
            if not description:
                raise ValueError("Description is required")

            # 데이터 타입 변환 추가
            charge_state = request.form.get('charge_state', '')
            beam_energy = request.form.get('beam_energy', '')
            
            # 숫자 필드 변환 시 빈 문자열 리
            charge_state_value = int(charge_state) if charge_state.strip() else None
            beam_energy_value = float(beam_energy) if beam_energy.strip() else None
            
            print(f"Converted values - charge_state: {charge_state_value}, beam_energy: {beam_energy_value}")
            
            experiment = Experiment(
                description=description,
                source_mode=request.form.get('source_mode'),
                beam_mode=request.form.get('beam_mode'),
                machine_mode=request.form.get('machine_mode'),
                ion_type=request.form.get('ion_type'),
                charge_state=charge_state_value,
                beam_energy=beam_energy_value,
                note=request.form.get('note')
            )
            
            print("Created experiment object:", experiment)
            db.session.add(experiment)
            db.session.commit()
            print("Successfully saved experiment")
            
            return redirect(url_for('api.experiment_list'))
            
        except Exception as e:
            print(f"Error adding experiment: {str(e)}")
            db.session.rollback()
            flash(str(e), 'error')
            return render_template('add_experiment.html'), 400
            
    return render_template('add_experiment.html')

@bp.route("/pv-list")
def pv_list():
    pv_data = PVDataset.query.all()
    return render_template("pv_list.html", pv_data=pv_data)
@bp.route('/api/update_pv/<int:pv_id>', methods=['POST'])
def update_pv_api(pv_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No JSON data received'
            }), 400

        pv = PVDataset.query.get_or_404(pv_id)
        
        field = data.get('field')
        value = data.get('value')
        
        if not field:
            return jsonify({
                'status': 'error',
                'message': 'Field name is required'
            }), 400
        
        # 허용된 필드 목록
        allowed_fields = ['set_pv_name', 'distance', 'set_value', 'readback_pv_name', 
                         'error_rate', 'HH', 'High', 'Low', 'LL', 'mode', 'state']
        
        if field not in allowed_fields:
            return jsonify({
                'status': 'error',
                'message': f'Invalid field: {field}'
            }), 400
        
        # 숫자 필드의 타입 변환
        numeric_fields = {
            'distance': float,
            'set_value': float,
            'error_rate': float,
            'HH': float,
            'High': float,
            'Low': float,
            'LL': float,
            'mode': int
        }
        
        try:
            if field in numeric_fields and value not in [None, '', '-']:
                value = numeric_fields[field](value)
            elif value == '' or value == '-':
                value = None
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': f'Invalid number format for {field}: {value}'
            }), 400
        
        # 값 업데이트
        setattr(pv, field, value)
        pv.last_updated = datetime.now(pytz.timezone('Asia/Seoul'))
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'PV updated successfully',
            'updated_value': value if value is not None else '-',
            'last_updated': pv.last_updated.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating PV: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to update PV: {str(e)}'
        }), 500
        
@bp.route('/update-multiple-pvs', methods=['POST'])
def update_multiple_pvs():
    try:
        print("\n=== Starting PV Update Process ===")
        changes = request.get_json()
        print(f"Received changes: {changes}")

        if db.session.is_active:
            db.session.rollback()

        for pv_id, fields in changes.items():
            print(f"\nProcessing PV ID: {pv_id}")
            
            # 명시적으로 UPDATE 쿼리 실행
            for field, value in fields.items():
                if field == 'distance':
                    try:
                        new_value = float(value) if value not in [None, '', '-'] else None
                        print(f"Setting distance to: {new_value}")
                        # 직접 UPDATE 쿼리 실행
                        db.session.execute(
                            text("UPDATE pv_dataset SET distance = :value WHERE id = :id"),
                            {"value": new_value, "id": int(pv_id)}
                        )
                        print(f"Executed UPDATE query for distance")
                    except (ValueError, TypeError) as e:
                        print(f"Error converting distance value: {e}")
                        continue

            # last_updated 업데이트
            db.session.execute(
                text("UPDATE pv_dataset SET last_updated = :now WHERE id = :id"),
                {"now": datetime.now(pytz.timezone('Asia/Seoul')), "id": int(pv_id)}
            )

        print("\nCommitting changes to database...")
        db.session.commit()

        # 저장 후 확인
        for pv_id, fields in changes.items():
            pv = db.session.query(PVDataset).get(int(pv_id))
            print(f"After commit - PV {pv_id} attributes: {vars(pv)}")

        return jsonify({
            'status': 'success',
            'message': 'Changes saved successfully'
        })

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@bp.route("/add-pv", methods=['POST'])
def add_pv():
    try:
        data = request.json
        print("Received PV data:", data)
        
        new_pv = PVDataset()
        new_pv.experiment_id = data.get('experiment_id')
        new_pv.set_pv_name = data.get('set_pv_name')
        new_pv.distance = float(data.get('distance')) if data.get('distance') not in [None, '', '-'] else None
        new_pv.set_value = float(data.get('set_value')) if data.get('set_value') not in [None, '', '-'] else None
        new_pv.readback_pv_name = data.get('readback_pv_name')
        new_pv.HH = float(data.get('HH')) if data.get('HH') not in [None, '', '-'] else None
        new_pv.High = float(data.get('High')) if data.get('High') not in [None, '', '-'] else None
        new_pv.Low = float(data.get('Low')) if data.get('Low') not in [None, '', '-'] else None
        new_pv.LL = float(data.get('LL')) if data.get('LL') not in [None, '', '-'] else None
        new_pv.error_rate = float(data.get('error_rate')) if data.get('error_rate') not in [None, '', '-'] else None
        new_pv.mode = int(data.get('mode')) if data.get('mode') not in [None, '', '-'] else None
        
        # 필수 필드 설정
        new_pv.state = 'Pending'  # 기본값 설정
        new_pv.last_updated = datetime.now(pytz.timezone('Asia/Seoul'))
        
        db.session.add(new_pv)
        db.session.commit()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error adding PV: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@bp.route('/experiments/<int:exp_id>/copy', methods=['POST'])
def copy_experiment(exp_id):
    try:
        original_exp = Experiment.query.get_or_404(exp_id)
        data = request.json
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_exp = Experiment(
            description=f"{data['description']}\n(Copied from Experiment #{original_exp.id} on {current_time})",
            source_mode=original_exp.source_mode,
            beam_mode=original_exp.beam_mode,
            machine_mode=original_exp.machine_mode,
            ion_type=original_exp.ion_type,
            charge_state=original_exp.charge_state,
            beam_energy=original_exp.beam_energy,
            note=original_exp.note
        )
        db.session.add(new_exp)
        db.session.flush()
        
        original_pvs = PVDataset.query.filter_by(experiment_id=exp_id).all()
        for pv in original_pvs:
            pv_data = {key: getattr(pv, key) for key in pv.__table__.columns.keys() if key != 'id'}
            pv_data['experiment_id'] = new_exp.id
            new_pv = PVDataset(**pv_data)
            db.session.add(new_pv)
        
        db.session.commit()
        return jsonify({
            'status': 'success',
            'redirect_url': url_for('api.experiment_detail', exp_id=new_exp.id)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400

@bp.route("/edit-pv/<int:id>", methods=['GET', 'POST'])
def edit_pv(id):
    pv = PVDataset.query.get_or_404(id)
    if request.method == 'POST':
        pv.experiment_id = request.form.get('experiment_id', type=int)
        pv.set_pv_name = request.form.get('set_pv_name')
        pv.set_value = request.form.get('set_value', type=float)
        pv.readback_pv_name = request.form.get('readback_pv_name')
        pv.HH = request.form.get('HH', type=float)
        pv.High = request.form.get('High', type=float)
        pv.Low = request.form.get('Low', type=float)
        pv.LL = request.form.get('LL', type=float)
        pv.error_rate = request.form.get('error_rate', type=float)
        pv.mode = request.form.get('mode', type=int)
        db.session.commit()
        return redirect(url_for('api.pv_list'))
    return render_template('edit_pv.html', pv=pv)

@bp.route("/delete-pv/<int:id>", methods=['POST'])
def delete_pv(id):
    try:
        pv = PVDataset.query.get_or_404(id)
        experiment_id = pv.experiment_id
        db.session.delete(pv)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'redirect_url': url_for('api.experiment_detail', exp_id=experiment_id)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400

@bp.route("/experiments/delete/<int:exp_id>", methods=['POST'])
def delete_experiment(exp_id):
    try:
        experiment = Experiment.query.get_or_404(exp_id)
        PVDataset.query.filter_by(experiment_id=exp_id).delete()
        db.session.delete(experiment)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400

@bp.route('/pv/set', methods=['POST'])
def set_pv_value():
    try:
        data = request.json
        pv_name = data['pv_name']
        value = float(data['value'])
        pv_id = data.get('pv_id')
        
        # EPICS PV에 값 설정
        success = caput(pv_name, value)
        if success is None:
            raise Exception(f"Failed to set value for PV: {pv_name}")
        
        # PV 상태 업데이트
        if pv_id:
            pv = PVDataset.query.get(pv_id)
            if pv:
                pv.last_updated = datetime.now(pytz.timezone('Asia/Seoul'))
                db.session.commit()
            
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@bp.route('/pv/check', methods=['POST'])
def check_pv_value():
    try:
        data = request.json
        pv_name = data['pv_name']
        expected_value = float(data['expected_value'])
        pv_id = data.get('pv_id')
        
        # EPICS PV 값 읽기
        current_value = caget(pv_name)
        if current_value is None:
            raise Exception(f"Failed to read value from PV: {pv_name}")
            
        # 값 비교 (작은 오차 허용)
        matches = abs(current_value - expected_value) < 0.0001
        
        # PV 상태 업데이트
        if pv_id:
            pv = PVDataset.query.get(pv_id)
            if pv:
                pv.state = 'OK' if matches else 'Error'
                pv.last_updated = datetime.now(pytz.timezone('Asia/Seoul'))
                db.session.commit()
            
        return jsonify({
            'status': 'success',
            'matches': matches,
            'current_value': current_value
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


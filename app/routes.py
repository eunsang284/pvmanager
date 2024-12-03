from flask import Blueprint, request, jsonify
from app.models.experiment import Experiment
from app.extensions.database import db

# Blueprint 정의
api = Blueprint('api', __name__)

@api.route('/app2/experiments/<int:exp_id>', methods=['DELETE'])
def delete_experiment(exp_id):
    try:
        experiment = Experiment.query.get_or_404(exp_id)
        
        # 실험과 관련된 데이터도 함께 삭제해야 할 수 있음
        # 예: experiment.delete_related_data()
        
        db.session.delete(experiment)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Experiment deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

# Blueprint를 app에 등록하는 부분은 __init__.py에 있어야 함 
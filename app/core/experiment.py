from typing import Dict, List, Optional
from app.models.pv_dataset import PVDataset
from epics import caget, caput

class ExperimentController:
    def __init__(self):
        self.active_experiments = set()

    def run_experiment(self, experiment_id: int, retry_count: int = 3) -> dict:
        """실험 실행"""
        if experiment_id in self.active_experiments:
            return {
                'success': False,
                'error': 'Experiment already running'
            }

        try:
            self.active_experiments.add(experiment_id)
            datasets = PVDataset.query.filter_by(experiment_id=experiment_id).all()
            results = []

            for dataset in datasets:
                # PV 값 설정 시도
                success, message = self.set_pv_value(dataset, retry_count)
                results.append({
                    'pv_name': dataset.set_pv_name,
                    'success': success,
                    'message': message
                })

            return {
                'success': True,
                'results': results
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            self.active_experiments.remove(experiment_id)

    def set_pv_value(self, dataset: PVDataset, retry_count: int = 3) -> tuple[bool, str]:
        """PV 값 설정 및 검증"""
        for attempt in range(retry_count):
            try:
                # PV 값 설정
                caput(dataset.set_pv_name, dataset.set_value, wait=True)
                
                # 리드백 값 확인
                readback_name = dataset.readback_pv_name or dataset.set_pv_name
                readback_value = caget(readback_name)
                
                # 값 검증
                is_valid, error_msg = self.validate_value(dataset, readback_value)
                
                if is_valid:
                    return True, "Success"
                
                if attempt == retry_count - 1:  # 마지막 시도
                    return False, f"Value validation failed: {error_msg}"
                
            except Exception as e:
                if attempt == retry_count - 1:
                    return False, f"Failed to set PV: {str(e)}"
                
        return False, "Maximum retry attempts reached"

    def validate_value(self, dataset: PVDataset, readback_value: float) -> tuple[bool, str]:
        """리드백 값 검증"""
        if dataset.mode == 0:  # NO_CHECK
            return True, ""
            
        if dataset.mode == 3:  # BOUNDARY
            if readback_value >= dataset.HH:
                return False, "Major High Error"
            if readback_value >= dataset.High:
                return False, "Minor High Error"
            if readback_value <= dataset.LL:
                return False, "Major Low Error"
            if readback_value <= dataset.Low:
                return False, "Minor Low Error"
            return True, ""
            
        if dataset.mode == 2:  # ERROR_RATE
            if dataset.set_value == 0:
                return True, ""  # 0으로 나누기 방지
            error = abs((readback_value - dataset.set_value) / dataset.set_value * 100)
            if error > dataset.error_rate:
                return False, f"Error Rate Exceeded: {error:.2f}%"
            return True, ""
            
        return True, ""  # 기본값
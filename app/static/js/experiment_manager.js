// window 객체에 직접 할당하여 중복 선언 방지
window.experimentManager = (function() {
    class ExperimentManager {
        constructor() {
            this.isRunning = false;
            this.monitoringInterval = null;
            this.experimentId = null;
        }

        init(experimentId) {
            this.experimentId = experimentId;
            this.setupEventListeners();
            this.checkExperimentStatus();
        }

        setupEventListeners() {
            document.getElementById('startExperimentBtn').addEventListener('click', () => this.startExperiment());
            document.getElementById('stopExperimentBtn').addEventListener('click', () => this.stopExperiment());
        }

        async checkExperimentStatus() {
            try {
                const response = await fetch('/app2/experiments/status');
                const data = await response.json();
                
                if (data.running_experiment === this.experimentId) {
                    this.isRunning = true;
                    this.updateUI(true);
                    this.startMonitoring();
                } else if (data.running_experiment !== null) {
                    document.getElementById('startExperimentBtn').disabled = true;
                    document.getElementById('experimentStatus').textContent = 
                        `Another experiment (#${data.running_experiment}) is currently running`;
                }
            } catch (error) {
                console.error('Error checking experiment status:', error);
            }
        }

        async startExperiment() {
            try {
                const response = await fetch(`/app2/experiments/${this.experimentId}/start`, {
                    method: 'POST'
                });
                const data = await response.json();

                if (response.ok) {
                    this.isRunning = true;
                    this.updateUI(true);
                    this.startMonitoring();
                    this.updateStatusHeader(`Experiment #${this.experimentId} is running`);
                } else {
                    alert(data.message || 'Failed to start experiment');
                }
            } catch (error) {
                console.error('Error starting experiment:', error);
                alert('Failed to start experiment');
            }
        }

        async stopExperiment() {
            try {
                const response = await fetch(`/app2/experiments/${this.experimentId}/stop`, {
                    method: 'POST'
                });
                const data = await response.json();

                if (response.ok) {
                    this.isRunning = false;
                    this.updateUI(false);
                    this.stopMonitoring();
                    this.updateStatusHeader('');
                } else {
                    alert(data.message || 'Failed to stop experiment');
                }
            } catch (error) {
                console.error('Error stopping experiment:', error);
                alert('Failed to stop experiment');
            }
        }

        updateUI(isRunning) {
            document.getElementById('startExperimentBtn').style.display = isRunning ? 'none' : 'block';
            document.getElementById('stopExperimentBtn').style.display = isRunning ? 'block' : 'none';
            document.getElementById('experimentStatus').textContent = 
                isRunning ? `Experiment #${this.experimentId} is running` : '';
        }

        updateStatusHeader(message) {
            const statusElement = document.getElementById('experiment-status');
            if (statusElement) {
                statusElement.textContent = message;
            }
        }

        startMonitoring() {
            if (this.monitoringInterval) return;

            this.monitoringInterval = setInterval(async () => {
                const pvRows = document.querySelectorAll('tr[data-pv-id]');
                
                for (const row of pvRows) {
                    const pvId = row.dataset.pvId;
                    const setPvName = row.querySelector('[data-field="set_pv_name"]').textContent;
                    const setValue = parseFloat(row.querySelector('[data-field="set_value"]').textContent);
                    const readbackPvName = row.querySelector('[data-field="readback_pv_name"]').textContent;

                    try {
                        // Set PV 값 설정
                        await this.setPVValue(setPvName, setValue, pvId);
                        
                        // Readback PV 값 확인
                        if (readbackPvName) {
                            await this.checkPVValue(readbackPvName, setValue, pvId, row);
                        }
                    } catch (error) {
                        console.error(`Error monitoring PV ${setPvName}:`, error);
                        row.querySelector('[data-field="error_state"]').textContent = 'Error';
                    }
                }
            }, 1000); // 1초마다 모니터링
        }

        stopMonitoring() {
            if (this.monitoringInterval) {
                clearInterval(this.monitoringInterval);
                this.monitoringInterval = null;
            }
        }

        async setPVValue(pvName, value, pvId) {
            const response = await fetch('/app2/pv/set', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ pv_name: pvName, value: value, pv_id: pvId })
            });
            
            if (!response.ok) {
                throw new Error('Failed to set PV value');
            }
        }

        async checkPVValue(pvName, expectedValue, pvId, row) {
            const response = await fetch('/app2/pv/check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    pv_name: pvName, 
                    expected_value: expectedValue,
                    pv_id: pvId 
                })
            });

            if (!response.ok) {
                throw new Error('Failed to check PV value');
            }

            const data = await response.json();
            
            // UI 업데이트
            row.querySelector('[data-field="rb_pv_value"]').textContent = data.current_value;
            row.querySelector('[data-field="error_state"]').textContent = 
                data.matches ? 'OK' : 'Error';
        }
    }

    return new ExperimentManager();
})();
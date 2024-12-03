// ExperimentManager 코드 위에 PVManager 추가
const PVManager = {
    changedCells: new Set(),

    makeEditable(cell) {
        if (ExperimentManager.isRunning) {
            return;
        }

        if (cell.querySelector('input')) {
            return;
        }

        const value = cell.textContent.trim();
        const field = cell.dataset.field;
        
        const input = document.createElement('input');
        input.className = 'edit-input';
        input.value = value === '-' ? '' : value;
        input.type = field.includes('value') || field.includes('HH') || 
                     field.includes('High') || field.includes('Low') || 
                     field.includes('LL') || field.includes('mode') || 
                     field.includes('error_rate') ? 'number' : 'text';
        
        if (input.type === 'number') {
            input.step = 'any';
        }

        const finishEditing = (newValue) => {
            newValue = newValue.trim();
            if (newValue !== value) {
                cell.textContent = newValue || '-';
                cell.classList.add('modified');
                const pvId = cell.closest('tr').dataset.pvId;
                this.changedCells.add(`${pvId}-${field}`);
                document.querySelector('.save-all-button').style.display = 'inline-block';
            } else {
                cell.textContent = value;
            }
            cell.classList.remove('editing');
        };

        input.addEventListener('blur', () => finishEditing(input.value));
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                finishEditing(input.value);
            } else if (e.key === 'Escape') {
                cell.textContent = value;
                cell.classList.remove('editing');
            }
        });

        cell.textContent = '';
        cell.classList.add('editing');
        cell.appendChild(input);
        input.focus();
    },

    async saveAllChanges() {
        if (ExperimentManager.isRunning) {
            Utils.showNotification('Cannot save changes while experiment is running', 'error');
            return;
        }

        const changes = {};
        document.querySelectorAll('.modified').forEach(cell => {
            const pvId = cell.closest('tr').dataset.pvId;
            const field = cell.dataset.field;
            let value = cell.textContent.trim();

            if (field.includes('value') || field.includes('HH') || 
                field.includes('High') || field.includes('Low') || 
                field.includes('LL') || field.includes('mode') || 
                field.includes('error_rate')) {
                value = value === '-' ? null : parseFloat(value);
            }

            if (!changes[pvId]) {
                changes[pvId] = {};
            }
            changes[pvId][field] = value;
        });

        if (Object.keys(changes).length === 0) {
            Utils.showNotification('No changes to save', 'info');
            return;
        }

        try {
            const response = await fetch('/app2/update-multiple-pvs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify(changes)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || `Server returned ${response.status}`);
            }

            document.querySelectorAll('.modified').forEach(cell => {
                cell.classList.remove('modified');
            });
            this.changedCells.clear();
            document.querySelector('.save-all-button').style.display = 'none';
            Utils.showNotification('Changes saved successfully!', 'success');

        } catch (error) {
            console.error('Error saving changes:', error);
            Utils.showNotification(`Error saving changes: ${error.message}`, 'error');
        }
    }
};

// 기존 ExperimentManager 코드...
const ExperimentManager = {
    isRunning: false,
    monitoringInterval: null,
    experimentId: null,

    init(experimentId) {
        this.experimentId = experimentId;
        this.setupEventListeners();
        this.checkExperimentStatus();
    },

    setupEventListeners() {
        // 시작/중지 버튼 이벤트 리스너
        document.getElementById('startExperimentBtn').addEventListener('click', () => this.startExperiment());
        document.getElementById('stopExperimentBtn').addEventListener('click', () => this.stopExperiment());
    },

    async checkExperimentStatus() {
        try {
            const response = await fetch('/app2/experiments/status');
            const data = await response.json();
            
            if (data.running_experiment === this.experimentId) {
                this.isRunning = true;
                this.updateUI(true);
                this.startMonitoring();
            } else if (data.running_experiment !== null) {
                // 다른 실험이 실행 중
                document.getElementById('startExperimentBtn').disabled = true;
                document.getElementById('experimentStatus').textContent = 
                    `Another experiment (#${data.running_experiment}) is currently running`;
            }
        } catch (error) {
            console.error('Error checking experiment status:', error);
        }
    },

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
    },

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
    },

    updateUI(isRunning) {
        document.getElementById('startExperimentBtn').style.display = isRunning ? 'none' : 'block';
        document.getElementById('stopExperimentBtn').style.display = isRunning ? 'block' : 'none';
        document.getElementById('experimentStatus').textContent = 
            isRunning ? `Experiment #${this.experimentId} is running` : '';
    },

    updateStatusHeader(message) {
        const statusElement = document.getElementById('experiment-status');
        if (statusElement) {
            statusElement.textContent = message;
        }
    },

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
    },

    stopMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }
    },

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
    },

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
};
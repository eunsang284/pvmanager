window.PVManager = (function() {
    return {
        changedCells: new Set(),

        makeEditable(cell) {
            if (window.experimentManager && window.experimentManager.isRunning) {
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
                         field.includes('error_rate') || field.includes('distance') ? 'number' : 'text';
            
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
            console.log('Starting saveAllChanges...');
            
            const changes = {};
            document.querySelectorAll('.modified').forEach(cell => {
                const pvId = cell.closest('tr').dataset.pvId;
                const field = cell.dataset.field;
                let value = cell.textContent.trim();

                console.log('Modified cell:', { pvId, field, value });

                if (field.includes('value') || field.includes('HH') || 
                    field.includes('High') || field.includes('Low') || 
                    field.includes('LL') || field.includes('mode') || 
                    field.includes('error_rate') || field.includes('distance')) {
                    value = value === '-' ? null : parseFloat(value);
                }

                if (!changes[pvId]) {
                    changes[pvId] = {};
                }
                changes[pvId][field] = value;
            });

            console.log('Changes to be sent:', changes);

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

                console.log('Response status:', response.status);
                const data = await response.json();
                console.log('Response data:', data);

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
        },

        deletePV(pvId) {
            if (confirm('Are you sure you want to delete this PV?')) {
                const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
                
                fetch(`/app2/delete-pv/${pvId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    credentials: 'same-origin'
                })
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        throw new Error(data.message || 'Failed to delete PV');
                    }
                    return data;
                })
                .then(data => {
                    if (data.status === 'success') {
                        window.location.reload();
                    } else {
                        throw new Error(data.message || 'Failed to delete PV');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert(error.message);
                });
            }
        }
    };
})(); 
async function loadDpeartments() {
    try {
        const departments_response = await fetch('/departments/all');
        const departments = await departments_response.json();
        
        const selectElement = document.getElementById('dpeartment');
        departments.forEach(department => {
            const option = document.createElement('option');
            option.value = department.id;
            option.textContent = department.name;
            selectElement.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading departments:', error);
    }
}

async function deletePatient(patientId) {
    if (confirm('האם למחוק מטופל זה?')) {
        try {
            const response = await fetch(`/patients/${patientId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            if (response.status === 204) {
                window.location.reload();
            } else {
                const error = await response.json();
                alert(error.detail || 'שגיאה במחיקת מטופל');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('אירעה שגיאה במחיקת מטופל');
        }
    }
  }

  document.getElementById('newpatientform').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('patient_name').value,
        department_id: document.getElementById('dpeartment').value,
    };
    
    try {
        const response = await fetch('/patients', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            window.location.href = window.location.pathname;
        } else {
            const error = await response.json();
            alert(`שגיאה: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error submitting form:', error);
        alert('אירעה שגיאה בשליחת הטופס');
    }
  });

  async function updateReleaseDate(patientId, patientName, departmentId) {
    const formData = {
        id: patientId,
        name: patientName,
        department_id: departmentId, 
        release_date: document.getElementById(`release_date-${patientId}`).value,
    };

        try {
            const response = await fetch(`/patients/${patientId}`, {
                method: 'PUT',
                body: JSON.stringify(formData),
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            
           
            window.location.reload();
            
        } catch (error) {
            console.error('Error:', error);
            alert('אירעה שגיאה בעדכון');
        }
    
  }

  document.addEventListener('DOMContentLoaded', loadDpeartments);
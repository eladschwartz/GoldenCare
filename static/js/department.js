
async function deleteDepartment(departmentId) {
    if (confirm('האם למחוק מחלקה זו?')) {
        try {
            const response = await fetch(`/departments/${departmentId}`, {
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

  document.getElementById('newdepartmentform').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('department_name').value,
    };
    
    try {
        const response = await fetch('/departments', {
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
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

document.getElementById('therapistForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('therapist').value,
        password: document.getElementById('password').value,
        email: document.getElementById('email').value,
        department_id: document.getElementById('dpeartment').value
    };
    
    try {
        const response = await fetch('/users', {
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


async function deleteUser(userId) {
    if (confirm('האם אתה בטוח שברצונך למחוק משתמש זה?')) {
        try {
            const response = await fetch(`/users/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            if (response.status === 204) {
                window.location.reload();
            } else {
                const error = await response.json();
                alert(error.detail || 'שגיאה במחיקת המשתמש');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('אירעה שגיאה במחיקת המשתמש');
        }
    }
}

async function updatePassword(userId) {
    const data = {
        user_id: userId,
        new_password: document.getElementById("update-password").value
    }

        try {
            const response = await fetch(`/users/password`, {
                method: 'PUT',
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data)
            });
            
            if (response.status === 204) {
                
            } else {
                const error = await response.json();
                alert(error.detail || 'שגיאה  ');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('אירעה שגיאה  המשתמש');
        }
}


document.addEventListener('DOMContentLoaded', loadDpeartments);

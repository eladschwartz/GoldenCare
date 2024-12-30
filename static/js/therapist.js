
var patients = [];


async function loadPatients() {
    try {
        const date = document.getElementById('main-date-selected').value
        const patients_response = await fetch(`/patients/all?date=${date}`);
      
        patients = await patients_response.json();
        
        const selectElement = document.getElementById('patient');
        patients.forEach(patient =>{
            const option = document.createElement('option');
            option.value = patient.id;
            option.textContent = patient.name;
            selectElement.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading patients:', error);
    }
  }
  
  document.getElementById('newtreatmentform').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const date = new Date(document.getElementById('main-date-selected').value)
    const time = document.getElementById('time-picker').value
    const [hours, minutes] = time.split(":").map(Number);

    date.setHours(hours);
    date.setMinutes(minutes);

    const formData = {
        patient_id: document.getElementById('patient').value,
        therapist_id: document.getElementById('form_therapist_id').value,
        timestamp: date
    };
    
    try {
        const response = await fetch('/treatments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            window.location.href = window.location.href;
        } else {
            const error = await response.json();
            alert(`שגיאה: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error submitting form:', error);
        alert('אירעה שגיאה בשליחת הטופס');
    }
  });
  
  function openEditModal(treatmentId, patientId, date, time) {
    let dateTimeStr = `${date}T${time}`;
    let [datePart, timePart] = dateTimeStr.split("T");
    let [day, month, year] = datePart.split("/");
    let formattedDatePart = `${year}-${month}-${day}`;
    let formattedDateTime = `${formattedDatePart}T${timePart}`;   
    document.getElementById('edit-treatment-date').value = formattedDateTime;
  
    document.getElementById('treatmentId').value = treatmentId;

    
    const selectElement = document.getElementById('patientSelect');
    patients.forEach(patient =>{
        const option = document.createElement('option');
        option.value = patient.id;
        option.textContent = patient.name;
        selectElement.appendChild(option);
    });

    document.getElementById('patientSelect').value = patientId;
    new bootstrap.Modal(document.getElementById('editModal')).show();
  }
  
  async function saveEditModalChanges() {
    treatment_id = document.getElementById('treatmentId').value;
    const formData = {
        id: treatment_id,
        patient_id: document.getElementById('patientSelect').value,
        therapist_id: getUserId(),
        timestamp: document.getElementById('edit-treatment-date').value
    };

    try {
        const response = await fetch(`/treatments/${treatment_id}`, {
            method: 'Put',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
  
        if (response.ok) {
            window.location.reload();
        } else {
            alert('Error updating appointment');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error updating appointment');
    }
  }
  
  function closeEditModal() {
    // Remove the modal
    const modalElement = document.getElementById('editModal');
    const modal = bootstrap.Modal.getInstance(modalElement);
    modal.hide();
    
    // Remove the backdrop
    const backdrop = document.querySelector('.modal-backdrop');
    if (backdrop) {
        backdrop.remove();
    }
    
    // Remove modal-open class from body
    document.body.classList.remove('modal-open');
  }
  
  async function deleteTreatment(treatmentId) {
    if (confirm('האם למחוק טיפול זה?')) {
        try {
            const response = await fetch(`/treatments/${treatmentId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            if (response.status === 204) {
                window.location.reload();
            } else {
                const error = await response.json();
                alert(error.detail || 'שגיאה במחיקת הטיפול');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('אירעה שגיאה במחיקת הטיפול');
        }
    }
  }

  function getUserId(){
    // Get the current path
    let path = window.location.pathname;
    console.log(path)
    // Split the path by "/"
    let segments = path.split("/");
    console.log(segments);
    console.log(segments[segments.length - 1]);
    // Get the user ID (assumes it's the last segment)
    let userId = segments[segments.length - 1];

    return userId
  }
  
  function changeDate(direction) {
    // Get the current date from the input field
    let currentDate = new Date(document.getElementById('main-date-selected').value);
    
    // Modify the date by adding or subtracting one day based on the direction
    currentDate.setDate(currentDate.getDate() + direction);
    
    // Update the input field with the new date
  
    window.location.href = window.location.pathname + '?selected_date=' + currentDate.toISOString().split('T')[0];
  }
  
  function openEditForm(scheduleId, therapistId) {
    const url = `/treatments/${scheduleId}/${therapistId}`;
  
    fetch(url)
    .then(response => response.text())
    .then(data => {
        document.getElementById('editModalContainer').innerHTML = data;
  
        var modalElement = document.getElementById('editModal');
        if (modalElement) {
        var editModal = new bootstrap.Modal(modalElement)
  
        editModal.show();
      } else {
        console.error("modal element not found")
      }
  
        // Add an event listener to hide the modal correctly when closed
        modalElement.addEventListener('hidden.bs.modal', function () {
            // Remove the modal content after it is hidden to prevent it from persisting
            document.getElementById('editModalContainer').innerHTML = '';
        });
    })
    .catch(error => console.error('Error loading modal:', error))
  }
  

  async function copyTreatments(therapistId, fromDate){
    const to_date = document.getElementById('copy-date-selected').value

    const formData = {
        therapist_id: therapistId,
        from_date: fromDate,
        to_date: to_date
    };
    
    try {
        const response = await fetch('/treatments/copy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            window.location.href = window.location.href;
        } else {
            const error = await response.json();
            alert(`שגיאה: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error submitting form:', error);
        alert('אירעה שגיאה בשליחת הטופס');
    }
  }
  
  document.addEventListener('DOMContentLoaded', function() {
    loadPatients();
  });
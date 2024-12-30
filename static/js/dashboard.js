// Add Authorization header to all fetch requests
function addAuthHeader(url, options = {}) {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }
    
    return fetch(url, {
        ...options,
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
}

// Check token on page load
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
    }
});

function changeDate(direction) {
  // Get the current date from the input field
  let currentDate = new Date(document.getElementById('date').value);
  
  // Modify the date by adding or subtracting one day based on the direction
  currentDate.setDate(currentDate.getDate() + direction);
  
  // Update the input field with the new date

  window.location.href = window.location.pathname + '?selected_date=' + currentDate.toISOString().split('T')[0];
}


function getTableData() {
    const table = document.getElementById('dataTable');
    const headers = Array.from(table.querySelectorAll('thead th'))
        .map(th => th.textContent.trim());
    
    const rows = Array.from(table.querySelectorAll('tbody tr'))
        .map(row => {
            // Convert each row's cells to an array of values
            const cellValues = Array.from(row.querySelectorAll('td')).map(cell => {
                const content = cell.textContent.trim();
                // Ensure each cell value is treated as a string
                return content || "";
            });
            // Ensure each row is an array, even if it's a single value
            return cellValues;
        })
        // Filter out completely empty rows
        .filter(row => row.some(cell => cell !== ""));
    
    // Filter out empty rows
    const filteredRows = rows.filter(row => row.length > 0);
    
    return { 
        headers: headers,
        rows: filteredRows
    };
}


async function exportToExcel() {
    const excelBtn = document.getElementById('excelBtn');
    excelBtn.disabled = true;
    excelBtn.textContent = 'מייצא...';

    try {
        const tableData = getTableData();
        const response = await fetch('/export/excel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(tableData)
        });

        if (!response.ok) throw new Error('Export failed');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'table_data.xlsx';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error exporting to Excel:', error);
        alert('Failed to export to Excel');
    } finally {
        excelBtn.disabled = false;
        excelBtn.textContent = 'ייצא לאקסל';
    }
}
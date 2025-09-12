// Layer & Generic CRUD functionality
// This file contains all JavaScript functionality for the home page

let currentData = [];
let table2Options = [];
let table3Options = [];
let currentTable = null;
let currentMode = 'layers';

function toggleDropdown() {
    document.getElementById("tableDropdown").classList.toggle("show");
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById("tableDropdown");
    
    // If the click was not within the dropdown, close it
    if (!dropdown.contains(event.target)) {
        dropdown.classList.remove("show");
    }
});

// Function to get CRUD service URL based on table and mode
function getCrudUrl(table) {
    if (currentMode === 'generic') {
        return `/layer_and_generic/api/generic/${table}/`;
    } else {
        return `/layer_and_generic/api/${table}/`;
    }
}

// Function that executes when user selects a table (layers)
function showTable(table) {
    currentMode = 'layers';
    document.getElementById('current_table').innerText = table.replace('table', 'Table ');
    document.getElementById("tableDropdown").classList.remove("show");
    currentTable = table;
    
    loadTableData();
}

// Function that executes when "CRUD with Generic Views" is pressed
function showGenericTable() {
    console.log('showGenericTable() called - switching to Generic mode');
    currentMode = 'generic';
    currentTable = 'table1';
    document.getElementById('current_table').innerText = 'Table 1';
    
    loadTableData();
}

// Function to load table data
function loadTableData() {
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch(getCrudUrl(currentTable), {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        currentData = data.data || [];
        if (currentTable === 'table1') {
            table2Options = data.table2_options || [];
            table3Options = data.table3_options || [];
        }
        renderTable();
    })
    .catch(error => {
        console.error('Error:', error);
        // Show error message to user
        document.getElementById('tableDiv').innerHTML = `
            <span class="tablediv_title">Error loading ${currentTable.replace('table', 'Table ')}</span><br>
            <span style="color: red;">Error: ${error.message}</span>
        `;
    });
}

// Function to render table with current data
function renderTable() {
    let info = document.querySelector(".info");
    if (info) {
        info.remove();
    }
    
    // Determine header text based on mode
    const modeText = currentMode === 'generic' ? 'Generic' : 'Layers';
    const tableNumber = currentTable.replace('table', '');
    const headerText = `${modeText} - Table ${tableNumber}`;
    
    if (!currentData.length) {
        let html_no = `<span class="tablediv_title">${headerText}</span>`;
        html_no += `<br>`;
        html_no += `<span class="tablediv_title">No entries found :( (Create your first entry)</span>`;
        html_no += `<br>`;
        html_no += `<button class="tablediv_button" onclick="openCrudModal('create')">Add New Entry +</button>`;
        document.getElementById('tableDiv').innerHTML = html_no;
        return;
    }
    
    let fields = Object.keys(currentData[0]).filter(f => f !== 'id');
    let html = `<span class="tablediv_title">${headerText}</span>`;
    html += `<br>`;
    html += `<button class="tablediv_button" onclick="openCrudModal('create')">Add New Entry +</button>`;
    html += `<table class="crud-table"><thead><tr>`;
    html += `<th>ID</th>`;
    fields.forEach(f => html += `<th>${formatHeader(f)}</th>`);
    html += `<th>Actions</th></tr></thead><tbody>`;
    
    currentData.forEach(row => {
        html += `<tr>`;
        html += `<td>${row.id}</td>`;
        fields.forEach(f => html += `<td>${formatCell(f, row[f])}</td>`);
        html += `<td>
            <button class="edit_button" onclick="openCrudModal('edit', ${row.id})"><i class="bi bi-pencil-square"></i> Edit</button>
            <button class="delete_button" onclick="deleteEntry(${row.id})"><i class="bi bi-trash-fill"></i> Delete</button>
        </td>`;
        html += `</tr>`;
    });
    html += `</tbody></table>`;
    document.getElementById('tableDiv').innerHTML = html;
}

function formatHeader(field) {
    // Capitalize and add spaces for better readability
    return field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatCell(field, value) {
    // Table1 specific fields
    if (field === 'image_field') {
        if (value) {
            return `<img src="${value}" alt="img" style="max-width: 100px; max-height: 100px;">`;
        } else {
            return '-';
        }
    }
    if (field === 'file_field') {
        if (value) {
            return `<a href="${value}" download>Download</a>`;
        } else {
            return '-';
        }
    }
    if (field === 'boolean_field') {
        return value ? 'True' : 'False';
    }
    
    // Date and time fields
    if (field === 'date_field' && value) {
        return new Date(value).toLocaleDateString();
    }
    if (field === 'time_field' && value) {
        return value;
    }
    if (field === 'datetime_field' && value) {
        return new Date(value).toLocaleString();
    }
    
    if (field === 'duration_field' && value) {
        return value; // Show as it comes from backend
    }

    // Relationships
    if ((field === 'foreign_key' || field === 'one_to_one') && value) {
        if (typeof value === 'object' && value.positive_small_int !== undefined) {
            return `Table2 id:${value.id} (${value.positive_small_int})`;
        }
        return `ID: ${value}`;
    }
    
    if (field === 'many_to_many') {
        if (Array.isArray(value) && value.length) {
            return value.map(item => 
                typeof item === 'object' ? 
                `Table3 id:${item.id} (${item.email_field})` : 
                `ID: ${item}`
            ).join(', ');
        }
        return '-';
    }

    // Show empty as dash
    if (value === null || value === undefined || value === '') {
        return '-';
    }
    
    return value;
}

function openCrudModal(mode, id=null) {
    document.getElementById('grey_background').style.display = 'block';
    document.getElementById('crudTable').value = currentTable;
    document.getElementById('crudId').value = id || '';
    document.getElementById('crudModal').style.display = 'block';
    document.getElementById('crudTitle').innerText = mode === 'create' ? 'Create Entry' : 'Edit Entry';
    document.getElementById('crudSubmitBtn').innerHTML = mode === 'create' ? '<i class="bi bi-save"></i> Create' : '<i class="bi bi-pencil"></i> Update';
    
    let data = {};
    if (mode === 'edit' && id) {
        data = currentData.find(d => d.id == id) || {};
    }

    renderFormFields(data);
}

function renderFormFields(data = {}) {
    const fields = currentData.length ? Object.keys(currentData[0]).filter(f => f !== 'id') : [];
    const formFields = [];

    fields.forEach(field => {
        if (currentTable === 'table1') {
            switch(field) {
                case 'foreign_key':
                case 'one_to_one':
                    formFields.push(renderSelect(field, table2Options, data[field]?.id));
                    break;
                
                case 'many_to_many':
                    formFields.push(renderMultiSelect(field, table3Options, (data[field] || []).map(item => item.id)));
                    break;
                
                case 'image_field':
                case 'file_field':
                    formFields.push(renderFileInput(field, data[field]));
                    break;
                
                case 'boolean_field':
                    formFields.push(renderCheckbox(field, data[field]));
                    break;
                
                case 'date_field':
                    formFields.push(renderDateInput(field, data[field]));
                    break;
                
                case 'time_field':
                    formFields.push(renderTimeInput(field, data[field]));
                    break;
                
                case 'datetime_field':
                    formFields.push(renderDateTimeInput(field, data[field]));
                    break;
                
                default:
                    formFields.push(renderTextInput(field, data[field]));
            }
        } else if (currentTable === 'table2') {
            if (field === 'positive_small_int') {
                formFields.push(renderSelect(field, [
                    {id: 1, name: 'Option 1'}, 
                    {id: 2, name: 'Option 2'}
                ], data[field]));
            } else {
                formFields.push(renderTextInput(field, data[field]));
            }
        } else if (currentTable === 'table3') {
            if (field === 'duration_field') {
                formFields.push(renderDurationInput(field, data[field]));
            } else if (field === 'email_field') {
                formFields.push(renderEmailInput(field, data[field]));
            } else {
                formFields.push(renderTextInput(field, data[field]));
            }
        } else {
            formFields.push(renderTextInput(field, data[field]));
        }
    });
    
    document.getElementById('formFields').innerHTML = formFields.join('');
}

// Functions to render different field types
function renderSelect(field, options, selectedId) {
    let optionsHtml = '';
    if (field === 'positive_small_int') {
        optionsHtml = options.map(opt => `
            <option value="${opt.id}" ${selectedId === opt.id ? 'selected' : ''}>
                ${opt.name}
            </option>
        `).join('');
    } else {
        optionsHtml = options.map(opt => `
            <option value="${opt.id}" ${selectedId === opt.id ? 'selected' : ''}>
                ${opt.id} - Table2 (${opt.positive_small_int || 'N/A'})
            </option>
        `).join('');
    }
    
    return `
        <div class="form-row">
            <label class="label_field">${formatHeader(field)}:</label>
            <select class="input_field" name="${field}">
                <option value="">-- Select ${formatHeader(field)} --</option>
                ${optionsHtml}
            </select>
        </div>`;
}

function renderMultiSelect(field, options, selectedIds) {
    return `
        <div class="form-row">
            <label class="label_field">${formatHeader(field)}:</label>
            <select class="input_field" name="${field}" multiple size="3" style="height:auto;">
                ${options.map(opt => `
                    <option value="${opt.id}" ${selectedIds.includes(opt.id) ? 'selected' : ''}>
                        ${opt.id} - Table3 (${opt.email_field})
                    </option>
                `).join('')}
            </select>
        </div>`;
}

function renderFileInput(field, currentValue) {
    return `
        <div class="form-row">
            <label class="label_field">${formatHeader(field)}:</label>
            ${currentValue ? `<span style="display: block; margin-bottom: 5px;">Current: ${currentValue}</span>` : ''}
            <input class="input_field" type="file" name="${field}">
        </div>`;
}

function renderCheckbox(field, checked) {
    return `
        <div class="form-row">
            <label class="label_field">${formatHeader(field)}:</label>
            <input style="height:20px" class="input_field" type="checkbox" name="${field}" ${checked ? 'checked' : ''}>
        </div>`;
}

function renderDateInput(field, value) {
    return `
        <div class="form-row">
            <label class="label_field">${formatHeader(field)}:</label>
            <input class="input_field" type="date" name="${field}" value="${value ? value.split('T')[0] : ''}">
        </div>`;
}

function renderTimeInput(field, value) {
    return `
        <div class="form-row">
            <label class="label_field">${formatHeader(field)}:</label>
            <input class="input_field" type="time" name="${field}" value="${value || ''}">
        </div>`;
}

function renderDateTimeInput(field, value) {
    return `
        <div class="form-row">
            <label class="label_field">${formatHeader(field)}:</label>
            <input class="input_field" type="datetime-local" name="${field}" value="${value ? value.replace('Z', '') : ''}">
    </div>`;
}

function renderDurationInput(field, value) {
    return `
        <div class="form-row">
            <label class="label_field">${formatHeader(field)} (days:hours:minutes:seconds):</label>
            <input class="input_field" type="text" name="${field}" value="${value || ''}" placeholder="P1DT2H30M45S">
        </div>`;
}

function renderEmailInput(field, value) {
    return `
        <div class="form-row">
            <label class="label_field">${formatHeader(field)}:</label>
            <input class="input_field" type="email" name="${field}" value="${value || ''}" required>
        </div>`;
}

function renderTextInput(field, value) {
    return `
        <div class="form-row">
            <label class="label_field">${formatHeader(field)}:</label>
            <input class="input_field" name="${field}" value="${value || ''}">
        </div>`;
}

function submitCrud(e) {
    e.preventDefault();
    const form = document.getElementById('crudForm');
    const table = form.elements['crudTable'].value;
    const id = form.elements['crudId'].value;
    const method = id ? 'PUT' : 'POST';
    const url = getCrudUrl(table);

    // Prepare JSON data
    const jsonData = prepareFormData(form);
    
    if (method === 'PUT') {
        jsonData.id = parseInt(id);
    }

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(jsonData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        loadTableData();
        closeCrud();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error: ' + error.message);
    });
}

function prepareFormData(form) {
    const jsonData = {};
    
    // Iterate through form elements to build the JSON object
    for (const field of form.elements) {
        if (!field.name || field.name === 'crudTable' || field.name === 'crudId') continue;
        
        if (field.name === 'many_to_many' && field.multiple) {
            jsonData[field.name] = Array.from(field.selectedOptions).map(opt => ({
                id: parseInt(opt.value)
            }));
        } else if (field.name === 'foreign_key' || field.name === 'one_to_one') {
            jsonData[field.name] = field.value ? { id: parseInt(field.value) } : null;
        } else if (field.type === 'checkbox') {
            jsonData[field.name] = field.checked;
        } else if (field.type !== 'file') {
            jsonData[field.name] = field.value || null;
        }
    }

    return jsonData;
}

function deleteEntry(id) {
    if (!confirm('Are you sure you want to delete this entry?')) return;
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    let url = getCrudUrl(currentTable);
    
    fetch(url, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({id: id})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        loadTableData();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error deleting entry: ' + error.message);
    });
}

function closeCrud() {
    document.getElementById('grey_background').style.display = 'none';
    document.getElementById('crudModal').style.display = 'none';
    document.getElementById('crudForm').reset();
}